(() => {
  const canvas = document.getElementById("leaves");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const colors = ["#c23b22", "#d4572a", "#e07a3d", "#b91c1c", "#f0a35a", "#8a1f14", "#c4782b"];
  let leaves = [];
  let width = 0;
  let height = 0;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function maplePath(context) {
    context.beginPath();
    context.moveTo(0, -18);
    context.bezierCurveTo(4, -10, 9, -9, 12, -14);
    context.bezierCurveTo(10, -4, 16, -2, 18, -6);
    context.bezierCurveTo(14, 2, 8, 4, 6, 8);
    context.bezierCurveTo(11, 10, 14, 16, 11, 20);
    context.bezierCurveTo(6, 16, 3, 14, 0, 22);
    context.bezierCurveTo(-3, 14, -6, 16, -11, 20);
    context.bezierCurveTo(-14, 16, -11, 10, -6, 8);
    context.bezierCurveTo(-8, 4, -14, 2, -18, -6);
    context.bezierCurveTo(-16, -2, -10, -4, -12, -14);
    context.bezierCurveTo(-9, -9, -4, -10, 0, -18);
    context.closePath();
  }

  function spawn(randomY = true) {
    const depth = 0.35 + Math.random() * 0.9;
    return {
      x: Math.random() * width,
      y: randomY ? Math.random() * height : -30,
      size: 10 + depth * 22,
      speed: 0.35 + depth * 1.15,
      sway: 0.4 + Math.random() * 1.3,
      phase: Math.random() * Math.PI * 2,
      rot: Math.random() * Math.PI,
      spin: (Math.random() - 0.5) * 0.02,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 0.35 + depth * 0.5,
    };
  }

  function resetLeaves() {
    const count = Math.min(68, Math.floor(width / 18));
    leaves = Array.from({ length: count }, () => spawn(true));
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    for (const leaf of leaves) {
      leaf.phase += 0.01 * leaf.sway;
      leaf.x += Math.sin(leaf.phase) * leaf.sway;
      leaf.y += leaf.speed;
      leaf.rot += leaf.spin;
      if (leaf.y > height + 40) {
        Object.assign(leaf, spawn(false));
      }
      ctx.save();
      ctx.translate(leaf.x, leaf.y);
      ctx.rotate(leaf.rot);
      ctx.scale(leaf.size / 28, leaf.size / 28);
      ctx.globalAlpha = leaf.alpha;
      ctx.fillStyle = leaf.color;
      maplePath(ctx);
      ctx.fill();
      ctx.restore();
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", () => {
    resize();
    resetLeaves();
  });
  resize();
  resetLeaves();
  draw();
})();
