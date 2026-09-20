(() => {
  const canvas = document.getElementById("ingots");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const palettes = [
    { light: "#fff4a8", mid: "#ffe566", dark: "#e6b800", rim: "#c49200" },
    { light: "#fff8c2", mid: "#ffd84a", dark: "#d4a017", rim: "#b8860b" },
    { light: "#fff1a0", mid: "#f5c518", dark: "#c99700", rim: "#a67c00" },
    { light: "#ffe97a", mid: "#ffcc33", dark: "#d4af37", rim: "#b8960b" },
  ];
  let ingots = [];
  let width = 0;
  let height = 0;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function spawn(randomY = true) {
    const depth = 0.45 + Math.random() * 0.9;
    return {
      x: Math.random() * width,
      y: randomY ? Math.random() * height : -40,
      size: 18 + depth * 28,
      speed: 0.55 + depth * 1.35,
      sway: 0.35 + Math.random() * 1.2,
      phase: Math.random() * Math.PI * 2,
      rot: (Math.random() - 0.5) * 0.8,
      spin: (Math.random() - 0.5) * 0.03,
      alpha: 0.55 + depth * 0.4,
      palette: palettes[Math.floor(Math.random() * palettes.length)],
    };
  }

  function resetIngots() {
    const count = Math.min(62, Math.floor(width / 20) + 16);
    ingots = Array.from({ length: count }, () => spawn(true));
  }

  function drawYuanbao(ingot) {
    const { light, mid, dark, rim } = ingot.palette;
    const s = ingot.size / 36;
    ctx.save();
    ctx.translate(ingot.x, ingot.y);
    ctx.rotate(ingot.rot);
    ctx.scale(s, s);
    ctx.globalAlpha = ingot.alpha;

    ctx.fillStyle = "rgba(80, 10, 0, 0.22)";
    ctx.beginPath();
    ctx.ellipse(0, 17, 16, 4.5, 0, 0, Math.PI * 2);
    ctx.fill();

    const body = ctx.createLinearGradient(-18, -12, 16, 18);
    body.addColorStop(0, light);
    body.addColorStop(0.45, mid);
    body.addColorStop(1, dark);

    ctx.beginPath();
    ctx.moveTo(-18, 1);
    ctx.bezierCurveTo(-22, 8, -12, 16, 0, 16);
    ctx.bezierCurveTo(12, 16, 22, 8, 18, 1);
    ctx.bezierCurveTo(14, 7, -14, 7, -18, 1);
    ctx.fillStyle = body;
    ctx.fill();
    ctx.strokeStyle = rim;
    ctx.lineWidth = 1.1;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(-18, 1);
    ctx.bezierCurveTo(-26, -2, -24, -13, -13, -11);
    ctx.quadraticCurveTo(-6, -3, 0, 1);
    ctx.quadraticCurveTo(6, -3, 13, -11);
    ctx.bezierCurveTo(24, -13, 26, -2, 18, 1);
    ctx.bezierCurveTo(8, -1, -8, -1, -18, 1);
    ctx.fillStyle = mid;
    ctx.fill();
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(-13, -11);
    ctx.quadraticCurveTo(0, -5, 13, -11);
    ctx.strokeStyle = light;
    ctx.lineWidth = 1.4;
    ctx.stroke();

    ctx.beginPath();
    ctx.ellipse(-5, 5, 6, 2.6, -0.5, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255, 255, 230, 0.55)";
    ctx.fill();

    ctx.fillStyle = rim;
    ctx.font = "700 9px 'Noto Sans TC', sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("元", 0, 5);

    ctx.restore();
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    for (const ingot of ingots) {
      ingot.phase += 0.012 * ingot.sway;
      ingot.x += Math.sin(ingot.phase) * ingot.sway;
      ingot.y += ingot.speed;
      ingot.rot += ingot.spin;
      if (ingot.y > height + 50) {
        Object.assign(ingot, spawn(false));
      }
      drawYuanbao(ingot);
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", () => {
    resize();
    resetIngots();
  });
  resize();
  resetIngots();
  draw();
})();
