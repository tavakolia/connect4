# Connect 4 Implementation Plan

**Goal:** Build a Connect 4 Python module with a minimax bot that beats casual players, a terminal CLI, and comprehensive tests.

**Architecture:** Three-layer design — core engine (Board + types), player layer (protocol + implementations), orchestration + UI (Game + CLI). TDD throughout: write failing test → implement → pass → commit.

**Tech Stack:** Python 3.10+, pytest, standard library only.

**Spec:** `docs/design.md`

---

## File Map

| File | Responsibility | Created in Task |
|------|---------------|-----------------|
| `connect4/__init__.py` | Public API barrel exports | 1 |
| `connect4/types.py` | Piece enum, GameState, MoveAnalysis, MoveResult | 1 |
| `connect4/board.py` | Board state, drop, win/draw detection | 2 |
| `connect4/players/__init__.py` | Player exports barrel | 3 |
| `connect4/players/base.py` | Player protocol | 3 |
| `connect4/players/random.py` | RandomPlayer (seeded RNG) | 3 |
| `connect4/evaluation.py` | Board evaluation heuristic (pure function) | 4 |
| `connect4/players/minimax.py` | MinimaxPlayer with alpha-beta | 5 |
| `connect4/players/greedy.py` | GreedyPlayer (one-ply) | 6 |
| `connect4/game.py` | Game orchestrator (generator) | 7 |
| `connect4/players/human.py` | HumanPlayer (stdin) | 8 |
| `connect4/cli.py` | Terminal entry point | 8 |
| `connect4/__main__.py` | `python -m connect4` hook | 8 |
| `tests/test_board.py` | Board unit tests | 2 |
| `tests/test_evaluation.py` | Evaluation unit tests | 4 |
| `tests/test_minimax.py` | Minimax integration tests | 5 |
| `tests/test_game.py` | Game flow tests | 7 |
| `tests/test_bot_strength.py` | Statistical + perf tests | 9 |
| `tests/conftest.py` | Shared pytest fixtures | 2 |
| `pyproject.toml` | Project config + pytest settings | 1 |

---

### Task 1: Project Scaffolding + Core Types

**Files:**
- Create: `pyproject.toml`
- Create: `connect4/__init__.py`
- Create: `connect4/types.py`
- Create: `tests/__init__.py`
- Create: `tests/test_types.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "connect4"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `connect4/types.py` with Piece enum and dataclasses**

```python
from __future__ import annotations

import enum
import dataclasses


class Piece(enum.Enum):
    RED = "R"
    YELLOW = "Y"

    @property
    def opponent(self) -> Piece:
        return Piece.YELLOW if self == Piece.RED else Piece.RED


@dataclasses.dataclass(frozen=True)
class MoveAnalysis:
    column: int
    score: float
    depth_reached: int


@dataclasses.dataclass(frozen=True)
class MoveResult:
    column: int
    analysis: list[MoveAnalysis] | None = None


@dataclasses.dataclass(frozen=True)
class GameState:
    board: object  # Board (avoid circular import)
    piece: Piece
    column: int
    winner: Piece | None
    is_draw: bool
    analysis: list[MoveAnalysis] | None = None
```

- [ ] **Step 3: Create `connect4/__init__.py` barrel**

```python
from connect4.types import Piece, GameState, MoveAnalysis, MoveResult

__all__ = ["Piece", "GameState", "MoveAnalysis", "MoveResult"]
```

Note: `Board`, `Game`, and `Player` will be added to `__init__.py` as they're created.

- [ ] **Step 4: Create `tests/__init__.py`** (empty file)

- [ ] **Step 5: Write test for Piece enum**

```python
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
```

- [ ] **Step 6: Run tests**

Run: `python -m pytest tests/test_types.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml connect4/__init__.py connect4/types.py tests/__init__.py tests/test_types.py
git commit -m "feat: add project scaffolding and core types (Piece, MoveResult, GameState)"
```

---

### Task 2: Board — State, Drop, Win Detection

**Files:**
- Create: `connect4/board.py`
- Create: `tests/test_board.py`
- Create: `tests/conftest.py`
- Modify: `connect4/__init__.py`

- [ ] **Step 1: Write failing tests for Board basics**

```python
# tests/conftest.py
import pytest
from connect4.board import Board
from connect4.types import Piece


@pytest.fixture
def board():
    return Board()
```

```python
# tests/test_board.py
import pytest
from connect4.board import Board
from connect4.types import Piece


class TestBoardInit:
    def test_new_board_is_empty(self, board):
        for row in range(Board.ROWS):
            for col in range(Board.COLS):
                assert board._grid[row][col] is None

    def test_board_dimensions(self):
        assert Board.ROWS == 6
        assert Board.COLS == 7
        assert Board.CONNECT == 4


