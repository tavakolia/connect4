from __future__ import annotations

import logging

from connect4.game import Game
from connect4.players.human import HumanPlayer
from connect4.players.minimax import MinimaxPlayer


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    red = HumanPlayer()
    yellow = MinimaxPlayer()
    game = Game(red=red, yellow=yellow)

    print("Connect 4 — You are RED, bot is YELLOW")
    print(game.board)

    for state in game.play():
        print(f"\n{state.piece.name} plays column {state.column}")
        print(game.board)

        if state.winner:
            print(f"\n{state.winner.name} wins!")
            break
        elif state.is_draw:
            print("\nIt's a draw!")
            break
