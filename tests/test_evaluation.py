import math

from connect4.board import Board
from connect4.evaluation import _is_contiguous, _score_window, evaluate
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
        assert score == 0.0


class TestCenterPreference:
    def test_center_piece_scores_higher_than_edge(self):
        board_center = Board()
        board_center.drop(column=3, piece=Piece.RED)
        board_edge = Board()
        board_edge.drop(column=0, piece=Piece.RED)
        assert evaluate(board_center, Piece.RED) == 6.0
        assert evaluate(board_edge, Piece.RED) == 0.0


class TestWindowScoring:
    def test_three_in_a_row_scores_high(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        score = evaluate(board, Piece.RED)
        assert score == 110.0

    def test_opponent_three_scores_negative(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        score = evaluate(board, Piece.RED)
        assert score == -110.0

    def test_two_in_a_row_positive(self):
        board = Board()
        board.drop(column=2, piece=Piece.RED)
        board.drop(column=3, piece=Piece.RED)
        score_2 = evaluate(board, Piece.RED)

        board_1 = Board()
        board_1.drop(column=3, piece=Piece.RED)
        score_1 = evaluate(board_1, Piece.RED)

        assert score_2 == 36.0
        assert score_1 == 6.0


class TestIsContiguous:
    def test_single_piece_is_contiguous(self):
        # [R, None, None, None] — trivially contiguous
        window = [Piece.RED, None, None, None]
        assert _is_contiguous(window, Piece.RED) is True

    def test_adjacent_pieces_are_contiguous(self):
        window = [Piece.RED, Piece.RED, None, None]
        assert _is_contiguous(window, Piece.RED) is True

    def test_pieces_with_gap_are_not_contiguous(self):
        window = [Piece.RED, None, Piece.RED, None]
        assert _is_contiguous(window, Piece.RED) is False

    def test_scattered_across_window_is_not_contiguous(self):
        window = [Piece.RED, None, None, Piece.RED]
        assert _is_contiguous(window, Piece.RED) is False

    def test_three_adjacent_pieces_are_contiguous(self):
        window = [None, Piece.RED, Piece.RED, Piece.RED]
        assert _is_contiguous(window, Piece.RED) is True


class TestScoreWindowScatteredVsContiguous:
    def test_contiguous_two_scores_higher_than_scattered(self):
        # Contiguous: [R, R, None, None]
        contiguous = [Piece.RED, Piece.RED, None, None]
        # Scattered: [R, None, R, None]
        scattered = [Piece.RED, None, Piece.RED, None]
        assert _score_window(contiguous, Piece.RED, Piece.YELLOW) == 10.0
        assert _score_window(scattered, Piece.RED, Piece.YELLOW) == 2.0

    def test_scattered_two_still_scores_positive(self):
        scattered = [Piece.RED, None, Piece.RED, None]
        assert _score_window(scattered, Piece.RED, Piece.YELLOW) == 2.0

    def test_contiguous_opponent_two_scores_lower_than_scattered_opponent(self):
        # Contiguous opponent should be penalised more than a scattered opponent.
        contiguous_opp = [Piece.YELLOW, Piece.YELLOW, None, None]
        scattered_opp = [Piece.YELLOW, None, Piece.YELLOW, None]
        assert _score_window(contiguous_opp, Piece.RED, Piece.YELLOW) == -10.0
        assert _score_window(scattered_opp, Piece.RED, Piece.YELLOW) == -2.0

    def test_opponent_two_in_a_row_scores_negative(self):
        """Regression: previously opponent two-in-a-row returned 0, now it must be negative."""
        window = [Piece.YELLOW, Piece.YELLOW, None, None]
        assert _score_window(window, Piece.RED, Piece.YELLOW) == -10.0

    def test_opponent_scattered_two_scores_negative(self):
        window = [Piece.YELLOW, None, Piece.YELLOW, None]
        assert _score_window(window, Piece.RED, Piece.YELLOW) == -2.0