class TestDrop:
    def test_drop_lands_at_bottom(self, board):
        row = board.drop(column=3, piece=Piece.RED)
        assert row == 0
        assert board._grid[0][3] == Piece.RED

    def test_pieces_stack(self, board):
        board.drop(column=3, piece=Piece.RED)
        row = board.drop(column=3, piece=Piece.YELLOW)
        assert row == 1
        assert board._grid[1][3] == Piece.YELLOW

    def test_drop_returns_row(self, board):
        for i in range(Board.ROWS):
            row = board.drop(column=0, piece=Piece.RED)
            assert row == i

    def test_drop_full_column_raises(self, board):
        for _ in range(Board.ROWS):
            board.drop(column=0, piece=Piece.RED)
        with pytest.raises(ValueError, match="full"):
            board.drop(column=0, piece=Piece.RED)

    def test_drop_invalid_column_raises(self, board):
        with pytest.raises(ValueError, match="Invalid column"):
            board.drop(column=-1, piece=Piece.RED)
        with pytest.raises(ValueError, match="Invalid column"):
            board.drop(column=7, piece=Piece.RED)


class TestValidColumns:
    def test_all_columns_valid_on_empty_board(self, board):
        assert board.valid_columns() == [0, 1, 2, 3, 4, 5, 6]

    def test_full_column_not_valid(self, board):
        for _ in range(Board.ROWS):
            board.drop(column=0, piece=Piece.RED)
        assert 0 not in board.valid_columns()

    def test_is_valid_column(self, board):
        assert board.is_valid_column(3) is True
        for _ in range(Board.ROWS):
            board.drop(column=3, piece=Piece.RED)
        assert board.is_valid_column(3) is False


class TestIsFull:
    def test_empty_board_not_full(self, board):
        assert board.is_full() is False

    def test_full_board(self, board):
        # Fill entire board
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                board.drop(column=col, piece=Piece.RED)
        assert board.is_full() is True


class TestCopy:
    def test_copy_is_independent(self, board):
        board.drop(column=3, piece=Piece.RED)
        copy = board.copy()
        copy.drop(column=3, piece=Piece.YELLOW)
        # Original unchanged
        assert board._grid[1][3] is None
        # Copy has the new piece
        assert copy._grid[1][3] == Piece.YELLOW
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_board.py -v`
Expected: FAIL (Board not defined yet)

- [ ] **Step 3: Implement Board basics (init, drop, valid_columns, is_full, copy)**

```python
# connect4/board.py
from __future__ import annotations

import copy as copy_module

from connect4.types import Piece


class Board:
    ROWS = 6
    COLS = 7
    CONNECT = 4

    def __init__(self) -> None:
        self._grid: list[list[Piece | None]] = [
            [None] * self.COLS for _ in range(self.ROWS)
        ]

    def drop(self, column: int, piece: Piece) -> int:
        """Drop a piece into the given column. Returns the row it landed in."""
        if column < 0 or column >= self.COLS:
            raise ValueError(f"Invalid column: {column}. Must be 0-{self.COLS - 1}")
        for row in range(self.ROWS):
            if self._grid[row][column] is None:
                self._grid[row][column] = piece
                return row
        raise ValueError(f"Column {column} is full")

    def is_valid_column(self, column: int) -> bool:
        return 0 <= column < self.COLS and self._grid[self.ROWS - 1][column] is None

    def valid_columns(self) -> list[int]:
        return [col for col in range(self.COLS) if self.is_valid_column(col)]

    def is_full(self) -> bool:
        return all(self._grid[self.ROWS - 1][col] is not None for col in range(self.COLS))

    def copy(self) -> Board:
        new_board = Board()
        new_board._grid = [row[:] for row in self._grid]
        return new_board
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_board.py -v`
Expected: All PASS

- [ ] **Step 5: Write failing tests for win detection**

Add to `tests/test_board.py`:

```python
class TestHasWinner:
    def test_no_winner_empty_board(self, board):
        assert board.has_winner(Piece.RED) is False

    def test_horizontal_win(self, board):
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_horizontal_win_middle(self, board):
        for col in range(2, 6):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_horizontal_win_right_edge(self, board):
        for col in range(3, 7):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_vertical_win(self, board):
        for _ in range(4):
            board.drop(column=3, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_vertical_win_top(self, board):
        # Fill 2 non-winning, then 4 winning
        board.drop(column=3, piece=Piece.YELLOW)
        board.drop(column=3, piece=Piece.YELLOW)
        for _ in range(4):
            board.drop(column=3, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_ne_win(self, board):
        # Build a NE diagonal (↗): (0,0), (1,1), (2,2), (3,3)
        # Need to stack pieces to reach the right rows
        board.drop(column=0, piece=Piece.RED)      # (0,0)
        board.drop(column=1, piece=Piece.YELLOW)    # (0,1) padding
        board.drop(column=1, piece=Piece.RED)       # (1,1)
        board.drop(column=2, piece=Piece.YELLOW)    # (0,2) padding
        board.drop(column=2, piece=Piece.YELLOW)    # (1,2) padding
        board.drop(column=2, piece=Piece.RED)       # (2,2)
        board.drop(column=3, piece=Piece.YELLOW)    # (0,3) padding
        board.drop(column=3, piece=Piece.YELLOW)    # (1,3) padding
        board.drop(column=3, piece=Piece.YELLOW)    # (2,3) padding
        board.drop(column=3, piece=Piece.RED)       # (3,3)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_nw_win(self, board):
        # Build a NW diagonal (↘): (3,0), (2,1), (1,2), (0,3)
        board.drop(column=3, piece=Piece.RED)       # (0,3)
        board.drop(column=2, piece=Piece.YELLOW)    # (0,2) padding
        board.drop(column=2, piece=Piece.RED)       # (1,2)
        board.drop(column=1, piece=Piece.YELLOW)    # (0,1) padding
        board.drop(column=1, piece=Piece.YELLOW)    # (1,1) padding
        board.drop(column=1, piece=Piece.RED)       # (2,1)
        board.drop(column=0, piece=Piece.YELLOW)    # (0,0) padding
        board.drop(column=0, piece=Piece.YELLOW)    # (1,0) padding
        board.drop(column=0, piece=Piece.YELLOW)    # (2,0) padding
        board.drop(column=0, piece=Piece.RED)       # (3,0)
        assert board.has_winner(Piece.RED) is True

    def test_diagonal_win_at_edge(self, board):
        # Diagonal starting at bottom-right area
        board.drop(column=3, piece=Piece.RED)       # (0,3)
        board.drop(column=4, piece=Piece.YELLOW)
        board.drop(column=4, piece=Piece.RED)       # (1,4)
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=5, piece=Piece.RED)       # (2,5)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.RED)       # (3,6)
        assert board.has_winner(Piece.RED) is True

    def test_three_in_a_row_not_winner(self, board):
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.RED) is False

    def test_wrong_piece_not_winner(self, board):
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        assert board.has_winner(Piece.YELLOW) is False


