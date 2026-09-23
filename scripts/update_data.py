#!/usr/bin/env python3
"""Fetch the latest 20 trading days of 外資買賣超 from Wantgoo."""

from __future__ import annotations

import json
import ssl
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE_PAGE = (
    "https://www.wantgoo.com/stock/institutional-investors/three-trade-for-trading-amount"
)
DATA_PATH = "/stock/institutional-investors/three-trade-for-trading-amount-data?topdays=490"
DATA_URL = f"https://www.wantgoo.com{DATA_PATH}"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "foreign.json"
TAIPEI = timezone(timedelta(hours=8))
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": SOURCE_PAGE,
    "Origin": "https://www.wantgoo.com",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_rows_http() -> list[dict]:
    request = urllib.request.Request(DATA_URL, headers=HEADERS)
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=40, context=context) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("Wantgoo HTTP payload was empty or unexpected")
    return payload


def fetch_rows_playwright() -> list[dict]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page(
            locale="zh-TW",
            timezone_id="Asia/Taipei",
            user_agent=HEADERS["User-Agent"],
        )
        response = page.goto(SOURCE_PAGE, wait_until="domcontentloaded", timeout=90000)
        title = page.title()
        if (response and response.status == 403) or ("請稍候" in title) or ("Just a moment" in title):
            browser.close()
            raise RuntimeError(f"Wantgoo Cloudflare challenge (title={title!r})")
        page.wait_for_function(
            """() => Array.isArray(window.threeTradeData) && window.threeTradeData.length > 10
                || (window.$ && $.http && document.querySelectorAll('#dataTable tr').length > 10)""",
            timeout=90000,
        )
        payload = page.evaluate(
            """async (path) => {
                if (Array.isArray(window.threeTradeData) && window.threeTradeData.length > 10) {
                    return window.threeTradeData;
                }
                if (window.$ && $.http) {
                    return await new Promise((resolve, reject) => {
                        $.http.get(path).then(resolve).fail((_, __, error) => reject(error));
                    });
                }
                throw new Error("Wantgoo page did not expose threeTradeData");
            }""",
            DATA_PATH,
        )
        browser.close()
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("Wantgoo Playwright payload was empty or unexpected")
    return payload


def fetch_rows_twse(needed: int = 20, lookback_days: int = 50) -> list[dict]:
    """Official TWSE BFI82U series.

    外資及陸資(不含外資自營商) + 外資自營商 matches Wantgoo's
    sumForeignNoDealer + sumForeignWithDealer (億元, rounded to 2 decimals).
    Amounts are returned in 千元 so to_yi() stays unchanged.
    """
    today = datetime.now(TAIPEI).date()
    rows: list[dict] = []
    for offset in range(lookback_days):
        day = today - timedelta(days=offset)
        url = (
            "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
            f"?response=json&dayDate={day.strftime('%Y%m%d')}"
        )
        request = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=40, context=context) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data") or []
        foreign_no_dealer = None
        foreign_dealer = None
        for item in data:
            if not item or len(item) < 4:
                continue
            name = str(item[0])
            diff = int(str(item[3]).replace(",", ""))
            if "不含外資自營商" in name:
                foreign_no_dealer = diff
            elif name == "外資自營商":
                foreign_dealer = diff
        if payload.get("stat") == "OK" and foreign_no_dealer is not None:
            rows.append(
                {
                    "date": day.isoformat(),
                    "sumForeignNoDealer": (foreign_no_dealer or 0) / 1000,
                    "sumForeignWithDealer": (foreign_dealer or 0) / 1000,
                }
            )
        if len(rows) >= needed:
            break
        time.sleep(0.25)
    rows.reverse()
    if len(rows) < 10:
        raise RuntimeError(f"TWSE returned too few trading days: {len(rows)}")
    return rows


def fetch_rows() -> list[dict]:
    errors: list[str] = []
    try:
        return fetch_rows_http()
    except Exception as http_error:
        errors.append(f"HTTP: {http_error}")
        print(f"HTTP fetch failed ({http_error}); trying Playwright")
    try:
        return fetch_rows_playwright()
    except Exception as playwright_error:
        errors.append(f"Playwright: {playwright_error}")
        print(f"Playwright fetch failed ({playwright_error}); trying TWSE BFI82U")
    try:
        return fetch_rows_twse()
    except Exception as twse_error:
        errors.append(f"TWSE: {twse_error}")
        raise RuntimeError("All foreign-investor sources failed: " + " | ".join(errors)) from twse_error


def to_yi(row: dict) -> float:
    raw = (row.get("sumForeignNoDealer") or 0) + (row.get("sumForeignWithDealer") or 0)
    return round(raw / 100000, 2)


def main() -> None:
    rows = fetch_rows()
    rows.sort(key=lambda row: row.get("date", ""))
    latest_twenty = rows[-20:]
    days = []
    for row in latest_twenty:
        date = str(row.get("date", ""))[:10]
        if not date:
            continue
        days.append({"date": date, "netBuyYi": to_yi(row)})
    if len(days) < 10:
        raise RuntimeError(f"Not enough trading days parsed: {len(days)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "source": SOURCE_PAGE,
        "sourceName": "玩股網｜三大法人買賣金額",
        "field": "外資合計（不含自營 + 外資自營商）",
        "unit": "億元",
        "updatedAt": datetime.now(TAIPEI).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "days": days,
    }
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days to {OUT} (latest {days[-1]['date']})")


if __name__ == "__main__":
    main()
