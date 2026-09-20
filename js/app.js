const SOURCE =
  "https://www.wantgoo.com/stock/institutional-investors/three-trade-for-trading-amount";

function formatYi(value) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toLocaleString("zh-TW", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function direction(value) {
  if (value > 0) return "買超";
  if (value < 0) return "賣超";
  return "持平";
}

function tone(value) {
  if (value > 0) return "buy";
  if (value < 0) return "sell";
  return "";
}

function renderStats(days) {
  const latest = days[days.length - 1];
  const sum = days.reduce((acc, day) => acc + day.netBuyYi, 0);
  const buys = days.filter((day) => day.netBuyYi > 0).length;
  const sells = days.filter((day) => day.netBuyYi < 0).length;
  const cards = [
    { label: "最新一日", value: formatYi(latest.netBuyYi), extra: latest.date, cls: tone(latest.netBuyYi) },
    { label: "近20日合計", value: formatYi(Number(sum.toFixed(2))), extra: "億元", cls: tone(sum) },
    { label: "買超天數", value: `${buys} 日`, extra: "近20交易日", cls: "buy" },
    { label: "賣超天數", value: `${sells} 日`, extra: "近20交易日", cls: "sell" },
  ];
  document.getElementById("stats").innerHTML = cards
    .map(
      (card) => `
        <article class="stat">
          <p class="label">${card.label}</p>
          <p class="value ${card.cls}">${card.value}</p>
          <p class="label">${card.extra}</p>
        </article>`
    )
    .join("");
}

function renderTable(days) {
  const body = document.getElementById("rows");
  const newestFirst = [...days].reverse();
  body.innerHTML = newestFirst
    .map(
      (day) => `
        <tr>
          <td>${day.date}</td>
          <td class="num ${tone(day.netBuyYi)}">${formatYi(day.netBuyYi)}</td>
          <td class="${tone(day.netBuyYi)}">${direction(day.netBuyYi)}</td>
        </tr>`
    )
    .join("");
}

function renderChart(days) {
  const labels = days.map((day) => day.date.slice(5).replace("-", "/"));
  const values = days.map((day) => day.netBuyYi);
  const ctx = document.getElementById("chart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "外資買賣超（億元）",
          data: values,
          backgroundColor: values.map((value) =>
            value >= 0 ? "rgba(196, 58, 44, 0.88)" : "rgba(61, 107, 74, 0.82)"
          ),
          borderColor: values.map((value) =>
            value >= 0 ? "rgba(140, 32, 24, 0.95)" : "rgba(36, 74, 48, 0.95)"
          ),
          borderWidth: 1,
          borderRadius: 6,
          maxBarThickness: 36,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(item) {
              return `外資 ${formatYi(item.parsed.y)} 億`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "交易日", color: "#6d4333" },
          ticks: { color: "#6d4333", maxRotation: 60, minRotation: 40 },
          grid: { display: false },
        },
        y: {
          title: { display: true, text: "買賣超（億元）", color: "#6d4333" },
          ticks: {
            color: "#6d4333",
            callback(value) {
              return value;
            },
          },
          grid: { color: "rgba(122, 46, 26, 0.12)" },
        },
      },
    },
  });
}

async function main() {
  const response = await fetch("data/foreign.json", { cache: "no-store" });
  if (!response.ok) throw new Error("無法讀取外資資料");
  const payload = await response.json();
  const days = payload.days || [];
  document.getElementById("updated").textContent =
    `更新 ${payload.updatedAt || ""} · 來源 ${payload.sourceName || SOURCE}`;
  renderStats(days);
  renderTable(days);
  renderChart(days);
}

main().catch((error) => {
  document.getElementById("updated").textContent = error.message;
});
