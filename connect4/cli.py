from __future__ import annotations

import argparse
import logging

from connect4.game import Game
from connect4.players.human import HumanPlayer
from connect4.players.minimax import MinimaxPlayer
from connect4.renderer import TerminalRenderer
from connect4.types import Piece


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Connect 4 against a bot")
    parser.add_argument(
        "--play-as", choices=["red", "yellow"], default="red",
        help="Which color to play as (default: red, moves first)",
    )
    parser.add_argument(
        "--depth", type=int, default=6,
        help="Bot search depth (default: 6)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    renderer = TerminalRenderer()
    human = HumanPlayer(ui_delegate=renderer)
    bot = MinimaxPlayer(depth=args.depth)

    if args.play_as == "red":
        game = Game(red=human, yellow=bot)
    else:
        game = Game(red=bot, yellow=human)

    you_piece = Piece.RED if args.play_as == "red" else Piece.YELLOW
    bot_piece = you_piece.opponent
    renderer.show_welcome(you_piece, bot_piece)
    renderer.show_board(game.board)

    for state in game.play():
        renderer.show_move(state.piece, state.column, state.board)

        if state.winner:
            renderer.show_winner(state.winner)
            break
        elif state.is_draw:
            renderer.show_draw()
            break

