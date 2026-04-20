from __future__ import annotations

import argparse
import importlib
import inspect
import logging
import sys
import typing

from connect4.game import Game
from connect4.renderer import TerminalRenderer
from connect4.types import Piece


def _load_player(tokens: list[str], renderer: TerminalRenderer):
    if not tokens:
        raise ValueError("Not enough players specified")

    token = tokens.pop(0).lower()
    try:
        module = importlib.import_module(f"connect4.players.{token}")
    except ModuleNotFoundError as e:
        raise ValueError(f"Unknown player type: '{token}'") from e

    class_name = token.title() + "Player"
    try:
        player_class = getattr(module, class_name)
    except AttributeError as e:
        raise ValueError(f"Could not find class {class_name} in connect4.players.{token}") from e

    sig = inspect.signature(player_class.__init__)
    hints = typing.get_type_hints(player_class.__init__)
    kwargs = {}

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        if name == "ui_delegate":
            kwargs[name] = renderer
            continue

        # Check if the annotation indicates an integer (handles int | None unions)
        hint = hints.get(name, param.annotation)
        args = typing.get_args(hint)
        is_int = hint is int or (len(args) > 0 and int in args)

        if is_int:
            if tokens and tokens[0].lstrip("-").isdigit():
                val_str = tokens.pop(0)
                kwargs[name] = int(val_str)
            elif param.default is not inspect.Parameter.empty:
                kwargs[name] = param.default
            else:
                raise ValueError(
                    f"Player '{token}' expects an integer for '{name}', but none was provided."
                )
            continue

        if param.default is not inspect.Parameter.empty:
            kwargs[name] = param.default

    return player_class(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Connect 4")
    parser.add_argument(
        "players",
        nargs="*",
        help="Sequence of two players (e.g. human, minimax 6) with their args",
    )
    args = parser.parse_args()

    if not args.players:
        args.players = ["human", "minimax"]

    tokens = list(args.players)

    logging.basicConfig(level=logging.WARNING)
    renderer = TerminalRenderer()

    try:
        red_player = _load_player(tokens, renderer)
        yellow_player = _load_player(tokens, renderer)
    except Exception as e:
        print(f"Error parsing players: {e}", file=sys.stderr)
        sys.exit(1)

    game = Game(red=red_player, yellow=yellow_player)

    # For display purposes, assume Red is P1 and Yellow is P2
    renderer.show_welcome(Piece.RED, Piece.YELLOW)
    renderer.show_board(game.board)

    # Note: TerminalRenderer.show_welcome mentions "You are RED".
    # This might look slightly off in bot vs bot, but matches original behavior.

    import time

    for state in game.play():
        renderer.show_move(state.piece, state.column, state.board)

        if state.winner:
            renderer.show_winner(state.winner)
            break
        elif state.is_draw:
            renderer.show_draw()
            break

        if not getattr(red_player, "is_interactive", False) and not getattr(yellow_player, "is_interactive", False):
            time.sleep(0.5)
