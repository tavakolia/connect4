from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class RandomPlayer:
    """Player that selects uniformly from the currently legal columns."""

    def __init__(self, seed: int | None = None) -> None:
        """Create a random player with optional deterministic seeding."""
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        """Choose any legal column without board evaluation."""
        column = self._rng.choice(board.valid_columns())
        return MoveResult(column=column)