class TestStr:
    def test_str_empty_board(self, board):
        s = str(board)
        assert "0" in s  # column numbers
        assert "6" in s

    def test_str_shows_pieces(self, board):
        board.drop(column=3, piece=Piece.RED)
        s = str(board)
        assert "R" in s
```

- [ ] **Step 6: Run tests to verify the new ones fail**

Run: `python -m pytest tests/test_board.py::TestHasWinner -v`
Expected: FAIL (has_winner not implemented)

- [ ] **Step 7: Implement has_winner and __str__**

Add to `Board` class in `connect4/board.py`:

```python
    def has_winner(self, piece: Piece) -> bool:
        """Check if the given piece has four in a row."""
        # Direction vectors: (row_delta, col_delta)
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diag↗, diag↘

        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self._grid[row][col] != piece:
                    continue
                for dr, dc in directions:
                    if self._check_line(row, col, dr, dc, piece):
                        return True
        return False

    def _check_line(self, row: int, col: int, dr: int, dc: int, piece: Piece) -> bool:
        """Check if there are CONNECT pieces in a line starting at (row, col)."""
        for i in range(self.CONNECT):
            r = row + i * dr
            c = col + i * dc
            if r < 0 or r >= self.ROWS or c < 0 or c >= self.COLS:
                return False
            if self._grid[r][c] != piece:
                return False
        return True

    def __str__(self) -> str:
        lines = []
        for row in range(self.ROWS - 1, -1, -1):
            cells = []
            for col in range(self.COLS):
                piece = self._grid[row][col]
                cells.append(piece.value if piece else ".")
            lines.append("| " + "  ".join(cells) + " |")
        lines.append("  " + "  ".join(str(i) for i in range(self.COLS)) + "  ")
        return "\n".join(lines)
```

- [ ] **Step 8: Run all board tests**

Run: `python -m pytest tests/test_board.py -v`
Expected: All PASS

- [ ] **Step 9: Update `connect4/__init__.py`**

Add Board to the barrel:
```python
from connect4.board import Board
# update __all__ to include "Board"
```

- [ ] **Step 10: Commit**

```bash
git add connect4/board.py connect4/__init__.py tests/conftest.py tests/test_board.py
git commit -m "feat: add Board with drop, win detection, and full test coverage"
```

---

### Task 3: Player Protocol + RandomPlayer

**Files:**
- Create: `connect4/players/__init__.py`
- Create: `connect4/players/base.py`
- Create: `connect4/players/random.py`
- Create: `tests/test_random_player.py`

- [ ] **Step 1: Create Player protocol**

```python
# connect4/players/base.py
from __future__ import annotations

from typing import Protocol

from connect4.board import Board
from connect4.types import MoveResult, Piece


class Player(Protocol):
    def choose_column(self, board: Board, piece: Piece) -> MoveResult: ...
```

- [ ] **Step 2: Write failing tests for RandomPlayer**

```python
# tests/test_random_player.py
import pytest
from connect4.board import Board
from connect4.players.random import RandomPlayer
from connect4.types import Piece


class TestRandomPlayer:
    def test_chooses_valid_column(self):
        board = Board()
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert 0 <= result.column < Board.COLS

    def test_no_analysis(self):
        board = Board()
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.analysis is None

    def test_seeded_is_deterministic(self):
        board = Board()
        p1 = RandomPlayer(seed=42)
        p2 = RandomPlayer(seed=42)
        r1 = p1.choose_column(board, Piece.RED)
        r2 = p2.choose_column(board, Piece.RED)
        assert r1.column == r2.column

    def test_avoids_full_columns(self):
        board = Board()
        # Fill all columns except column 4
        for col in range(Board.COLS):
            if col == 4:
                continue
            for _ in range(Board.ROWS):
                board.drop(column=col, piece=Piece.RED)
        player = RandomPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 4
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_random_player.py -v`
Expected: FAIL

- [ ] **Step 4: Implement RandomPlayer**

```python
# connect4/players/random.py
from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class RandomPlayer:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        column = self._rng.choice(board.valid_columns())
        return MoveResult(column=column)
