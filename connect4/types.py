from __future__ import annotations

import enum
import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connect4.board import Board


class Piece(enum.Enum):
    RED = "R"
    YELLOW = "Y"

    @property
    def opponent(self) -> Piece:
        return Piece.YELLOW if self == Piece.RED else Piece.RED


@dataclasses.dataclass(frozen=True)
class MoveAnalysis:
    column: int
    score: float
    depth_reached: int


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
