from __future__ import annotations

from typing import Protocol

from connect4.board import Board
from connect4.types import MoveResult, Piece


class Player(Protocol):
    def choose_column(self, board: Board, piece: Piece) -> MoveResult: ...
