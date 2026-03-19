const BOARD_SIZE = 11;
const EMPTY = null;
const ATTACKER = "A";
const DEFENDER = "D";
const KING = "K";

const CORNERS = [
  [0, 0], [0, 10], [10, 0], [10, 10]
];
const THRONE = [5, 5];

const boardEl = document.getElementById("board");
const turnDisplay = document.getElementById("turnDisplay");
const capturedDisplay = document.getElementById("capturedDisplay");
const messageDisplay = document.getElementById("messageDisplay");
const resetBtn = document.getElementById("resetBtn");

let board = [];
let currentTurn = ATTACKER;
let selected = null;
let legalMoves = [];
let capturedAttackers = 0;
let capturedDefenders = 0;
let gameOver = false;

function initBoard() {
  board = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(EMPTY));

  // King
  placePiece(5, 5, KING);

  // Defenders (12)
  const defenders = [
    [5, 4], [5, 6], [4, 5], [6, 5],
    [5, 3], [5, 7], [3, 5], [7, 5],
    [4, 4], [4, 6], [6, 4], [6, 6]
  ];
  defenders.forEach(([r, c]) => placePiece(r, c, DEFENDER));

  // Attackers (24)
  const attackers = [
    [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
    [1, 5],
    [10, 3], [10, 4], [10, 5], [10, 6], [10, 7],
    [9, 5],
    [3, 0], [4, 0], [5, 0], [6, 0], [7, 0],
    [5, 1],
    [3, 10], [4, 10], [5, 10], [6, 10], [7, 10],
    [5, 9]
  ];
  attackers.forEach(([r, c]) => placePiece(r, c, ATTACKER));
}

function placePiece(r, c, piece) {
  board[r][c] = piece;
}

function renderBoard() {
  boardEl.innerHTML = "";
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = r;
      cell.dataset.col = c;

      if (isCorner(r, c)) cell.classList.add("corner");
      if (isThrone(r, c)) cell.classList.add("throne");

      if (selected && selected.r === r && selected.c === c) {
        cell.classList.add("selected");
      }
      if (isLegalMove(r, c)) {
        cell.classList.add("legal");
      }

      const piece = board[r][c];
      if (piece) {
        const pieceEl = document.createElement("div");
        pieceEl.className = "piece";
        if (piece === ATTACKER) pieceEl.classList.add("attacker");
        if (piece === DEFENDER) pieceEl.classList.add("defender");
        if (piece === KING) pieceEl.classList.add("king");
        cell.appendChild(pieceEl);
      }

      boardEl.appendChild(cell);
    }
  }
}

function isCorner(r, c) {
  return CORNERS.some(([cr, cc]) => cr === r && cc === c);
}

function isThrone(r, c) {
  return r === THRONE[0] && c === THRONE[1];
}

function isSpecial(r, c) {
  return isCorner(r, c) || isThrone(r, c);
}

function isFriendly(piece, side) {
  if (!piece) return false;
  if (side === ATTACKER) return piece === ATTACKER;
  return piece === DEFENDER || piece === KING;
}

function canSelect(piece) {
  if (!piece) return false;
  return isFriendly(piece, currentTurn);
}

function legalMovesFor(r, c) {
  const piece = board[r][c];
  if (!piece) return [];
  const isKing = piece === KING;

  const dirs = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1]
  ];
  const moves = [];

  for (const [dr, dc] of dirs) {
    let nr = r + dr;
    let nc = c + dc;
    while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE) {
      if (board[nr][nc] !== EMPTY) break;
      if (isSpecial(nr, nc) && !isKing) break;
      moves.push([nr, nc]);
      nr += dr;
      nc += dc;
    }
  }
  return moves;
}

function isLegalMove(r, c) {
  return legalMoves.some(([lr, lc]) => lr === r && lc === c);
}

function clearSelection() {
  selected = null;
  legalMoves = [];
}

