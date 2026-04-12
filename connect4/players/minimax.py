from __future__ import annotations

import logging
import math
from collections.abc import Callable

from connect4.board import Board
from connect4.evaluation import evaluate as default_evaluate
from connect4.types import MoveAnalysis, MoveResult, Piece

logger = logging.getLogger(__name__)

_COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]


class MinimaxPlayer:
    def __init__(
        self,
        depth: int = 6,
        evaluate: Callable[[Board, Piece], float] | None = None,
    ) -> None:
        self.depth = depth
        self.evaluate = evaluate or default_evaluate

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        analyses: list[MoveAnalysis] = []
        best_col = self._search(board, piece, analyses)
        logger.info("Chose column %d (analyses: %s)", best_col, analyses)
        return MoveResult(column=best_col, analysis=analyses)

    def _search(self, board: Board, piece: Piece, analyses: list[MoveAnalysis]) -> int:
        best_score = -math.inf
        best_col = board.valid_columns()[0]

        for col in _COLUMN_ORDER:
            if not board.is_valid_column(col):
                continue
            child = board.copy()
            child.drop(col, piece)

            if child.has_winner(piece):
                score = math.inf
            else:
                score = self._minimax(
                    child, piece, self.depth - 1, -math.inf, math.inf, False
                )

            analyses.append(MoveAnalysis(column=col, score=score, depth_reached=self.depth))
            logger.debug("Column %d: score=%.2f", col, score)

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def _minimax(
        self,
        board: Board,
        piece: Piece,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        opponent = piece.opponent

        if board.has_winner(piece):
            return math.inf
        if board.has_winner(opponent):
            return -math.inf
        if board.is_full():
            return 0
        if depth == 0:
            return self.evaluate(board, piece)

        if maximizing:
            max_score = -math.inf
            for col in _COLUMN_ORDER:
                if not board.is_valid_column(col):
                    continue
                child = board.copy()
                child.drop(col, piece)
                score = self._minimax(child, piece, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = math.inf
            for col in _COLUMN_ORDER:
                if not board.is_valid_column(col):
                    continue
                child = board.copy()
                child.drop(col, opponent)
                score = self._minimax(child, piece, depth - 1, alpha, beta, True)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return min_score
