from __future__ import annotations

from typing import ClassVar, Protocol

from connect4.board import Board
from connect4.types import MoveResult, Piece


class Player(Protocol):
    is_interactive: ClassVar[bool]

    def choose_column(self, board: Board, piece: Piece) -> MoveResult: ...
