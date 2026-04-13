"""Benchmark minimax performance at each search depth.

Usage:
    python scripts/benchmark_depth.py
    python scripts/benchmark_depth.py --max-depth 12 --max-time 60
"""

import argparse
import time

from connect4.board import Board
from connect4.players.minimax import MinimaxPlayer
from connect4.types import Piece


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark minimax at each depth")
    parser.add_argument("--max-depth", type=int, default=10, help="Max depth to test")
    parser.add_argument("--max-time", type=float, default=30.0, help="Stop if a single move exceeds this (seconds)")
    args = parser.parse_args()

    # Mid-game position (more realistic than empty board)
    board = Board()
    board.drop(3, Piece.RED)
    board.drop(3, Piece.YELLOW)
    board.drop(4, Piece.RED)
    board.drop(2, Piece.YELLOW)
    board.drop(4, Piece.RED)

    print(board)
    print()

    header = f"{'Depth':<7} {'Time (s)':<12} {'Ratio':<10}"
    print(header)
    print("-" * len(header))

    prev = None
    for depth in range(1, args.max_depth + 1):
        start = time.monotonic()
        player = MinimaxPlayer(depth=depth)
        player.choose_column(board, Piece.YELLOW)
        elapsed = time.monotonic() - start

        ratio = f"{elapsed / prev:.1f}x" if prev and prev > 0.0001 else "---"
        prev = elapsed
        bar = "#" * max(1, int(elapsed * 20))
        print(f"{depth:<7} {elapsed:<12.4f} {ratio:<10} {bar}")

        if elapsed > args.max_time:
            print(f"(stopping — exceeded {args.max_time}s budget)")
            break


if __name__ == "__main__":
    main()
