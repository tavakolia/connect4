# Connect 4

A Python module for playing Connect 4 against a minimax bot with alpha-beta pruning.

## Quick Start

```bash
python -m connect4
```

You play as RED (first move), the bot plays as YELLOW. Enter a column number (1-7) each turn.

### Options

The CLI allows you to pit any combination of players against each other. Supported players include `human`, `minimax`, `greedy`, and `random`.
Arguments (like search depth for `minimax`) are provided immediately following the player's name.

```bash
python -m connect4 minimax 8 human   # let the bot go first (depth 8)
python -m connect4 human minimax 2   # play as red against an easy bot (depth 2)
python -m connect4 greedy random     # fast bot vs bot
```

## Using as a Library

```python
from connect4 import Board, Game, Piece, Player
from connect4.players import MinimaxPlayer, RandomPlayer, GreedyPlayer

# Play a game between two bots
game = Game(red=MinimaxPlayer(depth=6), yellow=RandomPlayer(seed=42))
for state in game.play():
    print(state.board)
    if state.winner:
        print(f"{state.winner.name} wins!")
    elif state.is_draw:
        print("Draw!")

# Inspect the board directly
board = Board()
board.drop(column=3, piece=Piece.RED)
print(board)
print(board.has_winner(Piece.RED))  # False
print(board.valid_columns())        # [0, 1, 2, 3, 4, 5, 6]
```

## Architecture

```
CLI (cli.py) → Game (game.py) → Players + Board (board.py) → Evaluation (evaluation.py)
```

- **Board** — 6×7 grid, piece dropping with gravity, win detection in 4 directions
- **Game** — Generator-based orchestrator: `Game.play()` yields a `GameState` after each move
- **Players** — All satisfy the `Player` protocol (structural typing, no inheritance required):
  - `MinimaxPlayer` — Alpha-beta pruning with configurable depth and injectable evaluation function
  - `RandomPlayer` — Seeded RNG for reproducible games
  - `GreedyPlayer` — Takes wins, blocks losses, otherwise random
  - `HumanPlayer` — Reads from stdin with input validation
- **Evaluation** — Pure function scoring board positions via window analysis and center preference

## Running Tests

```bash
python -m pytest tests/ -v
```

339 tests covering:
- Board mechanics and win detection (all 4 directions, edge cases)
- Minimax correctness (forced wins, forced blocks, immediate-win priority)
- Evaluation function (terminal states, center preference, window scoring)
- Game flow (alternation, win/draw detection, generator semantics)
- Bot strength (>95% vs random, >80% vs greedy over 100 games each)
- Performance (depth-6 move < 2 seconds)
- Game invariants (piece balance, no floating pieces, game length, single winner)

## Project Structure

```
connect4/
├── __init__.py          # Public API: Board, Game, Piece, Player
├── types.py             # Piece enum, GameState, MoveResult, MoveAnalysis
├── board.py             # Board state, drop, win/draw detection
├── game.py              # Game orchestrator (generator-based)
├── evaluation.py        # Board evaluation heuristics
├── cli.py               # Terminal entry point
├── __main__.py           # python -m connect4
└── players/
    ├── base.py          # Player and InteractivePlayer protocols
    ├── minimax.py       # Minimax with alpha-beta pruning
    ├── random.py        # Random player (seeded)
    ├── greedy.py        # One-ply greedy player
    └── human.py         # Human input via stdin

tests/
├── test_board.py        # 26 tests
├── test_minimax.py      # 7 tests
├── test_evaluation.py   # 7 tests
├── test_game.py         # 6 tests
├── test_bot_strength.py # 253 tests (statistical + property-based)
├── test_greedy_player.py
├── test_human_player.py
├── test_random_player.py
└── test_types.py
```

## Requirements

- Python >= 3.10
- No third-party dependencies (standard library only)
- pytest for running tests
