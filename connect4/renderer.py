from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from connect4.types import ANSI_RED, ANSI_RESET, ANSI_YELLOW, Piece

if TYPE_CHECKING:
    from connect4.board import Board


from connect4.players.human import HumanUIDelegate


class GameRenderer(HumanUIDelegate, Protocol):
    """UI contract for rendering game events and gathering human input."""

    def show_welcome(self, you: Piece, bot: Piece) -> None: ...

    def show_board(self, board: Board) -> None: ...

    def show_move(self, piece: Piece, column: int, board: Board) -> None: ...

    def show_winner(self, winner: Piece) -> None: ...

    def show_draw(self) -> None: ...


class TerminalRenderer:
    """Renders game events to stdout with ANSI colors and box-drawing characters."""

    # Display characters
    _FILLED = "●"   # U+25CF BLACK CIRCLE
    _EMPTY = "○"    # U+25CB WHITE CIRCLE
    _BOX_V = "│"    # U+2502 BOX DRAWINGS LIGHT VERTICAL
    _BOX_BL = "└"   # U+2514 BOX DRAWINGS LIGHT UP AND RIGHT
    _BOX_BR = "┘"   # U+2518 BOX DRAWINGS LIGHT UP AND LEFT
    _BOX_H = "─"    # U+2500 BOX DRAWINGS LIGHT HORIZONTAL

    _DISPLAY = {
        Piece.RED: f"{ANSI_RED}{_FILLED}{ANSI_RESET}",
        Piece.YELLOW: f"{ANSI_YELLOW}{_FILLED}{ANSI_RESET}",
        None: _EMPTY,
    }

    def format_board(self, board: Board) -> str:
        """Format the board as a string with ANSI colors and box-drawing borders."""
        from connect4.board import Board as BoardClass

        # Build an empty row to measure visible width (no ANSI escapes)
        empty_inner = " " + "  ".join([self._EMPTY] * board.COLS) + " "
        border = self._BOX_BL + self._BOX_H * len(empty_inner) + self._BOX_BR

        lines = []
        for row in range(board.ROWS - 1, -1, -1):
            cells = [self._DISPLAY[board.get(row, col)] for col in range(board.COLS)]
            lines.append(self._BOX_V + " " + "  ".join(cells) + " " + self._BOX_V)
        lines.append(border)
        lines.append("  " + "  ".join(str(i + 1) for i in range(board.COLS)) + "  ")
        return "\n".join(lines)

    def show_welcome(self, you: Piece, bot: Piece) -> None:
        print(f"Connect 4 — You are {you.colored_name}, bot is {bot.colored_name}")

    def show_board(self, board: Board) -> None:
        print(self.format_board(board))

    def show_move(self, piece: Piece, column: int, board: Board) -> None:
        print(f"\n{piece.colored_name} plays column {column + 1}")
        print(self.format_board(board))

    def show_winner(self, winner: Piece) -> None:
        print(f"\n{winner.colored_name} wins!")

    def show_draw(self) -> None:
        print("\nIt's a draw!")

    # HumanUIDelegate implementation

    def request_column(self, piece: Piece) -> str:
        return input(f"Player {piece.name}, pick a column (1-7): ")

    def show_error_invalid_input(self, raw: str) -> None:
        print(f"Invalid input: '{raw}'. Please enter a number 1-7.")

    def show_error_out_of_range(self, display_col: int) -> None:
        print(f"Column {display_col} is out of range. Pick 1-7.")

    def show_error_column_full(self, display_col: int) -> None:
        print(f"Column {display_col} is full. Pick another.")
