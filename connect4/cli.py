from __future__ import annotations

import argparse
import logging

from connect4.game import Game
from connect4.players.human import HumanPlayer
from connect4.players.minimax import MinimaxPlayer
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
    human = HumanPlayer()
    bot = MinimaxPlayer(depth=args.depth)

    if args.play_as == "red":
        game = Game(red=human, yellow=bot)
    else:
        game = Game(red=bot, yellow=human)

    you_piece = Piece.RED if args.play_as == "red" else Piece.YELLOW
    bot_piece = you_piece.opponent
    print(f"Connect 4 — You are {you_piece.colored_name}, bot is {bot_piece.colored_name}")
    print(game.board)

    for state in game.play():
        print(f"\n{state.piece.colored_name} plays column {state.column + 1}")
        print(state.board)

        if state.winner:
            print(f"\n{state.winner.colored_name} wins!")
            break
        elif state.is_draw:
            print("\nIt's a draw!")
            break
