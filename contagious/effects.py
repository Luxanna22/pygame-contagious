"""
effects.py
──────────
Visual-only animation objects.  They are purely presentational — no game
logic lives here.

Classes
-------
Particle      – atom flying from one cell to a neighbour.
Shockwave     – expanding ring at explosion origin.
ChainDisplay  – persistent "CHAIN x N!" HUD element.
"""
from math import sin, cos, pi, radians

import pygame

from .constants import WHITE, PARTICLE_DUR, chain_font


# ── Particle ──────────────────────────────────────────────────────────────────

class Particle:
    """A single atom zipping from (sx, sy) → (tx, ty) over *duration* frames."""

    def __init__(
        self,
        sx: int, sy: int,
        tx: int, ty: int,
        color: tuple[int, int, int],
        duration: int = PARTICLE_DUR,
    ) -> None:
        self.sx, self.sy = sx, sy
        self.tx, self.ty = tx, ty
        self.color    = color
        self.duration = duration
        self.t        = 0
        self.done     = False

    def update(self) -> None:
        self.t += 1
        if self.t >= self.duration:
            self.done = True

    def draw(self, surf: pygame.Surface) -> None:
        p    = min(self.t / self.duration, 1.0)
        x    = self.sx + (self.tx - self.sx) * p
        y    = self.sy + (self.ty - self.sy) * p
        size = max(2, int(8 * (1 - p * 0.4)))
        pygame.draw.circle(surf, self.color, (int(x), int(y)), size)
        pygame.draw.circle(surf, WHITE,      (int(x), int(y)), max(1, size // 3))

    def draw_sparks(self, surf: pygame.Surface) -> None:
        """Small decorative sparks trailing the particle."""
        p = min(self.t / self.duration, 1.0)
        if p > 0.6:
            return
        x = self.sx + (self.tx - self.sx) * p
        y = self.sy + (self.ty - self.sy) * p
        for k in range(4):
            angle   = (self.t * 40 + k * 90) * pi / 180
            off     = int(5 * (1 - p))
            px, py  = int(x + cos(angle) * off), int(y + sin(angle) * off)
            pygame.draw.circle(surf, self.color, (px, py), 2)


# ── Shockwave ─────────────────────────────────────────────────────────────────

class Shockwave:
    """Expanding translucent ring centred on an explosion."""

    def __init__(
        self,
        x: int, y: int,
        color: tuple[int, int, int],
        cell_size: int,
        duration: int = 18,
    ) -> None:
        self.x, self.y  = x, y
        self.color      = color
        self.cell_size  = cell_size
        self.duration   = duration
        self.t          = 0
        self.done       = False

    def update(self) -> None:
        self.t += 1
        if self.t >= self.duration:
            self.done = True

    def draw(self, surf: pygame.Surface) -> None:
        p = self.t / self.duration
        r = int(p * self.cell_size * 1.1)
        if r <= 0:
            return
        alpha     = int(220 * (1 - p))
        thickness = max(1, int(4 * (1 - p * 0.7)))
        ring      = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(
            ring, (*self.color, alpha), (r + 3, r + 3), r, thickness
        )
        surf.blit(ring, (self.x - r - 3, self.y - r - 3))


# ── ChainDisplay ──────────────────────────────────────────────────────────────

class ChainDisplay:
    """
    Persistent "CHAIN x N!" banner shown at the top of the screen.
    Created when a chain reaches 2; updated in-place for every subsequent
    link; fades out once the chain resolves.
    """

    def __init__(
        self,
        n: int,
        x: int, y: int,
        color: tuple[int, int, int],
    ) -> None:
        self.x, self.y = x, y
        self.color     = color
        self.n         = n
        self.pop_t     = 0
        self.pop_dur   = 22
        self.fading    = False
        self.fade_t    = 0
        self.fade_dur  = 45
        self.done      = False

    def update_n(self, n: int, color: tuple[int, int, int]) -> None:
        """Called on each new chain link — animates only the counter."""
        self.n      = n
        self.color  = color
        self.pop_t  = 0
        self.fading = False
        self.fade_t = 0

    def start_fade(self) -> None:
        if not self.fading:
            self.fading = True
            self.fade_t = 0

    def update(self) -> None:
        if self.pop_t < self.pop_dur:
            self.pop_t += 1
        if self.fading:
            self.fade_t += 1
            if self.fade_t >= self.fade_dur:
                self.done = True

    def draw(self, surf: pygame.Surface) -> None:
        alpha = (
            255
            if not self.fading
            else int(255 * (1 - self.fade_t / self.fade_dur))
        )

        chain_ren = chain_font.render("CHAIN", True, self.color)
        chain_ren.set_alpha(alpha)
        cw, ch = chain_ren.get_size()

        p_pop     = min(self.pop_t / self.pop_dur, 1.0)
        pop_scale = 1.0 + 0.55 * sin(p_pop * pi)
        n_ren     = chain_font.render(f"x{self.n}!", True, WHITE)
        nw, nh    = n_ren.get_size()
        snw, snh  = max(1, int(nw * pop_scale)), max(1, int(nh * pop_scale))
        n_scaled  = pygame.transform.scale(n_ren, (snw, snh))
        n_scaled.set_alpha(alpha)

        total_w = cw + 10 + snw
        sx      = self.x - total_w // 2
        surf.blit(chain_ren, (sx,           self.y - ch  // 2))
        surf.blit(n_scaled,  (sx + cw + 10, self.y - snh // 2))
