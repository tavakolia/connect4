from __future__ import annotations

from connect4.types import Piece


class Board:
    ROWS = 6
    COLS = 7
    CONNECT = 4

    def __init__(self) -> None:
        self._grid: list[list[Piece | None]] = [
            [None] * self.COLS for _ in range(self.ROWS)
        ]

    def drop(self, column: int, piece: Piece) -> int:
        """Drop a piece into the given column. Returns the row it landed in."""
        if column < 0 or column >= self.COLS:
            raise ValueError(f"Invalid column: {column}. Must be 0-{self.COLS - 1}")
        for row in range(self.ROWS):
            if self._grid[row][column] is None:
                self._grid[row][column] = piece
                return row
        raise ValueError(f"Column {column} is full")

    def get(self, row: int, col: int) -> Piece | None:
        """Get the piece at the given position, or None if empty."""
        return self._grid[row][col]

    def is_valid_column(self, column: int) -> bool:
        return 0 <= column < self.COLS and self._grid[self.ROWS - 1][column] is None

    def valid_columns(self) -> list[int]:
        return [col for col in range(self.COLS) if self.is_valid_column(col)]

    def is_full(self) -> bool:
        return all(self._grid[self.ROWS - 1][col] is not None for col in range(self.COLS))

    def copy(self) -> Board:
        new_board = Board()
        new_board._grid = [row[:] for row in self._grid]
        return new_board

    def has_winner(self, piece: Piece) -> bool:
        """Check if the given piece has four in a row."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self._grid[row][col] != piece:
                    continue
                for dr, dc in directions:
                    if self._check_line(row, col, dr, dc, piece):
                        return True
        return False

    def _check_line(self, row: int, col: int, dr: int, dc: int, piece: Piece) -> bool:
        for i in range(self.CONNECT):
            r = row + i * dr
            c = col + i * dc
            if r < 0 or r >= self.ROWS or c < 0 or c >= self.COLS:
                return False
            if self._grid[r][c] != piece:
                return False
        return True

    # Display characters
    _FILLED = "●"   # U+25CF BLACK CIRCLE
    _EMPTY = "○"    # U+25CB WHITE CIRCLE
    _RED_ANSI = "\033[91m"
    _YELLOW_ANSI = "\033[93m"
    _RESET_ANSI = "\033[0m"
    _BOX_V = "│"    # U+2502 BOX DRAWINGS LIGHT VERTICAL
    _BOX_BL = "└"   # U+2514 BOX DRAWINGS LIGHT UP AND RIGHT
    _BOX_BR = "┘"   # U+2518 BOX DRAWINGS LIGHT UP AND LEFT
    _BOX_H = "─"    # U+2500 BOX DRAWINGS LIGHT HORIZONTAL

    _DISPLAY = {
        Piece.RED: f"{_RED_ANSI}{_FILLED}{_RESET_ANSI}",
        Piece.YELLOW: f"{_YELLOW_ANSI}{_FILLED}{_RESET_ANSI}",
        None: _EMPTY,
    }

    def __str__(self) -> str:
        lines = []
        for row in range(self.ROWS - 1, -1, -1):
            cells = [self._DISPLAY[self._grid[row][col]] for col in range(self.COLS)]
            lines.append(f"{self._BOX_V} " + "  ".join(cells) + f" {self._BOX_V}")
        lines.append(self._BOX_BL + self._BOX_H * 22 + self._BOX_BR)
        lines.append("  " + "  ".join(str(i) for i in range(self.COLS)) + "  ")
        return "\n".join(lines)
