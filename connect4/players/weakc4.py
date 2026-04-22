from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class WeakC4Player:
    """A heuristic player based on the WeakC4 explanation at https://2swap.github.io/WeakC4/explanation/

    Since the full WeakC4 steady-state graph isn't strictly embedded here, this player implements
    the core heuristic priority list fallback that doesn't require the precomputed graph:
    1. Make a winning move, if available.
    2. Block an opponent winning move, if available.
    3. Play pure Claimeven (play in a column where the piece lands on an even row, meaning
       it acts as a call-and-response in the same column the opponent just played).
    4. Fallback to random if no pure Claimeven moves exist.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        opponent = piece.opponent
        valid = board.valid_columns()

        # Priority 1: Make a winning move, if available
        for col in valid:
            child = board.copy()
            row = child.drop(col, piece)
            if child.is_winner_at(row, col, piece):
                return MoveResult(column=col)

        # Priority 2: Block an opponent winning move, if available
        for col in valid:
            child = board.copy()
            row = child.drop(col, opponent)
            if child.is_winner_at(row, col, opponent):
                return MoveResult(column=col)

        # Priority 3: Play pure Claimeven.
        # "The trick is for Red to merely play call-and-response with Yellow,
        # playing in the same column as Yellow's last move. As this strategy involves
        # Red filling rows 2, 4, and 6, this strategy was dubbed Claimeven."
        # In our board (0-indexed where 0 is bottom), rows 2, 4, 6 correspond to indices 1, 3, 5.
        # This occurs when dropping a piece into a column currently holding an odd number of pieces
        # (1, 3, or 5 pieces currently).
        for col in valid:
            # Calculate number of pieces in column to find our landing row.
            pieces_in_col = sum(board.get(r, col) is not None for r in range(board.ROWS))
            if pieces_in_col % 2 != 0:
                return MoveResult(column=col)

        # Priority 4: Fallback to a random valid column
        return MoveResult(column=self._rng.choice(valid))
