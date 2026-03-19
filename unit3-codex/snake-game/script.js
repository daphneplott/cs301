const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const startBtn = document.getElementById("start");
const statusEl = document.getElementById("status");
const difficultyEl = document.getElementById("difficulty");

const gridSize = 20;
const cellSize = canvas.width / gridSize;
const bestKey = "snake_best_score";

const speeds = {
  easy: 150,
  normal: 110,
  hard: 80,
};

let snake = [];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let food = { x: 10, y: 10 };
let score = 0;
let best = Number(localStorage.getItem(bestKey)) || 0;
let running = false;
let paused = false;
let intervalId = null;
let selectedSpeed = speeds[difficultyEl.value];

bestEl.textContent = String(best);

function resetGame() {
  snake = [
    { x: 8, y: 10 },
    { x: 7, y: 10 },
    { x: 6, y: 10 },
  ];
  direction = { x: 1, y: 0 };
  nextDirection = { x: 1, y: 0 };
  score = 0;
  scoreEl.textContent = String(score);
  paused = false;
  statusEl.textContent = "Ready";
  placeFood();
  draw();
}

function startGame() {
  if (intervalId) {
    clearInterval(intervalId);
  }
  selectedSpeed = speeds[difficultyEl.value];
  intervalId = setInterval(tick, selectedSpeed);
  running = true;
  paused = false;
  statusEl.textContent = "Running";
}

function endGame() {
  running = false;
  paused = false;
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
  statusEl.textContent = "Game Over";
}

function placeFood() {
  let placed = false;
  while (!placed) {
    const candidate = {
      x: Math.floor(Math.random() * gridSize),
      y: Math.floor(Math.random() * gridSize),
    };
    const occupied = snake.some((seg) => seg.x === candidate.x && seg.y === candidate.y);
    if (!occupied) {
      food = candidate;
      placed = true;
    }
  }
}

function setDirection(newDir) {
  if (newDir.x === -direction.x && newDir.y === -direction.y) {
    return;
  }
  nextDirection = newDir;
}

function tick() {
  if (!running || paused) {
    return;
  }

  direction = nextDirection;
  const head = snake[0];
  const newHead = { x: head.x + direction.x, y: head.y + direction.y };

  const hitWall =
    newHead.x < 0 || newHead.x >= gridSize || newHead.y < 0 || newHead.y >= gridSize;
  const hitSelf = snake.some((seg) => seg.x === newHead.x && seg.y === newHead.y);

  if (hitWall || hitSelf) {
    endGame();
    return;
  }

  snake.unshift(newHead);

  if (newHead.x === food.x && newHead.y === food.y) {
    score += 1;
    scoreEl.textContent = String(score);
    if (score > best) {
      best = score;
      bestEl.textContent = String(best);
      localStorage.setItem(bestKey, String(best));
    }
    placeFood();
  } else {
    snake.pop();
  }

  draw();
}

function drawCell(cell, color, stroke) {
  ctx.fillStyle = color;
  ctx.fillRect(cell.x * cellSize, cell.y * cellSize, cellSize, cellSize);
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    ctx.strokeRect(cell.x * cellSize + 1, cell.y * cellSize + 1, cellSize - 2, cellSize - 2);
  }
}

function drawGrid() {
  ctx.fillStyle = "#f9f4ec";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#e6dac9";
  ctx.lineWidth = 1;
  for (let i = 0; i <= gridSize; i += 1) {
    ctx.beginPath();
    ctx.moveTo(i * cellSize, 0);
    ctx.lineTo(i * cellSize, canvas.height);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i * cellSize);
    ctx.lineTo(canvas.width, i * cellSize);
    ctx.stroke();
  }
}

function draw() {
  drawGrid();

  drawCell(food, "#d3422a", "#a83222");

  snake.forEach((segment, index) => {
    const isHead = index === 0;
    drawCell(segment, isHead ? "#2f7d6d" : "#3f9b87", "#1c5f52");
  });
}

function togglePause() {
  if (!running) {
    return;
  }
  paused = !paused;
  statusEl.textContent = paused ? "Paused" : "Running";
}

document.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (["arrowup", "arrowdown", "arrowleft", "arrowright", " ", "space"].includes(key)) {
    event.preventDefault();
  }

  switch (key) {
    case "arrowup":
    case "w":
      setDirection({ x: 0, y: -1 });
      break;
    case "arrowdown":
    case "s":
      setDirection({ x: 0, y: 1 });
      break;
    case "arrowleft":
    case "a":
      setDirection({ x: -1, y: 0 });
      break;
    case "arrowright":
    case "d":
      setDirection({ x: 1, y: 0 });
      break;
    case " ":
    case "space":
      togglePause();
      break;
    default:
      break;
  }
});

difficultyEl.addEventListener("change", () => {
  selectedSpeed = speeds[difficultyEl.value];
});

startBtn.addEventListener("click", () => {
  resetGame();
  startGame();
});

resetGame();
