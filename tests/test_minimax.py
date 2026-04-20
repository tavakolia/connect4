from connect4.board import Board
from connect4.players.minimax import MinimaxPlayer
from connect4.types import Piece


class TestForcedWin:
    def test_takes_winning_move(self):
        """Bot must take column 3 to complete 4 in a row."""
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_takes_vertical_win(self):
        """Bot must take column 0 to complete vertical 4."""
        board = Board()
        for _ in range(3):
            board.drop(column=0, piece=Piece.RED)
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 0

    def test_takes_immediate_win_over_deep_win(self):
        """When multiple columns lead to wins, bot must take the immediate one.

        Regression: bot chose col 2 (forced win in several moves) over
        col 4 (immediate win) because both scored +inf and col 2 was
        explored first in center-out order.
        """
        board = Board()
        # Row 0: R R R Y R . .
        board.drop(0, Piece.RED)
        board.drop(1, Piece.RED)
        board.drop(2, Piece.RED)
        board.drop(3, Piece.YELLOW)
        board.drop(4, Piece.RED)
        # Row 1: R Y Y Y . . .
        board.drop(0, Piece.RED)
        board.drop(1, Piece.YELLOW)
        board.drop(2, Piece.YELLOW)
        board.drop(3, Piece.YELLOW)
        # Row 2: . . . Y . . .
        board.drop(3, Piece.YELLOW)
        # Row 3: . . . R . . .
        board.drop(3, Piece.RED)

        # Col 4 is an immediate win: row 1 becomes Y Y Y Y at cols 1-4
        player = MinimaxPlayer(depth=6)
        result = player.choose_column(board, Piece.YELLOW)
        assert result.column == 4


class TestForcedBlock:
    def test_blocks_opponent_win(self):
        """Opponent has 3 in a row at cols 0-2, bot must play col 3."""
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3


class TestMoveAnalysis:
    def test_analysis_returned(self):
        board = Board()
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.analysis is not None
        assert len(result.analysis) > 0

    def test_analysis_covers_valid_columns(self):
        board = Board()
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        analyzed_cols = {a.column for a in result.analysis}
        assert analyzed_cols == set(board.valid_columns())


class TestDepth:
    def test_deeper_search_finds_better_moves(self):
        """At depth 4, bot should find a winning setup."""
        board = Board()
        board.drop(column=0, piece=Piece.RED)
        board.drop(column=1, piece=Piece.RED)
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)

        player_deep = MinimaxPlayer(depth=4)
        result = player_deep.choose_column(board, Piece.RED)
        assert result.column in [2, 3]
