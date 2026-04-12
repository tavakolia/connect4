from __future__ import annotations

from collections.abc import Callable

from connect4.board import Board
from connect4.types import MoveResult, Piece


class HumanPlayer:
    def __init__(self, input_fn: Callable[[str], str] = input) -> None:
        self._input_fn = input_fn

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        while True:
            raw = self._input_fn(f"Player {piece.name}, pick a column (0-6): ")
            try:
                column = int(raw)
            except ValueError:
                print(f"Invalid input: '{raw}'. Please enter a number 0-6.")
                continue
            if not board.is_valid_column(column):
                if column < 0 or column >= Board.COLS:
                    print(f"Column {column} is out of range. Pick 0-6.")
                else:
                    print(f"Column {column} is full. Pick another.")
                continue
            return MoveResult(column=column)