function movePiece(fromR, fromC, toR, toC) {
  const piece = board[fromR][fromC];
  board[fromR][fromC] = EMPTY;
  board[toR][toC] = piece;

  handleCaptures(toR, toC, piece);

  if (checkDefenderWin()) {
    gameOver = true;
    messageDisplay.textContent = "Defenders win! The King escaped.";
  } else if (checkAttackerWin()) {
    gameOver = true;
    messageDisplay.textContent = "Attackers win! The King was captured.";
  } else {
    currentTurn = currentTurn === ATTACKER ? DEFENDER : ATTACKER;
    messageDisplay.textContent = "Move completed.";
  }
}

function handleCaptures(r, c, movingPiece) {
  const side = currentTurn;
  const dirs = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1]
  ];

  for (const [dr, dc] of dirs) {
    const er = r + dr;
    const ec = c + dc;
    if (!inBounds(er, ec)) continue;

    const enemy = board[er][ec];
    if (!enemy) continue;
    if (enemy === KING) continue; // King has special capture rules
    if (isFriendly(enemy, side)) continue;

    const or = er + dr;
    const oc = ec + dc;
    if (!inBounds(or, oc)) continue;

    const opposite = board[or][oc];
    const oppositeFriendly = isFriendly(opposite, side);
    const oppositeSpecial = isSpecial(or, oc);

    let captures = false;
    if (oppositeFriendly) {
      captures = true;
    } else if (oppositeSpecial) {
      if (side === ATTACKER) {
        captures = true;
      } else if (side === DEFENDER && movingPiece === KING) {
        captures = true;
      }
    }

    if (captures) {
      if (enemy === ATTACKER) capturedAttackers++;
      if (enemy === DEFENDER) capturedDefenders++;
      board[er][ec] = EMPTY;
    }
  }
}

function checkDefenderWin() {
  const kingPos = findKing();
  if (!kingPos) return false;
  return isCorner(kingPos[0], kingPos[1]);
}

function checkAttackerWin() {
  const kingPos = findKing();
  if (!kingPos) return false;
  const [r, c] = kingPos;

  const adjacent = [
    [r - 1, c],
    [r + 1, c],
    [r, c - 1],
    [r, c + 1]
  ];

  for (const [ar, ac] of adjacent) {
    if (!inBounds(ar, ac)) return false;
    if (board[ar][ac] !== ATTACKER) return false;
  }
  return true;
}

function findKing() {
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      if (board[r][c] === KING) return [r, c];
    }
  }
  return null;
}

function inBounds(r, c) {
  return r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE;
}

function updateStatus() {
  turnDisplay.textContent = gameOver
    ? "Game Over"
    : currentTurn === ATTACKER
      ? "Attackers"
      : "Defenders";
  capturedDisplay.textContent = `${capturedAttackers} / ${capturedDefenders}`;
}

function onBoardClick(event) {
  if (gameOver) return;
  const cell = event.target.closest(".cell");
  if (!cell) return;

  const r = Number(cell.dataset.row);
  const c = Number(cell.dataset.col);
  const piece = board[r][c];

  if (selected) {
    if (isLegalMove(r, c)) {
      movePiece(selected.r, selected.c, r, c);
      clearSelection();
      updateStatus();
      renderBoard();
      return;
    }
  }

  if (canSelect(piece)) {
    selected = { r, c };
    legalMoves = legalMovesFor(r, c);
    messageDisplay.textContent = "Select a destination.";
  } else {
    clearSelection();
    messageDisplay.textContent = "Illegal selection.";
  }

  renderBoard();
}

function resetGame() {
  currentTurn = ATTACKER;
  capturedAttackers = 0;
  capturedDefenders = 0;
  gameOver = false;
  clearSelection();
  initBoard();
  updateStatus();
  messageDisplay.textContent = "Select a piece to begin.";
  renderBoard();
}

boardEl.addEventListener("click", onBoardClick);
resetBtn.addEventListener("click", resetGame);

resetGame();
