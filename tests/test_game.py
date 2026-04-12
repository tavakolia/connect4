from connect4.board import Board
from connect4.game import Game
from connect4.players.random import RandomPlayer
from connect4.types import MoveResult, Piece


class _FixedPlayer:
    """Player that plays a predetermined sequence of columns."""
    def __init__(self, columns: list[int]):
        self._columns = iter(columns)

    def choose_column(self, board, piece):
        return MoveResult(column=next(self._columns))


class TestGameFlow:
    def test_red_goes_first(self):
        game = Game(red=RandomPlayer(seed=1), yellow=RandomPlayer(seed=2))
        state = next(game.play())
        assert state.piece == Piece.RED

    def test_players_alternate(self):
        game = Game(red=RandomPlayer(seed=1), yellow=RandomPlayer(seed=2))
        pieces = []
        for state in game.play():
            pieces.append(state.piece)
            if len(pieces) >= 4:
                break
        assert pieces[:4] == [Piece.RED, Piece.YELLOW, Piece.RED, Piece.YELLOW]

    def test_game_ends_on_win(self):
        red = _FixedPlayer([0, 0, 0, 0])
        yellow = _FixedPlayer([1, 1, 1])
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        final = states[-1]
        assert final.winner == Piece.RED
        assert final.is_draw is False

    def test_game_ends_on_draw(self):
        # Build a draw by filling board with no 4-in-a-row.
        # Target board (bottom=row 0): even cols get R in rows 0-2 then Y in rows 3-5,
        # odd cols get Y in rows 0-2 then R in rows 3-5.
        # These sequences were computed by greedily assigning each alternating turn
        # to the leftmost column whose next slot matches the current piece.
        sequence_red = [0, 0, 0, 2, 2, 2, 1, 1, 1, 4, 4, 4, 3, 3, 3, 6, 6, 6, 5, 5, 5]
        sequence_yellow = [1, 1, 0, 0, 0, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6]

        red = _FixedPlayer(sequence_red)
        yellow = _FixedPlayer(sequence_yellow)
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        final = states[-1]
        assert final.winner is None
        assert final.is_draw is True
        assert len(states) == 42

    def test_winner_state_has_winner_set(self):
        red = _FixedPlayer([0, 0, 0, 0])
        yellow = _FixedPlayer([1, 1, 1])
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        winners = [s for s in states if s.winner is not None]
        assert len(winners) == 1
        assert winners[0].winner == Piece.RED

    def test_analysis_flows_through(self):
        from connect4.players.minimax import MinimaxPlayer
        game = Game(red=MinimaxPlayer(depth=1), yellow=RandomPlayer(seed=1))
        state = next(game.play())
        assert state.analysis is not None