```

- [ ] **Step 5: Create `connect4/players/__init__.py`**

```python
from connect4.players.base import Player
from connect4.players.random import RandomPlayer

__all__ = ["Player", "RandomPlayer"]
```

- [ ] **Step 6: Run tests**

Run: `python -m pytest tests/test_random_player.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add connect4/players/ tests/test_random_player.py
git commit -m "feat: add Player protocol and RandomPlayer"
```

---

### Task 4: Evaluation Function

**Files:**
- Create: `connect4/evaluation.py`
- Create: `tests/test_evaluation.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_evaluation.py
import math

from connect4.board import Board
from connect4.evaluation import evaluate
from connect4.types import Piece


class TestTerminalStates:
    def test_win_returns_positive_inf(self):
        board = Board()
        for col in range(4):
            board.drop(column=col, piece=Piece.RED)
        score = evaluate(board, Piece.RED)
        assert score == math.inf

    def test_loss_returns_negative_inf(self):
        board = Board()
        for col in range(4):
            board.drop(column=col, piece=Piece.YELLOW)
        score = evaluate(board, Piece.RED)
        assert score == -math.inf

    def test_empty_board_near_zero(self):
        board = Board()
        score = evaluate(board, Piece.RED)
        assert abs(score) < 50  # should be close to neutral


class TestCenterPreference:
    def test_center_piece_scores_higher_than_edge(self):
        board_center = Board()
        board_center.drop(column=3, piece=Piece.RED)
        board_edge = Board()
        board_edge.drop(column=0, piece=Piece.RED)
        assert evaluate(board_center, Piece.RED) > evaluate(board_edge, Piece.RED)


