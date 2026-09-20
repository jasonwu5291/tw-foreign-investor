# 台股外資買賣超（近 20 日）

公開靜態網站，紀錄台灣股市三大法人中的**外資**買賣超，並以統計直條圖顯示近 20 個交易日走勢。

- 網站（任何人知道連結即可讀取）：https://jasonwu5291.github.io/tw-foreign-investor/
- 倉庫：https://github.com/jasonwu5291/tw-foreign-investor
- 資料來源（僅觀察此頁外資欄位）：[玩股網｜三大法人買賣金額](https://www.wantgoo.com/stock/institutional-investors/three-trade-for-trading-amount)
- 欄位：外資合計（不含自營 + 外資自營商），單位為億元

更新資料時，在本機執行 `python scripts/update_data.py`，再把 `data/foreign.json` 推上 GitHub。
