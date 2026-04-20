from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from connect4.board import Board
from connect4.types import MoveResult, Piece


class Player(Protocol):
    def choose_column(self, board: Board, piece: Piece) -> MoveResult: ...


@runtime_checkable
class InteractivePlayer(Player, Protocol):
    is_interactive: ClassVar[bool]
