import pytest

from connect4.board import Board


@pytest.fixture
def board():
    return Board()
