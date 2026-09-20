#!/usr/bin/env python3
"""Fetch the latest 20 trading days of 外資買賣超 from TWSE."""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

SOURCE_PAGE = "https://www.twse.com.tw/zh/trading/foreign/bfi82u.html"
DATA_URL = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "foreign.json"
TAIPEI = timezone(timedelta(hours=8))


def fetch_day(date: datetime) -> dict | None:
    request = urllib.request.Request(
        f"{DATA_URL}?response=json&dayDate={date:%Y%m%d}&type=day",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    if payload.get("stat") != "OK":
        return None
    for row in payload.get("data", []):
        if row[0] == "外資及陸資(不含外資自營商)":
            net_buy_yi = round(int(row[3].replace(",", "")) / 100000000, 2)
            return {"date": date.strftime("%Y-%m-%d"), "netBuyYi": net_buy_yi}
    raise RuntimeError(f"Foreign investor row missing for {date:%Y-%m-%d}")


def fetch_rows() -> list[dict]:
    day = datetime.now(TAIPEI)
    rows = []
    for _ in range(60):
        row = fetch_day(day)
        if row:
            rows.append(row)
            if len(rows) == 20:
                return list(reversed(rows))
        day -= timedelta(days=1)
    raise RuntimeError(f"Only found {len(rows)} trading days in the last 60 days")


def main() -> None:
    rows = fetch_rows()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "source": SOURCE_PAGE,
        "sourceName": "臺灣證券交易所｜三大法人買賣金額統計表",
        "field": "外資及陸資（不含外資自營商）",
        "unit": "億元",
        "updatedAt": datetime.now(TAIPEI).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "days": rows,
    }
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} days to {OUT}")


if __name__ == "__main__":
    main()
