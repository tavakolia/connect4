import pytest
from connect4.board import Board
from connect4.types import Piece


@pytest.fixture
def board():
    return Board()
