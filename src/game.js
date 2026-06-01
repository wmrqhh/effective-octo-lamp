const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d");
const overlay = document.querySelector("#overlay");
const roundLabel = document.querySelector("#roundLabel");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const FLOOR = 430;
const GRAVITY = 0.82;
const keys = new Set();

const game = {
  running: false,
  round: 1,
  timer: 75,
  message: "准备战斗",
  shake: 0,
  lastTime: 0,
  winner: null,
};

const attacks = {
  jab: { name: "轻拳", damage: 7, range: 74, height: 48, duration: 190, cooldown: 280, windup: 55, knockback: 4 },
  kick: { name: "重踢", damage: 13, range: 98, height: 58, duration: 260, cooldown: 560, windup: 95, knockback: 8 },
};

function createFighter(config) {
  return {
    ...config,
    width: 58,
    height: 118,
    x: config.x,
    y: FLOOR - 118,
    vx: 0,
    vy: 0,
    health: 100,
    energy: 100,
    facing: config.facing,
    grounded: true,
    blocking: false,
    attack: null,
    attackStarted: 0,
    cooldownUntil: 0,
    hitConnected: false,
    hurtUntil: 0,
    aiNextDecision: 0,
    aiIntent: "wait",
    wins: config.wins ?? 0,
  };
}

const player = createFighter({ name: "玩家", x: 170, color: "#39e6ff", accent: "#d8fbff", facing: 1 });
const enemy = createFighter({ name: "AI 影刃", x: 730, color: "#ff4fd8", accent: "#ffe3f8", facing: -1 });

