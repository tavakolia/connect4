from __future__ import annotations

from typing import Protocol

from connect4.board import Board
from connect4.types import MoveResult, Piece


class HumanUIDelegate(Protocol):
    def request_column(self, piece: Piece) -> str: ...
    def show_error_invalid_input(self, raw: str) -> None: ...
    def show_error_out_of_range(self, display_col: int) -> None: ...
    def show_error_column_full(self, display_col: int) -> None: ...


class HumanPlayer:
    is_interactive = True

    def __init__(self, ui_delegate: HumanUIDelegate) -> None:
        self._ui = ui_delegate

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        while True:
            raw = self._ui.request_column(piece)
            try:
                display_col = int(raw)
            except ValueError:
                self._ui.show_error_invalid_input(raw)
                continue

            column = display_col - 1  # convert to 0-indexed

            if not board.is_valid_column(column):
                if column < 0 or column >= Board.COLS:
                    self._ui.show_error_out_of_range(display_col)
                else:
                    self._ui.show_error_column_full(display_col)
                continue

            return MoveResult(column=column)
