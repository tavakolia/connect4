from connect4.board import Board
from connect4.players.base import InteractivePlayer
from connect4.players.human import HumanPlayer
from connect4.types import Piece


class FakeUI:
    def __init__(self, inputs: list[str]):
        self._inputs = iter(inputs)
        self.errors = []

    def request_column(self, piece: Piece) -> str:
        return next(self._inputs)

    def show_error_invalid_input(self, raw: str) -> None:
        self.errors.append(("invalid_input", raw))

    def show_error_out_of_range(self, display_col: int) -> None:
        self.errors.append(("out_of_range", display_col))

    def show_error_column_full(self, display_col: int) -> None:
        self.errors.append(("column_full", display_col))


class TestHumanPlayer:
    def test_valid_input(self):
        ui = FakeUI(["4"])  # display col 4 → internal col 3
        player = HumanPlayer(ui_delegate=ui)
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3
        assert not ui.errors

    def test_retries_on_non_integer(self):
        ui = FakeUI(["abc", "4"])
        player = HumanPlayer(ui_delegate=ui)
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3
        assert ui.errors == [("invalid_input", "abc")]

    def test_retries_on_out_of_range(self):
        ui = FakeUI(["9", "-1", "0", "4"])
        player = HumanPlayer(ui_delegate=ui)
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3
        assert ui.errors == [
            ("out_of_range", 9),
            ("out_of_range", -1),
            ("out_of_range", 0),
        ]

    def test_retries_on_full_column(self):
        board = Board()
        for _ in range(Board.ROWS):
            board.drop(column=3, piece=Piece.RED)

        ui = FakeUI(["4", "5"])  # col 4 (internal 3) is full, col 5 (internal 4) works
        player = HumanPlayer(ui_delegate=ui)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 4
        assert ui.errors == [("column_full", 4)]

    def test_no_analysis(self):
        ui = FakeUI(["1"])  # display col 1 → internal col 0
        player = HumanPlayer(ui_delegate=ui)
        result = player.choose_column(Board(), Piece.RED)
        assert result.analysis is None

    def test_is_interactive(self):
        player = HumanPlayer(ui_delegate=FakeUI([]))
        assert isinstance(player, InteractivePlayer)
