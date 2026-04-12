from __future__ import annotations

import enum
import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connect4.board import Board


# ANSI color codes
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"


class Piece(enum.Enum):
    RED = "R"
    YELLOW = "Y"

    @property
    def opponent(self) -> Piece:
        return Piece.YELLOW if self == Piece.RED else Piece.RED

    @property
    def colored_name(self) -> str:
        """Piece name wrapped in its ANSI color."""
        ansi = ANSI_RED if self == Piece.RED else ANSI_YELLOW
        return f"{ansi}{self.name}{ANSI_RESET}"


@dataclasses.dataclass(frozen=True)
class MoveAnalysis:
    column: int
    score: float
    max_depth: int


@dataclasses.dataclass(frozen=True)
class MoveResult:
    column: int
    analysis: list[MoveAnalysis] | None = None


@dataclasses.dataclass(frozen=True)
class GameState:
    board: Board
    piece: Piece
    column: int
    winner: Piece | None
    is_draw: bool
    analysis: list[MoveAnalysis] | None = None
