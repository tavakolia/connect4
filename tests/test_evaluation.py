import math

from connect4.board import Board
from connect4.evaluation import evaluate
from connect4.types import Piece


class TestTerminalStates:
    def test_win_returns_positive_inf(self):
        board = Board()
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        score = evaluate(board, Piece.RED)
        assert score == math.inf

    def test_loss_returns_negative_inf(self):
        board = Board()
        for col in range(4):
            board.drop(column=col, piece=Piece.YELLOW)
        score = evaluate(board, Piece.RED)
        assert score == -math.inf

    def test_empty_board_near_zero(self):
        board = Board()
        score = evaluate(board, Piece.RED)
        assert abs(score) < 50


class TestCenterPreference:
    def test_center_piece_scores_higher_than_edge(self):
        board_center = Board()
        board_center.drop(column=3, piece=Piece.RED)
        board_edge = Board()
        board_edge.drop(column=0, piece=Piece.RED)
        assert evaluate(board_center, Piece.RED) > evaluate(board_edge, Piece.RED)


class TestWindowScoring:
    def test_three_in_a_row_scores_high(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        score = evaluate(board, Piece.RED)
        assert score > 50

    def test_opponent_three_scores_negative(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        score = evaluate(board, Piece.RED)
        assert score < -50

    def test_two_in_a_row_positive(self):
        board = Board()
        board.drop(column=2, piece=Piece.RED)
        board.drop(column=3, piece=Piece.RED)
        score_2 = evaluate(board, Piece.RED)

        board_1 = Board()
        board_1.drop(column=3, piece=Piece.RED)
        score_1 = evaluate(board_1, Piece.RED)

        assert score_2 > score_1
