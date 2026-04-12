from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class GreedyPlayer:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        opponent = piece.opponent
        valid = board.valid_columns()

        for col in valid:
            child = board.copy()
            child.drop(col, piece)
            if child.has_winner(piece):
                return MoveResult(column=col)

        for col in valid:
            child = board.copy()
            child.drop(col, opponent)
            if child.has_winner(opponent):
                return MoveResult(column=col)

        return MoveResult(column=self._rng.choice(valid))
