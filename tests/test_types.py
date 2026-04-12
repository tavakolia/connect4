# tests/test_types.py
from connect4.types import Piece, MoveResult, MoveAnalysis


class TestPiece:
    def test_red_opponent_is_yellow(self):
        assert Piece.RED.opponent == Piece.YELLOW

    def test_yellow_opponent_is_red(self):
        assert Piece.YELLOW.opponent == Piece.RED

    def test_piece_values(self):
        assert Piece.RED.value == "R"
        assert Piece.YELLOW.value == "Y"


class TestMoveResult:
    def test_move_result_without_analysis(self):
        result = MoveResult(column=3)
        assert result.column == 3
        assert result.analysis is None

    def test_move_result_with_analysis(self):
        analysis = [MoveAnalysis(column=3, score=10.0, depth_reached=6)]
        result = MoveResult(column=3, analysis=analysis)
        assert result.analysis == analysis

    def test_move_result_is_frozen(self):
        import dataclasses
        result = MoveResult(column=3)
        try:
            result.column = 5
            assert False, "Should have raised"
        except dataclasses.FrozenInstanceError:
            pass
