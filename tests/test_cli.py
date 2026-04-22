from unittest.mock import MagicMock

import pytest

from connect4.cli import _load_player
from connect4.players.base import InteractivePlayer
from connect4.players.greedy import GreedyPlayer
from connect4.players.human import HumanPlayer
from connect4.players.minimax import MinimaxPlayer
from connect4.players.random import RandomPlayer
from connect4.renderer import TerminalRenderer


def test_load_player_human():
    renderer = MagicMock(spec=TerminalRenderer)
    tokens = ["human"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, HumanPlayer)
    # Check that UI delegate injection worked
    assert player._ui == renderer
    assert len(tokens) == 0


def test_load_player_minimax_with_depth():
    renderer = MagicMock(spec=TerminalRenderer)
    # "4" should be consumed, leaving "greedy" in the tokens list
    tokens = ["minimax", "4", "greedy"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, MinimaxPlayer)
    assert player.depth == 4
    assert tokens == ["greedy"]


def test_load_player_minimax_default_depth():
    renderer = MagicMock(spec=TerminalRenderer)
    # "minimax" finds no number next, defaults to 6, leaves "greedy" untouched
    tokens = ["minimax", "greedy"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, MinimaxPlayer)
    assert player.depth == 6
    assert tokens == ["greedy"]


def test_load_player_greedy():
    renderer = MagicMock(spec=TerminalRenderer)
    tokens = ["greedy"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, GreedyPlayer)
    assert len(tokens) == 0


def test_load_unknown_player():
    renderer = MagicMock(spec=TerminalRenderer)
    tokens = ["idonotexist"]
    with pytest.raises(ValueError, match="Unknown player type"):
        _load_player(tokens, renderer)


def test_load_player_missing_tokens():
    renderer = MagicMock(spec=TerminalRenderer)
    tokens = []
    with pytest.raises(ValueError, match="Not enough players specified"):
        _load_player(tokens, renderer)


def test_load_player_random_with_seed():
    renderer = MagicMock(spec=TerminalRenderer)
    # "42" should be consumed as the seed (int | None annotation), leaving "human" untouched
    tokens = ["random", "42", "human"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, RandomPlayer)
    assert tokens == ["human"]


def test_load_player_greedy_with_seed():
    renderer = MagicMock(spec=TerminalRenderer)
    # "7" should be consumed as the seed (int | None annotation), leaving "human" untouched
    tokens = ["greedy", "7", "human"]
    player = _load_player(tokens, renderer)
    assert isinstance(player, GreedyPlayer)
    assert tokens == ["human"]


def test_bot_players_are_not_interactive():
    for player in (RandomPlayer(), GreedyPlayer(), MinimaxPlayer()):
        assert not isinstance(player, InteractivePlayer), (
            f"{type(player).__name__} should not be interactive"
        )
