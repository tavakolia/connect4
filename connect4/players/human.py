from __future__ import annotations

from collections.abc import Callable

from connect4.board import Board
from connect4.types import MoveResult, Piece


class HumanPlayer:
    def __init__(self, input_fn: Callable[[str], str] = input) -> None:
        self._input_fn = input_fn

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        while True:
            raw = self._input_fn(f"Player {piece.name}, pick a column (1-7): ")
            try:
                display_col = int(raw)
            except ValueError:
                print(f"Invalid input: '{raw}'. Please enter a number 1-7.")
                continue
            column = display_col - 1  # convert to 0-indexed
            if not board.is_valid_column(column):
                if column < 0 or column >= Board.COLS:
                    print(f"Column {display_col} is out of range. Pick 1-7.")
                else:
                    print(f"Column {display_col} is full. Pick another.")
                continue
            return MoveResult(column=column)
