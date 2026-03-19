const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const turnEl = document.getElementById("turn");
const resetBtn = document.getElementById("reset");
const capturedAttackersEl = document.getElementById("captured-attackers");
const capturedDefendersEl = document.getElementById("captured-defenders");

const SIZE = 9;
const CORNERS = new Set(["0,0", "0,8", "8,0", "8,8"]);

const initialBoard = () => {
  const empty = Array.from({ length: SIZE }, () => Array(SIZE).fill(null));
  const place = (r, c, v) => {
    empty[r][c] = v;
  };

  place(4, 4, "K");
  [
    [4, 3],
    [4, 5],
    [3, 4],
    [5, 4],
    [4, 2],
    [4, 6],
    [2, 4],
    [6, 4],
  ].forEach(([r, c]) => place(r, c, "D"));

  [
    [0, 3],
    [0, 4],
    [0, 5],
    [1, 4],
    [3, 0],
    [4, 0],
    [5, 0],
    [4, 1],
    [8, 3],
    [8, 4],
    [8, 5],
    [7, 4],
    [3, 8],
    [4, 8],
    [5, 8],
    [4, 7],
  ].forEach(([r, c]) => place(r, c, "A"));

  return empty;
};

let board = initialBoard();
let currentPlayer = "A";
let selected = null;
let legalMoves = [];
let gameOver = false;
let capturedAttackers = 0;
let capturedDefenders = 0;

const isCorner = (r, c) => CORNERS.has(`${r},${c}`);

const resetGame = () => {
  board = initialBoard();
  currentPlayer = "A";
  selected = null;
  legalMoves = [];
  gameOver = false;
  capturedAttackers = 0;
  capturedDefenders = 0;
  updateStatus("Select a piece to begin.");
  render();
};

const updateStatus = (message) => {
  statusEl.textContent = message;
};

const pieceBelongsToCurrentPlayer = (piece) => {
  if (!piece) return false;
  if (currentPlayer === "A") return piece === "A";
  return piece === "D" || piece === "K";
};

const isEnemy = (piece) => {
  if (!piece) return false;
  if (currentPlayer === "A") return piece === "D" || piece === "K";
  return piece === "A";
};

const inBounds = (r, c) => r >= 0 && r < SIZE && c >= 0 && c < SIZE;

const computeLegalMoves = (r, c) => {
  const moves = [];
  const piece = board[r][c];
  const directions = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ];

  directions.forEach(([dr, dc]) => {
    let nr = r + dr;
    let nc = c + dc;
    while (inBounds(nr, nc) && board[nr][nc] === null) {
      if (piece !== "K" && isCorner(nr, nc)) break;
      moves.push({ r: nr, c: nc });
      nr += dr;
      nc += dc;
    }
  });

  return moves;
};

const highlightMoves = () => {
  const tiles = boardEl.querySelectorAll(".tile");
  tiles.forEach((tile) => tile.classList.remove("selected", "legal"));

  if (!selected) return;
  const selectedIndex = selected.r * SIZE + selected.c;
  tiles[selectedIndex]?.classList.add("selected");

  legalMoves.forEach((move) => {
    const index = move.r * SIZE + move.c;
    tiles[index]?.classList.add("legal");
  });
};

const render = () => {
  boardEl.innerHTML = "";
  for (let r = 0; r < SIZE; r += 1) {
    for (let c = 0; c < SIZE; c += 1) {
      const tile = document.createElement("button");
      tile.type = "button";
      tile.className = "tile";
      if ((r + c) % 2 === 1) tile.classList.add("dark");
      if (isCorner(r, c)) tile.classList.add("corner");
      tile.dataset.row = r;
      tile.dataset.col = c;

      const piece = board[r][c];
      if (piece) {
        const pieceEl = document.createElement("span");
        pieceEl.className = "piece";
        if (piece === "A") pieceEl.classList.add("attacker");
        if (piece === "D") pieceEl.classList.add("defender");
        if (piece === "K") pieceEl.classList.add("king");
        pieceEl.textContent = piece === "K" ? "K" : "";
        tile.appendChild(pieceEl);
      }

      boardEl.appendChild(tile);
    }
  }

  turnEl.textContent = currentPlayer === "A" ? "Attackers" : "Defenders";
  capturedAttackersEl.textContent = capturedAttackers;
  capturedDefendersEl.textContent = capturedDefenders;
  highlightMoves();
};

const captureAt = (r, c) => {
  const piece = board[r][c];
  if (!piece || piece === "K") return;
  board[r][c] = null;
  if (piece === "A") capturedAttackers += 1;
  if (piece === "D") capturedDefenders += 1;
};

const handleCaptures = (r, c) => {
  const directions = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ];

  directions.forEach(([dr, dc]) => {
    const adjR = r + dr;
    const adjC = c + dc;
    const beyondR = r + dr * 2;
    const beyondC = c + dc * 2;
    if (!inBounds(adjR, adjC) || !inBounds(beyondR, beyondC)) return;

    const adjacent = board[adjR][adjC];
    const beyond = board[beyondR][beyondC];

    if (isEnemy(adjacent) && pieceBelongsToCurrentPlayer(beyond)) {
      captureAt(adjR, adjC);
    }
  });
};

const kingCaptured = () => {
  let kingPos = null;
  for (let r = 0; r < SIZE; r += 1) {
    for (let c = 0; c < SIZE; c += 1) {
      if (board[r][c] === "K") {
        kingPos = { r, c };
        break;
      }
    }
    if (kingPos) break;
  }
  if (!kingPos) return true;

  const directions = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ];

  return directions.every(([dr, dc]) => {
    const nr = kingPos.r + dr;
    const nc = kingPos.c + dc;
    return inBounds(nr, nc) && board[nr][nc] === "A";
  });
};

const kingEscaped = () => {
  for (const corner of CORNERS) {
    const [r, c] = corner.split(",").map(Number);
    if (board[r][c] === "K") return true;
  }
  return false;
};

const switchTurn = () => {
  currentPlayer = currentPlayer === "A" ? "D" : "A";
};

const makeMove = (toR, toC) => {
  if (!selected) return;
  const piece = board[selected.r][selected.c];
  board[selected.r][selected.c] = null;
  board[toR][toC] = piece;

  handleCaptures(toR, toC);

  if (kingEscaped()) {
    gameOver = true;
    updateStatus("Defenders win! The king escaped.");
  } else if (currentPlayer === "A" && kingCaptured()) {
    gameOver = true;
    updateStatus("Attackers win! The king is surrounded.");
  }

  selected = null;
  legalMoves = [];

  if (!gameOver) {
    switchTurn();
    updateStatus("Select a piece.");
  }

  render();
};

boardEl.addEventListener("click", (event) => {
  const tile = event.target.closest(".tile");
  if (!tile || gameOver) return;
  const r = Number(tile.dataset.row);
  const c = Number(tile.dataset.col);

  const move = legalMoves.find((m) => m.r === r && m.c === c);
  if (selected && move) {
    makeMove(r, c);
    return;
  }

  const piece = board[r][c];
  if (pieceBelongsToCurrentPlayer(piece)) {
    selected = { r, c };
    legalMoves = computeLegalMoves(r, c);
    updateStatus("Choose a destination.");
  } else {
    selected = null;
    legalMoves = [];
    updateStatus("Select one of your pieces.");
  }

  render();
});

resetBtn.addEventListener("click", resetGame);

resetGame();
