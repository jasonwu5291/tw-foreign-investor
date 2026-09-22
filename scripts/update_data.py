#!/usr/bin/env python3
"""Fetch the latest 20 trading days of 外資買賣超 from Wantgoo."""

from __future__ import annotations

import json
import ssl
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
        page.goto(SOURCE_PAGE, wait_until="domcontentloaded", timeout=90000)
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


def fetch_rows() -> list[dict]:
    try:
        return fetch_rows_http()
    except Exception as http_error:
        print(f"HTTP fetch failed ({http_error}); trying Playwright")
        return fetch_rows_playwright()


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
