#!/usr/bin/env python3
"""Fetch the latest 20 trading days of foreign-investor net buying from TWSE."""

from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE_PAGE = "https://www.twse.com.tw/zh/trading/foreign/bfi82u.html"
DATA_URL = "https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=json&dayDate={date}"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "foreign.json"
TAIPEI = timezone(timedelta(hours=8))


def fetch_day(day: datetime) -> dict | None:
    request = urllib.request.Request(
        DATA_URL.format(date=day.strftime("%Y%m%d")),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Referer": SOURCE_PAGE,
        },
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=40, context=context) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("stat") != "OK":
        return None

    totals = {
        row[0]: int(row[3].replace(",", ""))
        for row in payload.get("data", [])
        if len(row) >= 4
    }
    foreign = totals.get("外資及陸資(不含外資自營商)")
    if foreign is None:
        return None
    foreign_dealer = totals.get("外資自營商", 0)
    return {
        "date": datetime.strptime(payload["date"], "%Y%m%d").strftime("%Y-%m-%d"),
        "netBuyYi": round((foreign + foreign_dealer) / 100_000_000, 2),
    }


def main() -> None:
    cursor = datetime.now(TAIPEI)
    days = []
    while len(days) < 20 and (datetime.now(TAIPEI) - cursor).days < 40:
        row = fetch_day(cursor)
        if row:
            days.append(row)
        cursor -= timedelta(days=1)
    days.reverse()
    if len(days) < 10:
        raise RuntimeError(f"Not enough trading days parsed: {len(days)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "source": SOURCE_PAGE,
        "sourceName": "臺灣證券交易所｜三大法人買賣金額統計表",
        "field": "外資合計（不含自營 + 外資自營商）",
        "unit": "億元",
        "updatedAt": datetime.now(TAIPEI).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "days": days,
    }
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days to {OUT}")


if __name__ == "__main__":
    main()
