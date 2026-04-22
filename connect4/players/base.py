from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from connect4.board import Board
from connect4.types import MoveResult, Piece


class Player(Protocol):
    """Protocol implemented by any object that can choose a legal move."""

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        """Return the chosen move for `piece` on the given board state."""
        ...


@runtime_checkable
class InteractivePlayer(Player, Protocol):
    """Marker protocol for players that require human interaction through the UI."""

    is_interactive: ClassVar[bool]
