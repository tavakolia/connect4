from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connect4.board import Board


# ANSI color codes
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


class Piece(enum.Enum):
    """Player piece identifiers used throughout the game state."""

    RED = "R"
    YELLOW = "Y"

    @property
    def opponent(self) -> Piece:
        """Return the opposing piece color."""
        return Piece.YELLOW if self == Piece.RED else Piece.RED

    @property
    def colored_name(self) -> str:
        """Piece name wrapped in its ANSI color."""
        ansi = ANSI_RED if self == Piece.RED else ANSI_YELLOW
        return f"{ansi}{self.name}{ANSI_RESET}"


@dataclasses.dataclass(frozen=True)
class MoveAnalysis:
    """Score assigned to a candidate move during search."""

    column: int
    score: float
    max_depth: int


@dataclasses.dataclass(frozen=True)
class MoveResult:
    """Move chosen by a player, with optional search diagnostics."""

    column: int
    analysis: list[MoveAnalysis] | None = None


@dataclasses.dataclass(frozen=True)
class GameState:
    """Immutable snapshot emitted after each move during game play."""

    board: Board
    piece: Piece
    column: int
    winner: Piece | None
    is_draw: bool
    analysis: list[MoveAnalysis] | None = None
