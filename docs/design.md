# Connect 4 — Design Spec

A Python module that lets a user play Connect 4 against a bot in the terminal.
The bot uses minimax with alpha-beta pruning and a heuristic evaluation function.
The architecture separates game engine, player logic, and UI so that all interesting
logic is importable and testable without I/O.

Target: staff+ take-home. Evaluation weights code quality, testing rigor, and
system design above bot strength.

## Project Structure

```
connect4/
├── __init__.py    # Public API: Board, Game, Piece, Player, GameState, MoveResult, MoveAnalysis
├── board.py       # Board state, drop, win/draw detection
├── game.py        # Generator-based orchestrator
├── types.py       # Piece enum, dataclasses
├── evaluation.py  # Pure heuristic scoring function
├── renderer.py    # TerminalRenderer (UI / HumanUIDelegate)
├── cli.py         # argv parsing + entry point
├── __main__.py    # python -m connect4
└── players/
    ├── base.py    # Player, InteractivePlayer protocols
    ├── minimax.py # Alpha-beta search
    ├── random.py  # Uniform random (seeded)
    ├── greedy.py  # Take-win/block/random
    └── human.py   # Stdin via UI delegate
```

## Design Decisions

Each decision records what we chose, what we rejected, and why.

### D1: Bot Algorithm — Minimax with Alpha-Beta Pruning

**Chosen:** Minimax with alpha-beta pruning and a heuristic evaluation function.

**Rejected:**
- *MCTS* — Shines with huge branching factors (Go ~250). Connect 4's branching
  factor of 7 is ideal for classical minimax. MCTS would signal over-investment.
- *Rule-based / no search* — Too lightweight; the bot can't look ahead.
- *Reinforcement learning* — Explicitly called out as a non-requirement.

**Why:** Minimax is deterministic, naturally testable, and the evaluation
function provides substantive design trade-offs to discuss. Alpha-beta preserves
optimality (same result as full minimax, just prunes). Depth 6–8 runs in under
a second with move ordering.

### D2: Player Interface — Protocol (Structural Typing)

**Chosen:** `typing.Protocol`. Any object with a matching `choose_column` method
satisfies the interface — no inheritance required.

**Rejected:**
- *ABC* — Works, but couples every player implementation to the base class
  import. Less Pythonic.
- *No formal interface* — Duck typing without annotations gives up IDE and
  type-checker support.

**Why:** Protocol is the modern Pythonic equivalent of TypeScript's structural
interfaces. Zero import coupling between implementations and the protocol.
Type checkers catch mismatches at analysis time.

### D3: Game Flow — Generator Pattern

**Chosen:** `Game.play()` is a generator that yields `GameState` after each move.
The caller drives the loop with `for state in game.play()`.

**Rejected:**
- *Callbacks/events* — `Game(on_move=..., on_win=...)` is more complex and moves
  loop control into the engine.
- *Return final result only* — The CLI couldn't display the board mid-game
  without I/O leaking into `Game`.

**Why:** The engine has no knowledge of the caller. `list(game.play())` collapses
an entire game for testing. The caller controls pacing (sleeps, prompts, logs).

### D4: Board Representation — 2D List

**Chosen:** `list[list[Piece | None]]` with `grid[row][col]`, row 0 = bottom.

**Rejected:**
- *Bitboard (two 64-bit integers)* — ~15x faster, but cryptic bit manipulation.
  Overkill for depth 6–8.
- *1D flat array* — Marginally less readable; index math obscures intent.
- *NumPy* — Adds a dependency for no meaningful benefit at this scale.

**Why:** Readability over raw performance for a take-home. The grid is
debuggable, printable, and obvious. Row 0 = bottom matches the physical
gravity metaphor. Bitboard is a known optimization to mention in discussion.

### D5: Board Constants — Class Attributes (YAGNI)

**Chosen:** `ROWS = 6`, `COLS = 7`, `CONNECT = 4` as class-level constants on `Board`.

**Rejected:** Constructor parameters (`Board(rows=..., cols=..., connect=...)`).
Connect 4 is definitionally 6×7×4 — every test would have to consider variable
sizes, and the evaluation function would need to generalize.

**Why:** Named constants avoid magic numbers and live on the class they describe.
The change point for configurability is obvious; we just don't pay the cost.

### D6: Naming — Player (Protocol) + Piece (Enum)

**Chosen:** `Player` for the protocol, `Piece` for the enum (`RED`, `YELLOW`).

**Why:** Reads naturally: "a Player chooses where to drop a Piece." "Strategy"
implies computation, which feels wrong for `HumanPlayer`. "Agent" has AI/ML
baggage. "Piece" is more concrete than "Color" or "Side" — it's what's on the
board.

### D7: Evaluation Function — Pure Function, Separate File

**Chosen:** `evaluation.py` contains a standalone `evaluate(board, piece) -> float`.
`MinimaxPlayer` accepts an optional `evaluate` callable parameter.

