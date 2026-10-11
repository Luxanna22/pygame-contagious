"""
state.py
────────
Pure data container for a running game session.
No game logic or rendering code lives here — only the shared mutable
state accessed by both ``game.py`` and ``renderer.py``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from .board import Board

if TYPE_CHECKING:
    from effects import ChainDisplay, Particle, Shockwave


@dataclass
class GameState:
    # ── Board / geometry ──────────────────────────────────────────────────────
    board:       Board
    blocks:      int
    cols:        int
    rows:        int
    d:           int          # half-cell offset used by rendering

    # ── Players ───────────────────────────────────────────────────────────────
    num_players:    int
    players:        list[tuple[int, int, int]]   # ordered colour per player
    player_imgs:    list[pygame.Surface]          # scaled sprite per player
    active_players: list[int]                     # indices still in game
    scores:         list[int]

    # ── Turn tracking ─────────────────────────────────────────────────────────
    turns:          int  = 0
    current_player: int  = 0

    # ── Win state ─────────────────────────────────────────────────────────────
    game_over_winner: int  = -1   # -1 = nobody has won yet
    win_anim_t:       int  = 0

    # ── Animation queues ──────────────────────────────────────────────────────
    overflow_queue:   list  = field(default_factory=list)  # (i,j,color)
    pending_adds:     list  = field(default_factory=list)  # (i,j,color)
    active_particles: list  = field(default_factory=list)  # Particle
    active_shockwaves: list = field(default_factory=list)  # Shockwave

    # ── Chain / screen-shake ──────────────────────────────────────────────────
    active_chain:    "ChainDisplay | None" = None
    chain_count:     int                  = 0
    shake_frames:    int                  = 0
    shake_intensity: int                  = 0

    # ── Frame / idle animation ────────────────────────────────────────────────
    frame_count:            int  = 0
    need_score_update:      bool = False
    pop_played_this_frame:  bool = False

    # ── Restart memory ────────────────────────────────────────────────────────
    last_block_size:    int        = 40
    last_color_indices: list[int]  = field(default_factory=lambda: [0, 1, 2, 3])

    # ── Convenience ───────────────────────────────────────────────────────────

    @property
    def is_animating(self) -> bool:
        return bool(
            self.overflow_queue
            or self.active_particles
            or self.active_shockwaves
        )