class TestWindowScoring:
    def test_three_in_a_row_scores_high(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        score = evaluate(board, Piece.RED)
        assert score > 50  # strong threat

    def test_opponent_three_scores_negative(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        score = evaluate(board, Piece.RED)
        assert score < -50  # must block

    def test_two_in_a_row_positive(self):
        board = Board()
        board.drop(column=2, piece=Piece.RED)
        board.drop(column=3, piece=Piece.RED)
        score_2 = evaluate(board, Piece.RED)

        board_1 = Board()
        board_1.drop(column=3, piece=Piece.RED)
        score_1 = evaluate(board_1, Piece.RED)

        assert score_2 > score_1  # two pieces better than one
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_evaluation.py -v`
Expected: FAIL

- [ ] **Step 3: Implement evaluation function**

```python
# connect4/evaluation.py
from __future__ import annotations

import math

from connect4.board import Board
from connect4.types import Piece

# Scoring weights
_SCORE_TWO = 10
_SCORE_THREE = 100
_SCORE_CENTER = 6


def evaluate(board: Board, piece: Piece) -> float:
    """Score a board from piece's perspective. Positive = favorable."""
    opponent = piece.opponent

    # Terminal states
    if board.has_winner(piece):
        return math.inf
    if board.has_winner(opponent):
        return -math.inf

    score = 0.0

    # Center column preference
    center_col = Board.COLS // 2
    center_count = sum(
        1 for row in range(Board.ROWS)
        if board._grid[row][center_col] == piece
    )
    score += center_count * _SCORE_CENTER

    # Window scoring
    score += _score_all_windows(board, piece, opponent)

    return score


def _score_window(window: list[Piece | None], piece: Piece, opponent: Piece) -> float:
    """Score a single 4-cell window."""
    own = window.count(piece)
    opp = window.count(opponent)
    empty = window.count(None)

    if own == 3 and empty == 1:
        return _SCORE_THREE
    if own == 2 and empty == 2:
        return _SCORE_TWO
    if opp == 3 and empty == 1:
        return -_SCORE_THREE
    return 0


def _score_all_windows(board: Board, piece: Piece, opponent: Piece) -> float:
    """Sum scores across all 69 possible 4-cell windows."""
    score = 0.0
    grid = board._grid

    # Horizontal
    for row in range(Board.ROWS):
        for col in range(Board.COLS - 3):
            window = [grid[row][col + i] for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Vertical
    for row in range(Board.ROWS - 3):
        for col in range(Board.COLS):
            window = [grid[row + i][col] for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Diagonal ↗
    for row in range(Board.ROWS - 3):
        for col in range(Board.COLS - 3):
            window = [grid[row + i][col + i] for i in range(4)]
            score += _score_window(window, piece, opponent)

    # Diagonal ↘
    for row in range(3, Board.ROWS):
        for col in range(Board.COLS - 3):
            window = [grid[row - i][col + i] for i in range(4)]
            score += _score_window(window, piece, opponent)

    return score
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_evaluation.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add connect4/evaluation.py tests/test_evaluation.py
git commit -m "feat: add board evaluation function with window scoring and center preference"
```

---

### Task 5: MinimaxPlayer

**Files:**
- Create: `connect4/players/minimax.py`
- Create: `tests/test_minimax.py`
- Modify: `connect4/players/__init__.py`

- [ ] **Step 1: Write failing tests for forced positions**

```python
# tests/test_minimax.py
import math

from connect4.board import Board
from connect4.players.minimax import MinimaxPlayer
from connect4.types import Piece


class TestForcedWin:
    def test_takes_winning_move(self):
        """Bot must take column 3 to complete 4 in a row."""
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_takes_vertical_win(self):
        """Bot must take column 0 to complete vertical 4."""
        board = Board()
        for _ in range(3):
            board.drop(column=0, piece=Piece.RED)
        player = MinimaxPlayer(depth=1)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 0


class TestForcedBlock:
    def test_blocks_opponent_win(self):
        """Opponent has 3 in a row at cols 0-2, bot must play col 3."""
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3


class TestMoveAnalysis:
    def test_analysis_returned(self):
        board = Board()
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        assert result.analysis is not None
        assert len(result.analysis) > 0

    def test_analysis_covers_valid_columns(self):
        board = Board()
        player = MinimaxPlayer(depth=2)
        result = player.choose_column(board, Piece.RED)
        analyzed_cols = {a.column for a in result.analysis}
        assert analyzed_cols == set(board.valid_columns())


class TestDepth:
    def test_deeper_search_finds_better_moves(self):
        """At depth 1 the bot might miss a win-in-2. At depth 4 it should find it."""
        # Set up a position where RED can force a win in 2 moves
        # RED has pieces at cols 0,1 on row 0. If RED plays col 2,
        # then no matter what YELLOW does, RED can win with col 3 or vice versa.
        board = Board()
        # Row 0: R R . . . . .
        board.drop(column=0, piece=Piece.RED)
        board.drop(column=1, piece=Piece.RED)
        # YELLOW has some pieces elsewhere
        board.drop(column=5, piece=Piece.YELLOW)
        board.drop(column=6, piece=Piece.YELLOW)

        player_deep = MinimaxPlayer(depth=4)
        result = player_deep.choose_column(board, Piece.RED)
        # Should play col 2 or col 3 to set up the win
        assert result.column in [2, 3]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_minimax.py -v`
Expected: FAIL

- [ ] **Step 3: Implement MinimaxPlayer**

```python
# connect4/players/minimax.py
from __future__ import annotations

import logging
import math
from collections.abc import Callable

from connect4.board import Board
from connect4.evaluation import evaluate as default_evaluate
from connect4.types import MoveAnalysis, MoveResult, Piece

logger = logging.getLogger(__name__)

# Center-out column ordering for better alpha-beta pruning
_COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6]


class MinimaxPlayer:
    def __init__(
        self,
        depth: int = 6,
        evaluate: Callable[[Board, Piece], float] | None = None,
    ) -> None:
        self.depth = depth
        self.evaluate = evaluate or default_evaluate

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        analyses: list[MoveAnalysis] = []
        best_col = self._search(board, piece, analyses)
        logger.info("Chose column %d (analyses: %s)", best_col, analyses)
        return MoveResult(column=best_col, analysis=analyses)

    def _search(self, board: Board, piece: Piece, analyses: list[MoveAnalysis]) -> int:
        best_score = -math.inf
        best_col = board.valid_columns()[0]

        for col in _COLUMN_ORDER:
            if not board.is_valid_column(col):
                continue
            child = board.copy()
            child.drop(col, piece)

            if child.has_winner(piece):
                score = math.inf
            else:
                score = self._minimax(
                    child, piece, self.depth - 1, -math.inf, math.inf, False
                )

            analyses.append(MoveAnalysis(column=col, score=score, depth_reached=self.depth))
            logger.debug("Column %d: score=%.2f", col, score)

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def _minimax(
        self,
        board: Board,
        piece: Piece,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        opponent = piece.opponent

        # Terminal checks
        if board.has_winner(piece):
            return math.inf
        if board.has_winner(opponent):
            return -math.inf
        if board.is_full():
            return 0
        if depth == 0:
            return self.evaluate(board, piece)

        if maximizing:
            max_score = -math.inf
            for col in _COLUMN_ORDER:
                if not board.is_valid_column(col):
                    continue
                child = board.copy()
                child.drop(col, piece)
                score = self._minimax(child, piece, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = math.inf
            for col in _COLUMN_ORDER:
                if not board.is_valid_column(col):
                    continue
                child = board.copy()
                child.drop(col, opponent)
                score = self._minimax(child, piece, depth - 1, alpha, beta, True)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return min_score
```

- [ ] **Step 4: Update `connect4/players/__init__.py`**

Add `MinimaxPlayer` to imports and `__all__`.

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_minimax.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add connect4/players/minimax.py connect4/players/__init__.py tests/test_minimax.py
git commit -m "feat: add MinimaxPlayer with alpha-beta pruning and center-out ordering"
```

---

### Task 6: GreedyPlayer

**Files:**
- Create: `connect4/players/greedy.py`
- Create: `tests/test_greedy_player.py`
- Modify: `connect4/players/__init__.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_greedy_player.py
from connect4.board import Board
from connect4.players.greedy import GreedyPlayer
from connect4.types import Piece


class TestGreedyPlayer:
    def test_takes_winning_move(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_blocks_opponent_win(self):
        board = Board()
        for col in range(3):
            board.drop(column=col, piece=Piece.YELLOW)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3

    def test_prefers_win_over_block(self):
        """If both win and block are available, take the win."""
        board = Board()
        # RED can win at col 3
        for col in range(3):
            board.drop(column=col, piece=Piece.RED)
        # YELLOW can win at col 6
        for col in range(3, 6):
            board.drop(column=col, piece=Piece.YELLOW)
        player = GreedyPlayer()
        result = player.choose_column(board, Piece.RED)
        assert result.column == 3  # win, not block at 6

    def test_random_when_no_threats(self):
        board = Board()
        player = GreedyPlayer(seed=42)
        result = player.choose_column(board, Piece.RED)
        assert 0 <= result.column < Board.COLS

    def test_seeded_is_deterministic(self):
        board = Board()
        p1 = GreedyPlayer(seed=42)
        p2 = GreedyPlayer(seed=42)
        assert p1.choose_column(board, Piece.RED).column == p2.choose_column(board, Piece.RED).column
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_greedy_player.py -v`
Expected: FAIL

- [ ] **Step 3: Implement GreedyPlayer**

```python
# connect4/players/greedy.py
from __future__ import annotations

import random

from connect4.board import Board
from connect4.types import MoveResult, Piece


class GreedyPlayer:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        opponent = piece.opponent
        valid = board.valid_columns()

        # 1. Take the win
        for col in valid:
            child = board.copy()
            child.drop(col, piece)
            if child.has_winner(piece):
                return MoveResult(column=col)

        # 2. Block opponent's win
        for col in valid:
            child = board.copy()
            child.drop(col, opponent)
            if child.has_winner(opponent):
                return MoveResult(column=col)

        # 3. Random
        return MoveResult(column=self._rng.choice(valid))
```

- [ ] **Step 4: Update `connect4/players/__init__.py`**

Add `GreedyPlayer` to imports and `__all__`.

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_greedy_player.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add connect4/players/greedy.py connect4/players/__init__.py tests/test_greedy_player.py
git commit -m "feat: add GreedyPlayer (win/block/random)"
```

---

### Task 7: Game Orchestrator

**Files:**
- Create: `connect4/game.py`
- Create: `tests/test_game.py`
- Modify: `connect4/__init__.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_game.py
from connect4.board import Board
from connect4.game import Game
from connect4.players.random import RandomPlayer
from connect4.types import MoveResult, Piece


class _FixedPlayer:
    """Player that plays a predetermined sequence of columns."""
    def __init__(self, columns: list[int]):
        self._columns = iter(columns)

    def choose_column(self, board, piece):
        return MoveResult(column=next(self._columns))


class TestGameFlow:
    def test_red_goes_first(self):
        game = Game(red=RandomPlayer(seed=1), yellow=RandomPlayer(seed=2))
        state = next(game.play())
        assert state.piece == Piece.RED

    def test_players_alternate(self):
        game = Game(red=RandomPlayer(seed=1), yellow=RandomPlayer(seed=2))
        pieces = []
        for state in game.play():
            pieces.append(state.piece)
            if len(pieces) >= 4:
                break
        assert pieces[:4] == [Piece.RED, Piece.YELLOW, Piece.RED, Piece.YELLOW]

    def test_game_ends_on_win(self):
        # RED plays col 0 every turn, YELLOW plays col 1
        # RED wins with vertical 4 on col 0
        red = _FixedPlayer([0, 0, 0, 0])
        yellow = _FixedPlayer([1, 1, 1])
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        final = states[-1]
        assert final.winner == Piece.RED
        assert final.is_draw is False

    def test_game_ends_on_draw(self):
        # Known draw pattern — fill board so no 4-in-a-row exists.
        # Each column filled bottom-to-top. Pattern per column:
        #   col 0: R R R Y Y Y    col 1: Y Y Y R R R
        #   col 2: R R R Y Y Y    col 3: Y Y Y R R R
        #   col 4: R R R Y Y Y    col 5: Y Y Y R R R
        #   col 6: R R R Y Y Y
        # No horizontal, vertical, or diagonal 4-in-a-row.
        # Moves must alternate RED/YELLOW, so we interleave carefully.
        #
        # We use _FixedPlayer with a precomputed move sequence.
        # Build the sequence: place pieces column by column, tracking turns.
        red_moves = []
        yellow_moves = []
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                is_red_cell = (row < 3) == (col % 2 == 0)
                if is_red_cell:
                    red_moves.append(col)
                else:
                    yellow_moves.append(col)

        # Interleave into turn order (red first, then yellow, alternating)
        sequence_red = []
        sequence_yellow = []
        ri, yi = 0, 0
        for turn in range(42):
            if turn % 2 == 0:  # RED's turn
                sequence_red.append(red_moves[ri])
                ri += 1
            else:  # YELLOW's turn
                sequence_yellow.append(yellow_moves[yi])
                yi += 1

        red = _FixedPlayer(sequence_red)
        yellow = _FixedPlayer(sequence_yellow)
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        final = states[-1]
        assert final.winner is None
        assert final.is_draw is True
        assert len(states) == 42

    def test_winner_state_has_winner_set(self):
        red = _FixedPlayer([0, 0, 0, 0])
        yellow = _FixedPlayer([1, 1, 1])
        game = Game(red=red, yellow=yellow)
        states = list(game.play())
        winners = [s for s in states if s.winner is not None]
        assert len(winners) == 1
        assert winners[0].winner == Piece.RED

    def test_analysis_flows_through(self):
        """MoveAnalysis from players should appear in GameState."""
        from connect4.players.minimax import MinimaxPlayer
        game = Game(red=MinimaxPlayer(depth=1), yellow=RandomPlayer(seed=1))
        state = next(game.play())
        # MinimaxPlayer provides analysis
        assert state.analysis is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_game.py -v`
Expected: FAIL

- [ ] **Step 3: Implement Game**

```python
# connect4/game.py
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
```

- [ ] **Step 4: Update `connect4/__init__.py`**

Add `Game` to barrel imports and `__all__`.

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_game.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add connect4/game.py connect4/__init__.py tests/test_game.py
git commit -m "feat: add Game orchestrator with generator-based play loop"
```

---

### Task 8: HumanPlayer + CLI

**Files:**
- Create: `connect4/players/human.py`
- Create: `connect4/cli.py`
- Create: `connect4/__main__.py`
- Create: `tests/test_human_player.py`
- Modify: `connect4/players/__init__.py`

- [ ] **Step 1: Write failing tests for HumanPlayer**

```python
# tests/test_human_player.py
import pytest
from connect4.board import Board
from connect4.players.human import HumanPlayer
from connect4.types import Piece


class TestHumanPlayer:
    def test_valid_input(self):
        player = HumanPlayer(input_fn=lambda _: "3")
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_non_integer(self):
        inputs = iter(["abc", "3"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_out_of_range(self):
        inputs = iter(["9", "-1", "3"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(Board(), Piece.RED)
        assert result.column == 3

    def test_retries_on_full_column(self):
        board = Board()
        for _ in range(Board.ROWS):
            board.drop(column=3, piece=Piece.RED)
        inputs = iter(["3", "4"])
        player = HumanPlayer(input_fn=lambda _: next(inputs))
        result = player.choose_column(board, Piece.RED)
        assert result.column == 4

    def test_no_analysis(self):
        player = HumanPlayer(input_fn=lambda _: "0")
        result = player.choose_column(Board(), Piece.RED)
        assert result.analysis is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_human_player.py -v`
Expected: FAIL

- [ ] **Step 3: Implement HumanPlayer**

```python
# connect4/players/human.py
from __future__ import annotations

from collections.abc import Callable

from connect4.board import Board
from connect4.types import MoveResult, Piece


class HumanPlayer:
    def __init__(self, input_fn: Callable[[str], str] = input) -> None:
        self._input_fn = input_fn

    def choose_column(self, board: Board, piece: Piece) -> MoveResult:
        while True:
            raw = self._input_fn(f"Player {piece.name}, pick a column (0-6): ")
            try:
                column = int(raw)
            except ValueError:
                print(f"Invalid input: '{raw}'. Please enter a number 0-6.")
                continue
            if not board.is_valid_column(column):
                if column < 0 or column >= Board.COLS:
                    print(f"Column {column} is out of range. Pick 0-6.")
                else:
                    print(f"Column {column} is full. Pick another.")
                continue
            return MoveResult(column=column)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_human_player.py -v`
Expected: All PASS

- [ ] **Step 5: Create CLI**

```python
# connect4/cli.py
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
```

```python
# connect4/__main__.py
from connect4.cli import main

main()
```

- [ ] **Step 6: Update `connect4/players/__init__.py`**

Add `HumanPlayer` to imports and `__all__`.

- [ ] **Step 7: Smoke test**

Run: `echo "3\n3\n4\n4\n5\n5\n6" | python -m connect4`
Expected: Game runs, bot responds, output looks reasonable.

- [ ] **Step 8: Commit**

```bash
git add connect4/players/human.py connect4/cli.py connect4/__main__.py connect4/players/__init__.py tests/test_human_player.py
git commit -m "feat: add HumanPlayer, CLI, and python -m connect4 entry point"
```

---

### Task 9: Bot Strength + Property Tests

**Files:**
- Create: `tests/test_bot_strength.py`

- [ ] **Step 1: Write bot strength tests**

```python
# tests/test_bot_strength.py
import time

import pytest

from connect4.board import Board
from connect4.game import Game
from connect4.players.greedy import GreedyPlayer
from connect4.players.minimax import MinimaxPlayer
from connect4.players.random import RandomPlayer
from connect4.types import Piece


class TestBotVsRandom:
    def test_minimax_beats_random_overwhelmingly(self):
        """MinimaxPlayer should win >95% against RandomPlayer."""
        wins = 0
        games = 100
        for seed in range(games):
            game = Game(
                red=MinimaxPlayer(depth=4),
                yellow=RandomPlayer(seed=seed),
            )
            for state in game.play():
                if state.winner == Piece.RED:
                    wins += 1
                    break
        win_rate = wins / games
        assert win_rate > 0.95, f"Win rate {win_rate:.0%} is below 95%"


class TestBotVsGreedy:
    def test_minimax_beats_greedy(self):
        """MinimaxPlayer should win >80% against GreedyPlayer."""
        wins = 0
        games = 100
        for seed in range(games):
            game = Game(
                red=MinimaxPlayer(depth=4),
                yellow=GreedyPlayer(seed=seed),
            )
            for state in game.play():
                if state.winner == Piece.RED:
                    wins += 1
                    break
        win_rate = wins / games
        assert win_rate > 0.80, f"Win rate {win_rate:.0%} is below 80%"


class TestPerformance:
    def test_move_completes_within_budget(self):
        """Each move should complete in <2 seconds at depth 6."""
        board = Board()
        player = MinimaxPlayer(depth=6)
        # Make a few moves to create a non-trivial position
        board.drop(3, Piece.RED)
        board.drop(3, Piece.YELLOW)
        board.drop(4, Piece.RED)

        start = time.monotonic()
        player.choose_column(board, Piece.YELLOW)
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"Move took {elapsed:.2f}s, budget is 2s"


class TestGameInvariants:
    """Property-based tests: invariants that hold for any valid game."""

    def _play_full_game(self, seed: int) -> list:
        game = Game(
            red=RandomPlayer(seed=seed),
            yellow=RandomPlayer(seed=seed + 1000),
        )
        return list(game.play())

    @pytest.mark.parametrize("seed", range(50))
    def test_piece_count_balance(self, seed):
        """After each move, |red_count - yellow_count| <= 1."""
        states = self._play_full_game(seed)
        for state in states:
            red = sum(
                1 for r in range(Board.ROWS) for c in range(Board.COLS)
                if state.board._grid[r][c] == Piece.RED
            )
            yellow = sum(
                1 for r in range(Board.ROWS) for c in range(Board.COLS)
                if state.board._grid[r][c] == Piece.YELLOW
            )
            assert abs(red - yellow) <= 1

    @pytest.mark.parametrize("seed", range(50))
    def test_no_floating_pieces(self, seed):
        """Every piece must rest on the bottom or another piece."""
        states = self._play_full_game(seed)
        for state in states:
            for row in range(Board.ROWS):
                for col in range(Board.COLS):
                    if state.board._grid[row][col] is not None and row > 0:
                        assert state.board._grid[row - 1][col] is not None

    @pytest.mark.parametrize("seed", range(50))
    def test_game_length(self, seed):
        """A game has at most 42 moves."""
        states = self._play_full_game(seed)
        assert len(states) <= 42

    @pytest.mark.parametrize("seed", range(50))
    def test_at_most_one_winner(self, seed):
        """Only one state should have a winner."""
        states = self._play_full_game(seed)
        winners = [s for s in states if s.winner is not None]
        assert len(winners) <= 1

    @pytest.mark.parametrize("seed", range(50))
    def test_winner_actually_won(self, seed):
        """If a winner is declared, the winning line exists on the board."""
        states = self._play_full_game(seed)
        for state in states:
            if state.winner:
                assert state.board.has_winner(state.winner)
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_bot_strength.py -v`
Expected: All PASS. Bot strength tests may take ~30-60 seconds.

Note: if bot vs greedy or bot vs random thresholds fail, adjust minimax depth upward (try depth=5 or depth=6) in the test. The depth=4 is chosen for speed in CI; a higher depth wins more but takes longer.

- [ ] **Step 3: Commit**

```bash
git add tests/test_bot_strength.py
git commit -m "feat: add bot strength tests and game invariant property tests"
```

---

### Task 10: Final Polish + Full Test Run

**Files:**
- Modify: `connect4/__init__.py` (final barrel)
- Review: all files

- [ ] **Step 1: Verify final `connect4/__init__.py` exports**

```python
from connect4.board import Board
from connect4.game import Game
from connect4.types import GameState, MoveAnalysis, MoveResult, Piece

__all__ = ["Board", "Game", "GameState", "MoveAnalysis", "MoveResult", "Piece"]
```

- [ ] **Step 2: Verify `connect4/players/__init__.py` exports**

```python
from connect4.players.base import Player
from connect4.players.greedy import GreedyPlayer
from connect4.players.human import HumanPlayer
from connect4.players.minimax import MinimaxPlayer
from connect4.players.random import RandomPlayer

__all__ = ["Player", "GreedyPlayer", "HumanPlayer", "MinimaxPlayer", "RandomPlayer"]
```

- [ ] **Step 3: Run full test suite**

Run: `python -m pytest tests/ -v --tb=short`
Expected: All PASS

- [ ] **Step 4: Verify the public API works**

Run:
```python
python -c "
from connect4 import Board, Game, Piece
from connect4.players import MinimaxPlayer, RandomPlayer
board = Board()
board.drop(column=3, piece=Piece.RED)
print(board)
game = Game(red=MinimaxPlayer(depth=2), yellow=RandomPlayer(seed=42))
states = list(game.play())
print(f'Game ended in {len(states)} moves. Winner: {states[-1].winner}')
"
```
Expected: Board prints correctly, game completes.

- [ ] **Step 5: Check line counts**

Run: `wc -l connect4/*.py connect4/players/*.py`
Expected: No file exceeds ~300 lines.

- [ ] **Step 6: Commit and push**

```bash
git add -A
git commit -m "chore: finalize barrel exports and verify full test suite"
git push
```
