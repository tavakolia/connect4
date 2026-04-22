import pytest

from connect4.board import Board
from connect4.game import Game
from connect4.players.greedy import GreedyPlayer
from connect4.players.minimax import MinimaxPlayer
from connect4.players.random import RandomPlayer
from connect4.types import Piece


class TestBotVsRandom:
    def test_minimax_beats_random_overwhelmingly(self):
        """MinimaxPlayer should win >95% against RandomPlayer."""
        wins = 0
        games = 100
        for seed in range(games):
            game = Game(
                red=MinimaxPlayer(depth=4),
                yellow=RandomPlayer(seed=seed),
            )
            for state in game.play():
                if state.winner == Piece.RED:
                    wins += 1
                    break
        win_rate = wins / games
        print(f"\n  Minimax vs Random: {wins}/{games} wins ({win_rate:.0%})")
        assert win_rate > 0.95, f"Win rate {win_rate:.0%} is below 95%"


class TestBotVsGreedy:
    def test_minimax_beats_greedy(self):
        """MinimaxPlayer should win >80% against GreedyPlayer."""
        wins = 0
        games = 100
        for seed in range(games):
            game = Game(
                red=MinimaxPlayer(depth=4),
                yellow=GreedyPlayer(seed=seed),
            )
            for state in game.play():
                if state.winner == Piece.RED:
                    wins += 1
                    break
        win_rate = wins / games
        print(f"\n  Minimax vs Greedy: {wins}/{games} wins ({win_rate:.0%})")
        assert win_rate > 0.80, f"Win rate {win_rate:.0%} is below 80%"

class TestGameInvariants:
    """Property-based tests: invariants that hold for any valid game."""

    def _play_full_game(self, seed: int) -> list:
        game = Game(
            red=RandomPlayer(seed=seed),
            yellow=RandomPlayer(seed=seed + 1000),
        )
        return list(game.play())

    @pytest.mark.parametrize("seed", range(50))
    def test_piece_count_balance(self, seed):
        """After each move, |red_count - yellow_count| <= 1."""
        states = self._play_full_game(seed)
        for state in states:
            red = sum(
                1
                for r in range(Board.ROWS)
                for c in range(Board.COLS)
                if state.board._grid[r][c] == Piece.RED
            )
            yellow = sum(
                1
                for r in range(Board.ROWS)
                for c in range(Board.COLS)
                if state.board._grid[r][c] == Piece.YELLOW
            )
            assert abs(red - yellow) <= 1

    @pytest.mark.parametrize("seed", range(50))
    def test_no_floating_pieces(self, seed):
        """Every piece must rest on the bottom or another piece."""
        states = self._play_full_game(seed)
        for state in states:
            for row in range(Board.ROWS):
                for col in range(Board.COLS):
                    if state.board._grid[row][col] is not None and row > 0:
                        assert state.board._grid[row - 1][col] is not None

    @pytest.mark.parametrize("seed", range(50))
    def test_game_length(self, seed):
        """A game has at most 42 moves."""
        states = self._play_full_game(seed)
        assert len(states) <= 42

    @pytest.mark.parametrize("seed", range(50))
    def test_at_most_one_winner(self, seed):
        """Only one state should have a winner."""
        states = self._play_full_game(seed)
        winners = [s for s in states if s.winner is not None]
        assert len(winners) <= 1

    @pytest.mark.parametrize("seed", range(50))
    def test_winner_actually_won(self, seed):
        """If a winner is declared, the winning line exists on the board."""
        states = self._play_full_game(seed)
        for state in states:
            if state.winner:
                assert state.board.has_winner(state.winner)
