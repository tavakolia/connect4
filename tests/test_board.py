import pytest

from connect4.board import Board
from connect4.types import Piece


class TestBoardInit:
    def test_new_board_is_empty(self, board):
        for row in range(Board.ROWS):
            for col in range(Board.COLS):
                assert board._grid[row][col] is None

    def test_board_dimensions(self):
        assert Board.ROWS == 6
        assert Board.COLS == 7
        assert Board.CONNECT == 4


class TestDrop:
    def test_drop_lands_at_bottom(self, board):
        row = board.drop(column=3, piece=Piece.RED)
        assert row == 0
        assert board._grid[0][3] == Piece.RED

    def test_pieces_stack(self, board):
        board.drop(column=3, piece=Piece.RED)
        row = board.drop(column=3, piece=Piece.YELLOW)
        assert row == 1
        assert board._grid[1][3] == Piece.YELLOW

    def test_drop_returns_row(self, board):
        for i in range(Board.ROWS):
            row = board.drop(column=0, piece=Piece.RED)
            assert row == i

    def test_drop_full_column_raises(self, board):
        for _ in range(Board.ROWS):
            board.drop(column=0, piece=Piece.RED)
        with pytest.raises(ValueError, match="full"):
            board.drop(column=0, piece=Piece.RED)

    def test_drop_invalid_column_raises(self, board):
        with pytest.raises(ValueError, match="Invalid column"):
            board.drop(column=-1, piece=Piece.RED)
        with pytest.raises(ValueError, match="Invalid column"):
            board.drop(column=7, piece=Piece.RED)


class TestValidColumns:
    def test_all_columns_valid_on_empty_board(self, board):
        assert board.valid_columns() == [0, 1, 2, 3, 4, 5, 6]

    def test_full_column_not_valid(self, board):
        for _ in range(Board.ROWS):
            board.drop(column=0, piece=Piece.RED)
        assert 0 not in board.valid_columns()

    def test_is_valid_column(self, board):
        assert board.is_valid_column(3) is True
        for _ in range(Board.ROWS):
            board.drop(column=3, piece=Piece.RED)
        assert board.is_valid_column(3) is False


class TestIsFull:
    def test_empty_board_not_full(self, board):
        assert board.is_full() is False

    def test_full_board(self, board):
        for col in range(Board.COLS):
            for _row in range(Board.ROWS):
                board.drop(column=col, piece=Piece.RED)
        assert board.is_full() is True


class TestCopy:
    def test_copy_is_independent(self, board):
        board.drop(column=3, piece=Piece.RED)
        copy = board.copy()
        copy.drop(column=3, piece=Piece.YELLOW)
        assert board._grid[1][3] is None
        assert copy._grid[1][3] == Piece.YELLOW


class TestHasWinner:
    def test_no_winner_empty_board(self, board):
        assert board.has_winner(Piece.RED) is False

    def test_horizontal_win(self, board):
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_horizontal_win_middle(self, board):
        for col in range(2, 6):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_horizontal_win_right_edge(self, board):
        for col in range(3, 7):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_vertical_win(self, board):
        for _ in range(4):
            board.drop(column=3, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_vertical_win_top(self, board):
        board.drop(column=3, piece=Piece.YELLOW)
        board.drop(column=3, piece=Piece.YELLOW)
        for _ in range(4):
            board.drop(column=3, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_ne_win(self, board):
        board.drop(column=0, piece=Piece.RED)
        board.drop(column=1, piece=Piece.YELLOW)
        board.drop(column=1, piece=Piece.RED)
        board.drop(column=2, piece=Piece.YELLOW)
        board.drop(column=2, piece=Piece.YELLOW)
        board.drop(column=2, piece=Piece.RED)
        board.drop(column=3, piece=Piece.YELLOW)
        board.drop(column=3, piece=Piece.YELLOW)
        board.drop(column=3, piece=Piece.YELLOW)
        board.drop(column=3, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_nw_win(self, board):
        board.drop(column=3, piece=Piece.RED)
        board.drop(column=2, piece=Piece.YELLOW)
        board.drop(column=2, piece=Piece.RED)
        board.drop(column=1, piece=Piece.YELLOW)
        board.drop(column=1, piece=Piece.YELLOW)
        board.drop(column=1, piece=Piece.RED)
        board.drop(column=0, piece=Piece.YELLOW)
        board.drop(column=0, piece=Piece.YELLOW)
        board.drop(column=0, piece=Piece.YELLOW)
        board.drop(column=0, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_win_at_edge(self, board):
        board.drop(column=3, piece=Piece.RED)
        board.drop(column=4, piece=Piece.YELLOW)
        board.drop(column=4, piece=Piece.RED)
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=5, piece=Piece.RED)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_three_in_a_row_not_winner(self, board):
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is False

    def test_wrong_piece_not_winner(self, board):
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.YELLOW) is False


class TestIsWinnerAt:
    def test_horizontal_win_at(self, board):
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        assert board.is_winner_at(0, 3, Piece.RED) is True

    def test_no_win_at(self, board):
        board.drop(column=0, piece=Piece.RED)
        assert board.is_winner_at(0, 0, Piece.RED) is False

    def test_diagonal_win_at(self, board):
        # Build NE diagonal
        board.drop(0, Piece.RED)
        board.drop(1, Piece.YELLOW); board.drop(1, Piece.RED)
        board.drop(2, Piece.YELLOW); board.drop(2, Piece.YELLOW); board.drop(2, Piece.RED)
        board.drop(3, Piece.YELLOW); board.drop(3, Piece.YELLOW); board.drop(3, Piece.YELLOW)
        board.drop(3, Piece.RED)
        assert board.is_winner_at(3, 3, Piece.RED) is True


class TestUndo:
    def test_undo_removes_top_piece(self, board):
        board.drop(column=3, piece=Piece.RED)
        board.drop(column=3, piece=Piece.YELLOW)
        board.undo(column=3)
        assert board._grid[1][3] is None
        assert board._grid[0][3] == Piece.RED

    def test_undo_empty_column_raises(self, board):
        with pytest.raises(ValueError, match="empty"):
            board.undo(column=0)

    def test_drop_undo_roundtrip(self, board):
        board.drop(column=3, piece=Piece.RED)
        board.undo(column=3)
        assert board._grid[0][3] is None


class TestRepr:
    def test_repr_empty_board(self, board):
        s = repr(board)
        assert "1" in s
        assert "7" in s
        # All cells should be empty dots
        assert "." in s
        assert "R" not in s
        assert "Y" not in s

    def test_repr_shows_pieces(self, board):
        board.drop(column=3, piece=Piece.RED)
        s = repr(board)
        assert "R" in s

    def test_repr_shows_both_pieces(self, board):
        board.drop(column=0, piece=Piece.RED)
        board.drop(column=1, piece=Piece.YELLOW)
        s = repr(board)
        assert "R" in s
        assert "Y" in s
