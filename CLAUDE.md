# Connect 4 — Project Guidelines

## Key Gotchas (from requirements analysis)

1. **Module packaging is a hard requirement** — `from connect4 import ...` must work. Game logic MUST be decoupled from CLI/terminal. Reviewers will likely try to import and use the module programmatically.
2. **Draw condition** — Each player has 21 checkers (42 total). Board can fill up. Must handle draws explicitly.
3. **"First-principles heuristics"** — They're nudging toward minimax + eval function. Don't over-invest in exotic algorithms.
4. **Three evaluation axes** — Code quality, testing rigor, system design. All three must be strong.
5. **8-hour budget** — Don't gold-plate. Clean and well-tested, not over-engineered.
6. **"Be prepared to discuss"** — Every design choice should be defensible. The code is a vehicle for conversation.

## Architecture Principles

- **Strategy pattern for bot algorithms** — Design so a different algorithm can be swapped in later. Minimax w/ alpha-beta is the default.
- **Clean separation** — Game engine (board/rules) → Bot strategy (pluggable) → UI layer (terminal, swappable).
- **Human-modifiable during presentation** — Clear file names, clear responsibilities. Someone should be able to find and change things quickly.
- **Max ~300 lines per file** — Unless splitting would create an artificial seam. Keep files focused and navigable.

## Code Style

- Python >= 3.10 (use modern syntax: `X | None` not `Optional[X]`)
- Standard library only (unless a package genuinely adds value)
- pytest for testing

## Implementation Notes

- **Move ordering in minimax** — Explore columns center-out: [3,2,4,1,5,0,6]. Dramatically improves alpha-beta pruning.
- **Diagonal win detection** — Both directions (NE-SW and NW-SE). #1 source of bugs in Connect 4 implementations. Test thoroughly.

## Interview Prep (know but don't implement)

- Connect 4 is a **solved game** (Victor Allis, 1988). First player wins with perfect play starting center column.
- **Optimizations to mention**: transposition table, iterative deepening, bitboard representation, negamax simplification.
- **Difficulty levels**: reduce depth, add randomness, skip blocking. Not in scope but know how.
- **Odd/even threat theory**: threats on odd rows favor Player 1, even rows favor Player 2.
- **Board size changes**: constants become constructor params, eval generalizes. YAGNI but know the seams.