function resetRound(nextRound = game.round) {
  Object.assign(player, createFighter({ name: "玩家", x: 170, color: "#39e6ff", accent: "#d8fbff", facing: 1, wins: player.wins }));
  Object.assign(enemy, createFighter({ name: "AI 影刃", x: 730, color: "#ff4fd8", accent: "#ffe3f8", facing: -1, wins: enemy.wins }));
  game.round = nextRound;
  game.timer = 75;
  game.running = true;
  game.message = "战斗！";
  game.winner = null;
  game.lastTime = performance.now();
  roundLabel.textContent = String(game.round);
  overlay.classList.add("hidden");
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function centerOf(fighter) {
  return fighter.x + fighter.width / 2;
}

function distanceBetween(a, b) {
  return Math.abs(centerOf(a) - centerOf(b));
}

function faceOpponent(a, b) {
  a.facing = centerOf(a) < centerOf(b) ? 1 : -1;
}

function startAttack(fighter, type, now) {
  if (fighter.attack || fighter.cooldownUntil > now || fighter.energy < (type === "kick" ? 22 : 10)) return;
  fighter.attack = attacks[type];
  fighter.attackStarted = now;
  fighter.cooldownUntil = now + attacks[type].cooldown;
  fighter.hitConnected = false;
  fighter.energy -= type === "kick" ? 22 : 10;
}

function attackBox(fighter) {
  if (!fighter.attack) return null;
  const activeStart = fighter.attackStarted + fighter.attack.windup;
  const activeEnd = fighter.attackStarted + fighter.attack.duration - 55;
  const now = performance.now();
  if (now < activeStart || now > activeEnd) return null;

  const x = fighter.facing > 0 ? fighter.x + fighter.width - 3 : fighter.x - fighter.attack.range + 3;
  return {
    x,
    y: fighter.y + 24,
    width: fighter.attack.range,
    height: fighter.attack.height,
  };
}

function intersects(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

function receiveHit(target, attacker, attack, now) {
  const guarded = target.blocking && target.grounded && target.facing !== attacker.facing;
  const damage = guarded ? Math.ceil(attack.damage * 0.32) : attack.damage;
  target.health = clamp(target.health - damage, 0, 100);
  target.vx += attacker.facing * (guarded ? attack.knockback * 0.45 : attack.knockback);
  target.hurtUntil = now + (guarded ? 110 : 240);
  game.shake = guarded ? 4 : 9;
}

function resolveAttack(attacker, target, now) {
  const box = attackBox(attacker);
  if (!box || attacker.hitConnected) return;
  if (intersects(box, target)) {
    attacker.hitConnected = true;
    receiveHit(target, attacker, attacker.attack, now);
  }
}

function handlePlayer(now) {
  player.blocking = keys.has("s") && player.grounded && !player.attack;
  if (player.hurtUntil > now) return;

  const speed = player.blocking ? 1.6 : 4.9;
  player.vx = 0;
  if (keys.has("a")) player.vx -= speed;
  if (keys.has("d")) player.vx += speed;
  if (keys.has("w") && player.grounded && !player.blocking) {
    player.vy = -16;
    player.grounded = false;
  }
  if (keys.has("j")) startAttack(player, "jab", now);
  if (keys.has("k")) startAttack(player, "kick", now);
}

function handleEnemy(now) {
  const distance = distanceBetween(enemy, player);
  if (now > enemy.aiNextDecision) {
    if (enemy.health < 28 && distance < 150) enemy.aiIntent = Math.random() > 0.45 ? "retreat" : "block";
    else if (distance > 180) enemy.aiIntent = "chase";
    else if (distance < 82) enemy.aiIntent = Math.random() > 0.34 ? "attack" : "retreat";
    else enemy.aiIntent = Math.random() > 0.52 ? "attack" : "chase";
    enemy.aiNextDecision = now + 260 + Math.random() * 360;
  }

  enemy.blocking = enemy.aiIntent === "block" && enemy.grounded && !enemy.attack;
  if (enemy.hurtUntil > now) return;

  enemy.vx = 0;
  if (enemy.aiIntent === "chase") enemy.vx = enemy.facing * 3.7;
  if (enemy.aiIntent === "retreat") enemy.vx = -enemy.facing * 3.2;
  if (enemy.aiIntent === "attack" && distance < 130) {
    startAttack(enemy, Math.random() > 0.62 ? "kick" : "jab", now);
  }
  if (enemy.grounded && player.y < enemy.y - 20 && Math.random() > 0.985) {
    enemy.vy = -14;
    enemy.grounded = false;
  }
}

function updateFighter(fighter, now) {
  if (fighter.attack && now > fighter.attackStarted + fighter.attack.duration) fighter.attack = null;
  fighter.energy = clamp(fighter.energy + 0.085, 0, 100);

  fighter.vy += GRAVITY;
  fighter.x += fighter.vx;
  fighter.y += fighter.vy;
  fighter.vx *= 0.82;

  if (fighter.y + fighter.height >= FLOOR) {
    fighter.y = FLOOR - fighter.height;
    fighter.vy = 0;
    fighter.grounded = true;
  }
  fighter.x = clamp(fighter.x, 34, WIDTH - fighter.width - 34);
}

function endRound(message, winner) {
  game.running = false;
  game.message = message;
  game.winner = winner;
  if (winner) winner.wins += 1;
  overlay.querySelector("h2").textContent = message;
  overlay.querySelector("p").innerHTML = "按 <kbd>Enter</kbd> 进入下一回合";
  overlay.classList.remove("hidden");
}

function update(now) {
  const delta = Math.min(32, now - game.lastTime || 16);
  game.lastTime = now;
  if (!game.running) return;

  game.timer -= delta / 1000;
  faceOpponent(player, enemy);
  faceOpponent(enemy, player);
  handlePlayer(now);
  handleEnemy(now);
  updateFighter(player, now);
  updateFighter(enemy, now);
  resolveAttack(player, enemy, now);
  resolveAttack(enemy, player, now);
  game.shake = Math.max(0, game.shake - 0.45);

  if (player.health <= 0 && enemy.health <= 0) endRound("平局！", null);
  else if (enemy.health <= 0) endRound("你赢了！", player);
  else if (player.health <= 0) endRound("AI 获胜", enemy);
  else if (game.timer <= 0) {
    if (player.health === enemy.health) endRound("时间到：平局", null);
    else endRound(player.health > enemy.health ? "时间到：你赢了！" : "时间到：AI 获胜", player.health > enemy.health ? player : enemy);
  }
}

function drawBar(x, y, width, height, value, color, label) {
  ctx.fillStyle = "rgba(255,255,255,0.12)";
  ctx.fillRect(x, y, width, height);
  ctx.fillStyle = color;
  ctx.fillRect(x, y, width * (value / 100), height);
  ctx.strokeStyle = "rgba(255,255,255,0.5)";
  ctx.strokeRect(x, y, width, height);
  ctx.fillStyle = "#f7fbff";
  ctx.font = "700 16px system-ui";
  ctx.fillText(label, x, y - 9);
}

function drawBackground() {
  const gradient = ctx.createLinearGradient(0, 0, 0, HEIGHT);
  gradient.addColorStop(0, "#162149");
  gradient.addColorStop(0.58, "#101733");
  gradient.addColorStop(1, "#080b16");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  ctx.strokeStyle = "rgba(57,230,255,0.16)";
  ctx.lineWidth = 2;
  for (let x = -80; x < WIDTH + 100; x += 80) {
    ctx.beginPath();
    ctx.moveTo(x, FLOOR);
    ctx.lineTo(x + 240, HEIGHT);
    ctx.stroke();
  }
  for (let y = FLOOR; y < HEIGHT; y += 28) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WIDTH, y);
    ctx.stroke();
  }

  ctx.fillStyle = "rgba(255,79,216,0.22)";
  ctx.fillRect(0, FLOOR, WIDTH, 7);
  ctx.fillStyle = "rgba(57,230,255,0.14)";
  ctx.fillRect(0, FLOOR + 7, WIDTH, HEIGHT - FLOOR);

  ctx.fillStyle = "rgba(255,255,255,0.08)";
  for (let i = 0; i < 12; i += 1) {
    const bx = i * 90 + 20;
    const bh = 80 + (i % 4) * 28;
    ctx.fillRect(bx, FLOOR - 40 - bh, 44, bh);
  }
}

