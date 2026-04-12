# Connect 4 — Programming Exercise

## Objective

Write a Python program that enables a user to play Connect 4 against a bot you developed.

Your bot should be able to defeat a casual player. Be prepared to discuss your design decisions & testing strategy in detail.

The goal of this exercise is to give you an opportunity to demonstrate how you think about key design choices & architect your code, not to ask you to build a perfect game-playing system.

While bot performance will be one factor in our evaluation, the quality of your code, the rigor of your testing strategy, & the thoughtfulness of your system design will be given more weight. If you're spending more than 8 hours on this exercise, you're probably approaching diminishing returns.

## Requirements

1. Your solution should be packaged as python module(s) for ease of import.

## Non-requirements

1. Reinvent AlphaZero — we don't expect knowledge of reinforcement learning. It's sufficient to build a bot based upon first-principles heuristics.
2. Build a fancy UI — it's perfectly acceptable to enable the user to play interactively in the terminal.

## FAQs

1. Any version of Python >= 3.9 is acceptable.
2. You may use any 3rd party package that is available on PyPI if you like but this is not required. It's possible to complete the exercise using only the standard library.
3. Pick whichever testing library you are most comfortable with.

## Rules

Connect 4 is a two-player game played with checkers on a vertically-oriented 6 x 7 grid. A checker placed in one of the 7 slots at the top of the board will drop into the lowest available position in the column. The objective of the game is to get four of your colored checkers in a row vertically, horizontally, or diagonally in the grid. Each player starts with 21 checkers and takes turns placing one of their colored checkers. The first player to put four of their checkers in a row vertically, horizontally, or diagonally wins.

## Context

This project is a take-home assignment for a staff+ level position. Design choices and end product should reflect that level of seniority.