**Rejected:**
- *Method on Board* — Couples scoring to the data structure.
- *Method on MinimaxPlayer* — Couples the heuristic to the search algorithm.
- *Evaluator class/protocol* — Unnecessary abstraction for a stateless function.

**Why:** Search and evaluation are independent concerns. Each can be tested in
isolation. The injectable callable means swapping heuristics requires no
subclassing.

### D8: Human Input — Dependency Injection (UI Delegate)

**Chosen:** `HumanPlayer(ui_delegate: HumanUIDelegate)`. The player asks the
delegate for input and error formatting.

**Rejected:**
- *Mock stdin in tests* — Couples tests to ANSI codes and fragile stdin patching.
- *Human input outside the Player protocol* — Would force `Game` to know which
  players are human.

**Why:** `HumanPlayer(ui_delegate=FakeUI())` is a trivial test setup. Input
validation (non-integer, out-of-range, full column) is fully contained in the
player's retry loop; the CLI and Game never see invalid input.

### D9: Observability — Logging + Move Analysis

**Chosen:** Python `logging` (per-module loggers via `__name__`) plus structured
`MoveAnalysis` data returned alongside each move.

**Why:** Logging gives configurable verbosity (`DEBUG` for search internals,
`INFO` for chosen moves). `MoveAnalysis` is programmatic — tests can assert on
scores, the CLI can display reasoning. Together they provide full observability.

### D10: Move Ordering — Center-Out

**Chosen:** Explore columns in order `[3, 2, 4, 1, 5, 0, 6]` during minimax.

**Why:** Center columns participate in more four-in-a-row lines (center column
= 9 possible lines; edge columns = 4). Exploring them first means alpha-beta
finds tight bounds early and prunes more aggressively. Same result as
left-to-right, dramatically fewer nodes visited. Trivial to implement.

### D11: Random and Greedy Players — Separate Files

**Chosen:** `RandomPlayer` (uniform random, seeded) and `GreedyPlayer` (takes
wins, blocks losses, else random) in separate files.

**Why RandomPlayer:** Baseline opponent for bot strength tests, dev-time
sparring partner, test fixture without mocks, and seeded for reproducibility.

**Why GreedyPlayer:** A better proxy for "casual player" than pure random, and a
second data point for strength testing.

## Testing Strategy

pytest, five layers from fast/isolated to slow/statistical:

- **Unit** — `test_board.py`, `test_evaluation.py`, `test_types.py`,
  `test_renderer.py`, `test_random_player.py`, `test_greedy_player.py`,
  `test_human_player.py`.
- **Integration** — `test_game.py` (generator flow), `test_cli.py`
  (`_load_player` reflection), `test_minimax.py` (forced wins/blocks/depth).
- **Known positions** — `test_known_positions.py` drives the bot through
  handcrafted boards where the objectively correct move is known.
- **Property-based** — `test_bot_strength.py` (invariants): after any move,
  `|red − yellow| ≤ 1`, no floating pieces, length ≤ 42, ≤ 1 winner, and the
  declared winner actually has four in a row.
- **Statistical / E2E** — `test_bot_strength.py` runs MinimaxPlayer vs. Random
  (>95%) and vs. Greedy (>80%) over 100 seeded games. `test_e2e.py` invokes
  `python -m connect4` as a subprocess and asserts end-to-end behavior.

## Over-Engineering Traps

Things that seem like good ideas but violate YAGNI at this scope. Know them
for discussion; don't build them.

- **Transposition table** — Cache board-state → score to skip repeated subtrees.
  First optimization if perf became a concern.
- **Bitboard** — Two 64-bit ints, win detection via shift/mask. ~15x faster
  but cryptic to read and modify live.
- **Iterative deepening** — Search depth 1, 2, 3… with a time budget. Natural
  complement to a transposition table.
- **Configurable board size** — Named constants already mark the change point;
  don't pay the complexity cost.
- **Difficulty levels** — The `depth` parameter on `MinimaxPlayer` already
  provides a basic knob. A `NoisyMinimaxPlayer` wrapper would extend it.
- **Negamax refactor** — Elegant simplification of minimax. Our implementation
  is more widely understood; not a functional win.

## Known Limitations

- **No mate-distance scoring.** Wins and losses return `±math.inf` regardless of
  depth, so the bot can't distinguish "win in 1" from "win in 5" inside the
  recursion. The root-level `is_winner_at` shortcut masks this for immediate
  wins, but in deeper searches the bot may pick a longer forced win. Fix is a
  couple of lines (subtract depth from terminal score); left out to stay inside
  the time budget.
- **Evaluation redundancy.** `evaluate()` calls `board.has_winner()` for both
  sides at the top of every leaf node, though `_minimax` has already confirmed
  the last drop didn't win. Biggest perf lever if pushing to depth 8+.
- **`Game.play` uses full-board win scan.** `has_winner()` is O(rows·cols·4) on
  every move; `is_winner_at(row, col)` would be O(1). Not a correctness bug,
  just inconsistent with the optimization already used inside the search.