function drawFighter(fighter) {
  const hurt = fighter.hurtUntil > performance.now();
  ctx.save();
  ctx.translate(fighter.x + fighter.width / 2, fighter.y);
  ctx.scale(fighter.facing, 1);

  ctx.fillStyle = "rgba(0,0,0,0.28)";
  ctx.beginPath();
  ctx.ellipse(0, fighter.height + 8, 42, 10, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = hurt ? "#ffffff" : fighter.color;
  ctx.fillRect(-21, 34, 42, 58);
  ctx.fillStyle = fighter.accent;
  ctx.fillRect(-16, 16, 32, 28);
  ctx.fillStyle = fighter.color;
  ctx.fillRect(-28, 92, 18, 30);
  ctx.fillRect(10, 92, 18, 30);

  const punching = fighter.attack && fighter.attack.name === "轻拳";
  const kicking = fighter.attack && fighter.attack.name === "重踢";
  ctx.fillRect(17, 46, punching ? 58 : 26, 14);
  ctx.fillRect(-43, 48, 26, 14);
  if (kicking) ctx.fillRect(16, 101, 72, 15);

  if (fighter.blocking) {
    ctx.strokeStyle = "rgba(255,255,255,0.72)";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.arc(22, 56, 42, -1.25, 1.25);
    ctx.stroke();
  }
  ctx.restore();

  const box = attackBox(fighter);
  if (box) {
    ctx.fillStyle = fighter.color.replace("#", "#") + "33";
    ctx.fillRect(box.x, box.y, box.width, box.height);
  }
}

function drawHud() {
  drawBar(34, 42, 360, 24, player.health, "#39e6ff", `玩家  胜场 ${player.wins}`);
  drawBar(WIDTH - 394, 42, 360, 24, enemy.health, "#ff4fd8", `AI 影刃  胜场 ${enemy.wins}`);
  drawBar(34, 84, 220, 10, player.energy, "#ffd166", "能量");
  drawBar(WIDTH - 254, 84, 220, 10, enemy.energy, "#ffd166", "能量");

  ctx.fillStyle = "rgba(0,0,0,0.32)";
  ctx.fillRect(WIDTH / 2 - 54, 28, 108, 56);
  ctx.fillStyle = "#f7fbff";
  ctx.font = "800 32px system-ui";
  ctx.textAlign = "center";
  ctx.fillText(String(Math.max(0, Math.ceil(game.timer))).padStart(2, "0"), WIDTH / 2, 66);
  ctx.textAlign = "left";
}

function render() {
  ctx.save();
  if (game.shake > 0) ctx.translate((Math.random() - 0.5) * game.shake, (Math.random() - 0.5) * game.shake);
  drawBackground();
  drawFighter(player);
  drawFighter(enemy);
  drawHud();
  ctx.restore();
}

function loop(now) {
  update(now);
  render();
  requestAnimationFrame(loop);
}

window.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (["a", "d", "w", "s", "j", "k", "enter"].includes(key)) event.preventDefault();
  keys.add(key);
  if (key === "enter" && !game.running) resetRound(game.round + (game.winner ? 1 : 0));
});

window.addEventListener("keyup", (event) => {
  keys.delete(event.key.toLowerCase());
});

resetRound(1);
game.running = false;
overlay.classList.remove("hidden");
requestAnimationFrame(loop);
