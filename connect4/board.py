from __future__ import annotations

from connect4.types import Piece


class Board:
    """Mutable Connect 4 board using the standard 6x7 grid and connect-4 rule.

    The game dimensions are fixed as class constants because this exercise is
    specifically standard Connect 4, not a generalized connect-N engine.
    """

    ROWS = 6
    COLS = 7
    CONNECT = 4

    def __init__(self) -> None:
        """Initialize an empty board."""
        self._grid: list[list[Piece | None]] = [[None] * self.COLS for _ in range(self.ROWS)]

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
        """Return True if a piece can still be dropped into the column."""
        return 0 <= column < self.COLS and self._grid[self.ROWS - 1][column] is None

    def valid_columns(self) -> list[int]:
        """Return all columns that currently accept another piece."""
        return [col for col in range(self.COLS) if self.is_valid_column(col)]

    def is_full(self) -> bool:
        """Return True when no additional legal moves remain."""
        return all(self._grid[self.ROWS - 1][col] is not None for col in range(self.COLS))

    def copy(self) -> Board:
        """Return a deep copy of the board state."""
        new_board = Board()
        new_board._grid = [row[:] for row in self._grid]
        return new_board

    def has_winner(self, piece: Piece) -> bool:
        """Check if the given piece has four in a row (full board scan)."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self._grid[row][col] != piece:
                    continue
                for dr, dc in directions:
                    if self._check_line(row, col, dr, dc, piece):
                        return True
        return False

    def is_winner_at(self, row: int, col: int, piece: Piece) -> bool:
        """Check if the piece at (row, col) completes a four-in-a-row.

        Much faster than has_winner() — only checks lines through one cell
        instead of scanning the entire board. Use after a drop when you know
        which cell to check.
        """
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = 1
            # Count in the positive direction
            for sign in (1, -1):
                for i in range(1, self.CONNECT):
                    r = row + i * dr * sign
                    c = col + i * dc * sign
                    if r < 0 or r >= self.ROWS or c < 0 or c >= self.COLS:
                        break
                    if self._grid[r][c] != piece:
                        break
                    count += 1
            if count >= self.CONNECT:
                return True
        return False

    def undo(self, column: int) -> None:
        """Remove the topmost piece from a column. Inverse of drop()."""
        for row in range(self.ROWS - 1, -1, -1):
            if self._grid[row][column] is not None:
                self._grid[row][column] = None
                return
        raise ValueError(f"Column {column} is empty")

    def _check_line(self, row: int, col: int, dr: int, dc: int, piece: Piece) -> bool:
        """Return True if `piece` occupies a full connect-length line from a start cell."""
        for i in range(self.CONNECT):
            r = row + i * dr
            c = col + i * dc
            if r < 0 or r >= self.ROWS or c < 0 or c >= self.COLS:
                return False
            if self._grid[r][c] != piece:
                return False
        return True

    def __repr__(self) -> str:
        """Plain text representation for debugging and logging."""
        cell_map = {Piece.RED: "R", Piece.YELLOW: "Y", None: "."}
        lines = []
        for row in range(self.ROWS - 1, -1, -1):
            lines.append(" ".join(cell_map[self._grid[row][col]] for col in range(self.COLS)))
        lines.append(" ".join(str(i + 1) for i in range(self.COLS)))
        return "\n".join(lines)
