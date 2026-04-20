"""Known-position tests for minimax correctness.

Each test sets up a board state where the objectively correct move is known,
then verifies the bot finds it. This is the standard technique for validating
game-playing algorithms — equivalent to regression tests against a solved game.

Board setup helper: _build_board() takes a list of columns played in order
(alternating RED then YELLOW), returning the resulting board state.
"""

from connect4.board import Board
from connect4.players.minimax import MinimaxPlayer
from connect4.types import Piece


def _build_board(moves: list[int]) -> Board:
    """Play a sequence of moves (alternating RED/YELLOW) and return the board."""
    board = Board()
    pieces = [Piece.RED, Piece.YELLOW]
    for i, col in enumerate(moves):
        board.drop(col, pieces[i % 2])
    return board


class TestWinInOne:
    """Bot has an immediate winning move available."""

    def test_horizontal_win_left(self):
        # RED has pieces at cols 0,1,2 on row 0. Must play col 3.
        board = _build_board([0, 6, 1, 6, 2])  # R:0,1,2  Y:6,6
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_horizontal_win_right(self):
        # RED has pieces at cols 4,5,6 on row 0. Must play col 3.
        board = _build_board([4, 0, 5, 0, 6])  # R:4,5,6  Y:0,0
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_horizontal_win_gap(self):
        # RED at cols 0,1,3 on row 0 (gap at col 2). Must play col 2.
        board = _build_board([0, 6, 1, 6, 3])  # R:0,1,3  Y:6,6
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 2

    def test_vertical_win(self):
        # RED has 3 stacked in col 3. Must play col 3.
        board = _build_board([3, 0, 3, 0, 3])  # R:3,3,3  Y:0,0
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_diagonal_win(self):
        # Build a diagonal ↗ with RED at (0,0),(1,1),(2,2), needs (3,3)
        board = _build_board([
            0,  # R at (0,0)
            1,  # Y at (0,1)
            1,  # R at (1,1)
            2,  # Y at (0,2)
            2,  # R at (1,2)
            3,  # Y at (0,3)
            2,  # R at (2,2)
            3,  # Y at (1,3)
            3,  # R at (2,3)
            6,  # Y at (0,6)
        ])
        # RED needs to play col 3 to get (3,3) for the diagonal win
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3


class TestBlockOrLose:
    """Opponent has an immediate winning threat. Must block."""

    def test_block_horizontal(self):
        # YELLOW has cols 0,1,2 on row 0. RED must play col 3 to block.
        board = _build_board([6, 0, 6, 1, 5, 2])  # Y:0,1,2 on row 0
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_block_vertical(self):
        # YELLOW has 3 stacked in col 3. RED must play col 3 to block.
        board = _build_board([0, 3, 0, 3, 1, 3])  # Y: 3,3,3
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_prefer_win_over_block(self):
        # RED can win at col 0, YELLOW threatens at col 6. RED must win, not block.
        board = Board()
        # RED: 3 in a row at cols 1,2,3 on row 0
        board.drop(1, Piece.RED)
        board.drop(2, Piece.RED)
        board.drop(3, Piece.RED)
        # YELLOW: 3 in a row at cols 4,5,6 on row 0
        board.drop(4, Piece.YELLOW)
        board.drop(5, Piece.YELLOW)
        board.drop(6, Piece.YELLOW)
        # RED should play col 0 to win (not col 3 which is already occupied)
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 0


class TestWinInTwo:
    """Bot must set up a double threat (two ways to win) that opponent can't block both."""

    def test_fork_setup(self):
        # RED has R at (0,1) and (0,2). Playing col 3 creates threats at both
        # col 0 (horizontal) and col 4 (horizontal). Opponent can only block one.
        board = Board()
        board.drop(1, Piece.RED)
        board.drop(2, Piece.RED)
        # YELLOW scattered elsewhere
        board.drop(5, Piece.YELLOW)
        board.drop(6, Piece.YELLOW)
        # At depth 4, bot should find the winning setup
        player = MinimaxPlayer(depth=4)
        result = player.choose_column(board, Piece.RED)
        # Should play to create a double threat — col 0 or col 3
        assert result.column in [0, 3]


class TestOpeningMoves:
    """First move should always be center column (strongest opening)."""

    def test_first_move_is_center(self):
        board = Board()
        player = MinimaxPlayer(depth=4)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3  # center (0-indexed)

    def test_response_to_center_is_center(self):
        # If RED plays center, YELLOW's best response is also center (stack)
        # or an adjacent column. At minimum, should not play an edge.
        board = Board()
        board.drop(3, Piece.RED)  # RED plays center
        player = MinimaxPlayer(depth=4)
        result = player.choose_column(board, Piece.YELLOW)
        assert result.column in [2, 3, 4]  # center or adjacent


class TestTrapPositions:
    """Positions where only one move avoids losing."""

    def test_must_not_set_up_opponent_win(self):
        """Don't play a column if it lets the opponent win on the next move.

        YELLOW has 3 vertical in col 3 (rows 0,1,2). Col 3 row 3 is empty.
        If RED plays col 3, RED gets row 3 — but then YELLOW plays col 3
        and gets row 4 with no win. But we can construct a case where
        RED giving YELLOW a landing spot completes a horizontal.

        Setup: YELLOW has (0,1),(0,2),(0,3) — 3 horizontal on row 0.
        Col 0 is empty. If RED plays col 0, it lands at row 0 and blocks.
        But if RED plays somewhere else, YELLOW wins at col 0.
        RED *must* play col 0.
        """
        board = Board()
        board.drop(1, Piece.YELLOW)
        board.drop(2, Piece.YELLOW)
        board.drop(3, Piece.YELLOW)
        # RED has random pieces elsewhere to not be turn 1
        board.drop(4, Piece.RED)
        board.drop(6, Piece.RED)
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        # Must block at col 0
        assert result.column == 0


class TestLateGame:
    """Near-endgame positions where deep search matters."""

    def test_finds_win_in_nearly_full_board(self):
        """With few columns left, bot should find the winning move."""
        board = Board()
        # Fill most of the board leaving a winning opportunity
        # Cols 0-4 filled, col 5 has 5 pieces, col 6 has 5 pieces
        # RED can win by playing col 5 or col 6
        for col in range(5):
            for row in range(Board.ROWS):
                piece = Piece.RED if (col + row) % 2 == 0 else Piece.YELLOW
                board.drop(col, piece)

        # Col 5: alternate pieces, 5 high
        for i in range(5):
            board.drop(5, Piece.YELLOW if i % 2 == 0 else Piece.RED)

        # Col 6: alternate pieces, 5 high
        for i in range(5):
            board.drop(6, Piece.RED if i % 2 == 0 else Piece.YELLOW)

        # Bot should find a valid move in the remaining spots
        player = MinimaxPlayer(depth=6)
        result = player.choose_column(board, Piece.RED)
        assert result.column in [5, 6]  # only valid columns
        # Verify it actually produces a win
        clone = board.copy()
        clone.drop(result.column, Piece.RED)
        assert clone.has_winner(Piece.RED)
