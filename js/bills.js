(() => {
  const canvas = document.getElementById("bills");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const kinds = [
    { face: "1000", fill: "#d51f32", stripe: "#8e0f1c", ink: "#fff5d6" },
    { face: "1000", fill: "#c11428", stripe: "#7a0c18", ink: "#ffe9a8" },
    { face: "500", fill: "#b81d2c", stripe: "#6e1018", ink: "#fff0c2" },
    { face: "100", fill: "#e23b45", stripe: "#9a1620", ink: "#fff7e0" },
  ];
  let bills = [];
  let width = 0;
  let height = 0;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function roundRect(context, x, y, w, h, r) {
    const radius = Math.min(r, w / 2, h / 2);
    context.beginPath();
    context.moveTo(x + radius, y);
    context.arcTo(x + w, y, x + w, y + h, radius);
    context.arcTo(x + w, y + h, x, y + h, radius);
    context.arcTo(x, y + h, x, y, radius);
    context.arcTo(x, y, x + w, y, radius);
    context.closePath();
  }

  function spawn(randomY = true) {
    const depth = 0.4 + Math.random() * 0.9;
    const kind = kinds[Math.floor(Math.random() * kinds.length)];
    return {
      x: Math.random() * width,
      y: randomY ? Math.random() * height : -50,
      w: 42 + depth * 38,
      h: 20 + depth * 18,
      speed: 0.7 + depth * 1.6,
      sway: 0.5 + Math.random() * 1.6,
      phase: Math.random() * Math.PI * 2,
      rot: Math.random() * Math.PI,
      spin: (Math.random() - 0.5) * 0.045,
      alpha: 0.42 + depth * 0.45,
      kind,
    };
  }

  function resetBills() {
    const count = Math.min(56, Math.floor(width / 22) + 18);
    bills = Array.from({ length: count }, () => spawn(true));
  }

  function drawBill(bill) {
    const flutter = Math.cos(bill.phase * 1.4);
    ctx.save();
    ctx.translate(bill.x, bill.y);
    ctx.rotate(bill.rot);
    ctx.scale(1, 0.28 + Math.abs(flutter) * 0.72);
    ctx.globalAlpha = bill.alpha;

    const x = -bill.w / 2;
    const y = -bill.h / 2;
    roundRect(ctx, x, y, bill.w, bill.h, 4);
    ctx.fillStyle = bill.kind.fill;
    ctx.fill();

    ctx.strokeStyle = "rgba(255, 236, 180, 0.55)";
    ctx.lineWidth = 1.4;
    ctx.stroke();

    roundRect(ctx, x + 4, y + 3, bill.w - 8, bill.h - 6, 3);
    ctx.strokeStyle = bill.kind.stripe;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = bill.kind.stripe;
    ctx.fillRect(x + bill.w * 0.18, y + 2, 3, bill.h - 4);

    ctx.fillStyle = bill.kind.ink;
    ctx.font = `700 ${Math.max(8, bill.h * 0.38)}px "Noto Sans TC", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(`NT$${bill.kind.face}`, 0, 0);

    ctx.restore();
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    for (const bill of bills) {
      bill.phase += 0.018 * bill.sway;
      bill.x += Math.sin(bill.phase) * bill.sway;
      bill.y += bill.speed;
      bill.rot += bill.spin;
      if (bill.y > height + 60) {
        Object.assign(bill, spawn(false));
      }
      drawBill(bill);
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", () => {
    resize();
    resetBills();
  });
  resize();
  resetBills();
  draw();
})();
