from connect4.board import Board
from connect4.players.greedy import GreedyPlayer
from connect4.types import Piece


class TestGreedyPlayer:
    def test_takes_winning_move(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_blocks_opponent_win(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_prefers_win_over_block(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        for col in range(4, 7):
            board.drop(column=col, piece=Piece.YELLOW)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_random_when_no_threats(self):
        board = Board()
        player = GreedyPlayer(seed=42)
        result = player.choose_column(board, Piece.RED)
        assert 0 <= result.column < Board.COLS

    def test_seeded_is_deterministic(self):
        board = Board()
        p1 = GreedyPlayer(seed=42)
        p2 = GreedyPlayer(seed=42)
        assert (
            p1.choose_column(board, Piece.RED).column == p2.choose_column(board, Piece.RED).column
        )
