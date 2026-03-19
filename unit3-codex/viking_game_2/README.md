# Viking Game 2 — Hnefatafl 11x11

Open `index.html` in a browser to play.

## Controls
- Click a piece to select it.
- Legal destinations highlight in blue.
- Click a highlighted square to move.
- Click elsewhere to deselect.
- Use “Reset Game” to restart.

## Rules Implemented
- Pieces: Attackers (black), Defenders (white), King (gold).
- Movement: All pieces move any number of empty squares orthogonally (rook-like). No diagonal moves, no jumping.
- Special squares:
  - Corners are escape squares (only the King may enter).
  - The center square is the throne (only the King may enter).
- Captures:
  - A non-king piece is captured if, after a move, it is sandwiched orthogonally between two opposing pieces.
  - The throne and corners count as capturing surfaces for attackers if a defender is trapped against them, even if the throne/corner is empty.
  - Only the King may use the throne or corners as a friendly surface for capturing an attacker; regular defenders cannot.
- King capture:
  - The King is captured only when surrounded on all four orthogonal sides by attackers.
- Win conditions:
  - Defenders win if the King reaches any corner.
  - Attackers win if the King is captured.

## Starting Setup (11x11, 0-based coordinates)
- King: (5,5)
- Defenders (12):
  - (5,4), (5,6), (4,5), (6,5)
  - (5,3), (5,7), (3,5), (7,5)
  - (4,4), (4,6), (6,4), (6,6)
- Attackers (24):
  - Top: (0,3), (0,4), (0,5), (0,6), (0,7), (1,5)
  - Bottom: (10,3), (10,4), (10,5), (10,6), (10,7), (9,5)
  - Left: (3,0), (4,0), (5,0), (6,0), (7,0), (5,1)
  - Right: (3,10), (4,10), (5,10), (6,10), (7,10), (5,9)
