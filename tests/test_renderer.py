import io
import sys

import pytest

from connect4.board import Board
from connect4.renderer import TerminalRenderer
from connect4.types import Piece


@pytest.fixture
def renderer():
    return TerminalRenderer()


@pytest.fixture
def board():
    return Board()


class TestFormatBoard:
    def test_empty_board_has_column_numbers(self, renderer, board):
        s = renderer.format_board(board)
        for i in range(1, 8):
            assert str(i) in s

    def test_empty_board_has_empty_circles(self, renderer, board):
        s = renderer.format_board(board)
        assert "○" in s  # empty circle

    def test_placed_piece_has_filled_circle(self, renderer, board):
        board.drop(column=3, piece=Piece.RED)
        s = renderer.format_board(board)
        assert "●" in s  # filled circle

    def test_board_has_box_borders(self, renderer, board):
        s = renderer.format_board(board)
        assert "│" in s
        assert "└" in s
        assert "┘" in s
        assert "─" in s

    def test_red_piece_has_ansi_red(self, renderer, board):
        board.drop(column=0, piece=Piece.RED)
        s = renderer.format_board(board)
        assert "\033[91m" in s  # ANSI red

    def test_yellow_piece_has_ansi_yellow(self, renderer, board):
        board.drop(column=0, piece=Piece.YELLOW)
        s = renderer.format_board(board)
        assert "\033[93m" in s  # ANSI yellow


class TestShowMethods:
    def _capture(self, fn):
        """Capture stdout from a callable."""
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            fn()
        finally:
            sys.stdout = old
        return buf.getvalue()

    def test_show_welcome(self, renderer):
        output = self._capture(lambda: renderer.show_welcome(Piece.RED, Piece.YELLOW))
        assert "Connect 4" in output
        assert "RED" in output
        assert "YELLOW" in output

    def test_show_board(self, renderer, board):
        output = self._capture(lambda: renderer.show_board(board))
        assert "○" in output

    def test_show_move(self, renderer, board):
        board.drop(column=3, piece=Piece.RED)
        output = self._capture(lambda: renderer.show_move(Piece.RED, 3, board))
        assert "column 4" in output  # 0-indexed → 1-indexed
        assert "●" in output

    def test_show_winner(self, renderer):
        output = self._capture(lambda: renderer.show_winner(Piece.RED))
        assert "wins" in output
        assert "RED" in output

    def test_show_draw(self, renderer):
        output = self._capture(lambda: renderer.show_draw())
        assert "draw" in output
