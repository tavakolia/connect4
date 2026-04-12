from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class RandomPlayer:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        column = self._rng.choice(board.valid_columns())
        return MoveResult(column=column)
