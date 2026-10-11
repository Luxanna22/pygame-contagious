"""
board.py
────────
Grid data model.

Contains
--------
Spot    – a single cell on the board.
Board   – the 2-D grid with all mutation helpers.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .constants import BORDER

if TYPE_CHECKING:
    pass


# ── Spot ──────────────────────────────────────────────────────────────────────

class Spot:
    """One cell in the chain-reaction grid."""

    __slots__ = ("color", "neighbors", "noAtoms", "limit")

    def __init__(self) -> None:
        self.color: tuple[int, int, int] = BORDER
        self.neighbors: list[Spot]       = []
        self.noAtoms: int                = 0
        self.limit: int                  = 4  # overwritten by Board._link_neighbors

    def add_neighbors(self, i: int, j: int, grid: list[list["Spot"]]) -> None:
        """Populate ``self.neighbors`` from the surrounding grid cells."""
        cols = len(grid)
        rows = len(grid[0]) if grid else 0
        if i > 0:        self.neighbors.append(grid[i - 1][j])
        if i < cols - 1: self.neighbors.append(grid[i + 1][j])
        if j < rows - 1: self.neighbors.append(grid[i][j + 1])
        if j > 0:        self.neighbors.append(grid[i][j - 1])
        # Corner/edge cells have fewer neighbours → lower overflow threshold
        self.limit = len(self.neighbors)


# ── Board ─────────────────────────────────────────────────────────────────────

class Board:
    """
    Manages the cols × rows grid of ``Spot`` objects plus per-cell idle
    animation metadata.
    """

    def __init__(self, cols: int, rows: int) -> None:
        self.cols = cols
        self.rows = rows
        self.grid: list[list[Spot]]             = []
        self.cell_anim_data: dict[tuple, tuple] = {}
        self._build()

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid = [
            [Spot() for _ in range(self.rows)]
            for _ in range(self.cols)
        ]
        for i in range(self.cols):
            for j in range(self.rows):
                self.grid[i][j].add_neighbors(i, j, self.grid)

        # Assign a unique idle-spin speed and phase to every cell
        self.cell_anim_data = {
            (i, j): (random.uniform(0.18, 0.45), random.uniform(0, 360))
            for i in range(self.cols)
            for j in range(self.rows)
        }

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_neighbors(self, i: int, j: int) -> list[tuple[int, int]]:
        """Return valid (col, row) neighbour coordinates of cell (i, j)."""
        nb: list[tuple[int, int]] = []
        if i > 0:            nb.append((i - 1, j))
        if i < self.cols - 1: nb.append((i + 1, j))
        if j > 0:            nb.append((i, j - 1))
        if j < self.rows - 1: nb.append((i, j + 1))
        return nb

    def count_scores(
        self, players: list[tuple[int, int, int]]
    ) -> list[int]:
        """Return atom counts per player (by player-list index)."""
        scores = [0] * len(players)
        for col in self.grid:
            for cell in col:
                if cell.noAtoms > 0 and cell.color in players:
                    scores[players.index(cell.color)] += cell.noAtoms
        return scores

    def active_colors(self) -> set[tuple[int, int, int]]:
        """Return the set of player colours present anywhere on the board."""
        result: set[tuple[int, int, int]] = set()
        for col in self.grid:
            for cell in col:
                if cell.noAtoms > 0 and cell.color != BORDER:
                    result.add(cell.color)
        return result

    # ── Mutation ──────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Wipe the board while keeping animation metadata."""
        for col in self.grid:
            for cell in col:
                cell.color   = BORDER
                cell.noAtoms = 0

    def cell(self, i: int, j: int) -> Spot:
        return self.grid[i][j]
