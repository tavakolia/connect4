from __future__ import annotations

import math

from connect4.board import Board
from connect4.types import Piece

_SCORE_TWO = 10
_SCORE_THREE = 100
_SCORE_CENTER = 6


def evaluate(board: Board, piece: Piece) -> float:
    """Score a board from piece's perspective. Positive = favorable."""
    opponent = piece.opponent

    if board.has_winner(piece):
        return math.inf
    if board.has_winner(opponent):
        return -math.inf

    score = 0.0

    center_col = Board.COLS // 2
    center_count = sum(1 for row in range(Board.ROWS) if board.get(row, center_col) == piece)
    score += center_count * _SCORE_CENTER

    score += _score_all_windows(board, piece, opponent)

    return score


def _score_window(window: list[Piece | None], piece: Piece, opponent: Piece) -> float:
    own = window.count(piece)
    opp = window.count(opponent)
    empty = window.count(None)

    if own == 3 and empty == 1:
        return _SCORE_THREE
    if own == 2 and empty == 2:
        return _SCORE_TWO
    if opp == 3 and empty == 1:
        return -_SCORE_THREE
    return 0


def _score_all_windows(board: Board, piece: Piece, opponent: Piece) -> float:
    score = 0.0
    get = board.get

    # Horizontal
    for row in range(Board.ROWS):
        for col in range(Board.COLS - 3):
            window = [get(row, col + i) for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Vertical
    for row in range(Board.ROWS - 3):
        for col in range(Board.COLS):
            window = [get(row + i, col) for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Diagonal NE
    for row in range(Board.ROWS - 3):
        for col in range(Board.COLS - 3):
            window = [get(row + i, col + i) for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Diagonal NW
    for row in range(3, Board.ROWS):
        for col in range(Board.COLS - 3):
            window = [get(row - i, col + i) for i in range(4)]
            score += _score_window(window, piece, opponent)

    return score
