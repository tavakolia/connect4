import pytest
from connect4.board import Board
from connect4.players.human import HumanPlayer
from connect4.types import Piece


class TestHumanPlayer:
    def test_valid_input(self):
        player = HumanPlayer(input_fn=lambda _: "3")
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_non_integer(self):
        inputs = iter(["abc", "3"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_out_of_range(self):
        inputs = iter(["9", "-1", "3"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_full_column(self):
        board = Board()
        for _ in range(Board.ROWS):
            board.drop(column=3, piece=Piece.RED)
        inputs = iter(["3", "4"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(board, Piece.RED)
        assert result.column == 4

    def test_no_analysis(self):
        player = HumanPlayer(input_fn=lambda _: "0")
        result = player.choose_column(Board(), Piece.RED)
        assert result.analysis is None
