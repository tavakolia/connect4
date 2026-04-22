"""End-to-end tests that exercise the real CLI via subprocess.

These tests cover what unit tests cannot: arg parsing, __main__ wiring,
stdout rendering, and the full game loop from argv to terminal output.
"""

import re
import subprocess
import sys

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _run(*args: str, stdin: str = "", timeout: float = 60.0) -> subprocess.CompletedProcess:
    """Invoke `python -m connect4` with the given CLI args."""
    proc = subprocess.run(
        [sys.executable, "-m", "connect4", *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    # Strip ANSI escapes so assertions match plain text.
    proc.stdout = _ANSI_RE.sub("", proc.stdout)
    proc.stderr = _ANSI_RE.sub("", proc.stderr)
    return proc


class TestBotVsBot:
    def test_random_vs_random_completes(self):
        result = _run("random", "1", "random", "2")
        assert result.returncode == 0
        assert "Connect 4" in result.stdout
        # Game must end in a win or a draw — never mid-game.
        assert ("wins!" in result.stdout) or ("draw" in result.stdout)

    def test_greedy_vs_random_completes(self):
        result = _run("greedy", "random", "7")
        assert result.returncode == 0
        assert ("wins!" in result.stdout) or ("draw" in result.stdout)

    def test_minimax_beats_random(self):
        # Depth 2 is enough to reliably beat a seeded random player end-to-end.
        result = _run("minimax", "2", "random", "0")
        assert result.returncode == 0
        assert "RED wins!" in result.stdout


class TestCliErrors:
    def test_unknown_player_exits_nonzero(self):
        result = _run("bogus")
        assert result.returncode != 0
        assert "Unknown player type" in result.stderr

    def test_missing_second_player_exits_nonzero(self):
        result = _run("human")
        assert result.returncode != 0
        assert "Not enough players" in result.stderr


class TestHumanInput:
    # Cycling through all columns guarantees every input hits a legal move
    # (until the whole board fills), so stdin never runs out mid-game.
    _CYCLING_INPUT = ("\n".join(str(c) for c in range(1, 8)) + "\n") * 10

    def test_human_move_is_accepted_from_stdin(self):
        result = _run("human", "random", "0", stdin=self._CYCLING_INPUT, timeout=30.0)
        assert result.returncode == 0
        assert "RED plays column 1" in result.stdout
        assert ("wins!" in result.stdout) or ("draw" in result.stdout)

    def test_human_retries_on_invalid_input(self):
        stdin = "abc\n9\n" + self._CYCLING_INPUT
        result = _run("human", "random", "0", stdin=stdin, timeout=30.0)
        assert result.returncode == 0
        assert "Invalid input" in result.stdout
        assert "out of range" in result.stdout
