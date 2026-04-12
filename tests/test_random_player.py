import pytest
from connect4.board import Board
from connect4.players.random import RandomPlayer
from connect4.types import Piece


class TestRandomPlayer:
    def test_chooses_valid_column(self):
        board = Board()
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert 0 <= result.column < Board.COLS

    def test_no_analysis(self):
        board = Board()
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.analysis is None

    def test_seeded_is_deterministic(self):
        board = Board()
        p1 = RandomPlayer(seed=42)
        p2 = RandomPlayer(seed=42)
        r1 = p1.choose_column(board, Piece.RED)
        r2 = p2.choose_column(board, Piece.RED)
        assert r1.column == r2.column

    def test_avoids_full_columns(self):
        board = Board()
        for col in range(Board.COLS):
            if col == 4:
                continue
            for _ in range(Board.ROWS):
                board.drop(column=col, piece=Piece.RED)
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 4
