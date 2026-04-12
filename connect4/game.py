from __future__ import annotations

from collections.abc import Generator

from connect4.board import Board
from connect4.players.base import Player
from connect4.types import GameState, Piece


class Game:
    def __init__(self, red: Player, yellow: Player) -> None:
        self.board = Board()
        self.players = {Piece.RED: red, Piece.YELLOW: yellow}

    def play(self) -> Generator[GameState, None, None]:
        current = Piece.RED

        while True:
            player = self.players[current]
            result = player.choose_column(self.board, current)
            self.board.drop(result.column, current)

            winner = current if self.board.has_winner(current) else None
            is_draw = winner is None and self.board.is_full()

            yield GameState(
                board=self.board.copy(),
                piece=current,
                column=result.column,
                winner=winner,
                is_draw=is_draw,
                analysis=result.analysis,
            )

            if winner or is_draw:
                return

            current = current.opponent
