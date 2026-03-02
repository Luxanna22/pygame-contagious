"""
renderer.py
───────────
All Pygame drawing routines.  No game logic lives here — functions
receive ``GameState`` (or individual pieces of state) and paint to
``constants.display``.
"""
from __future__ import annotations

from math import cos, sin, radians, pi

import pygame

from constants import (
    display,
    WIDTH, HEIGHT,
    BACKGROUND, BORDER, WHITE,
    PLAYER_COLORS, COLOR_NAMES, PLAYER_NAMES,
    C_SEP, C_ACCENT, C_DIM, C_CARD_BG,
    title_font, label_font, small_font,
)
from state import GameState


# ── Grid lines ────────────────────────────────────────────────────────────────

def draw_grid(state: GameState) -> None:
    """Draw the thin grid lines using the current player's colour."""
    current_color = state.players[state.active_players[state.current_player]]
    for k in range(1, state.cols + 1):
        x = k * state.blocks
        pygame.draw.line(display, current_color, (x, 0), (x, HEIGHT))
    for k in range(1, state.rows + 1):
        y = k * state.blocks
        pygame.draw.line(display, current_color, (0, y), (WIDTH, y))


# ── Cell contents ─────────────────────────────────────────────────────────────

def draw_cells(state: GameState) -> None:
    """Render every occupied cell with its rotating virus image(s)."""
    grid   = state.board.grid
    blocks = state.blocks
    d      = state.d
    padding = 2

    for i in range(state.cols):
        for j in range(state.rows):
            cell = grid[i][j]
            if cell.noAtoms == 0:
                cell.color = BORDER
                continue

            x0 = i * blocks
            y0 = j * blocks

            spd, phase = state.board.cell_anim_data.get((i, j), (0.3, 0))

            near_overflow = (cell.noAtoms == len(cell.neighbors) - 1)
            if near_overflow:
                spd = spd * 4.0
                x0 += int(sin(state.frame_count * 1.7 + i * 3.1))
                y0 += int(cos(state.frame_count * 1.9 + j * 2.7))

            angle = (state.frame_count * spd + phase) % 360

            try:
                idx = state.players.index(cell.color)
            except ValueError:
                continue
            img = state.player_imgs[idx]

            if cell.noAtoms == 1:
                rotated = pygame.transform.rotate(img, angle)
                display.blit(rotated, (x0 + padding, y0 + padding))

            elif cell.noAtoms == 2:
                rotated = pygame.transform.rotate(img, angle)
                display.blit(rotated, (x0 + padding,     y0 + padding))
                display.blit(rotated, (x0 + padding + 9, y0 + padding))

            elif cell.noAtoms == 3:
                for k, dangle in enumerate([0, 120, 240]):
                    xi = x0 + (d / 2) * cos(radians(angle + dangle)) + blocks / 4
                    yi = y0 + (d / 2) * sin(radians(angle + dangle)) + blocks / 4
                    display.blit(img, (xi, yi))

            else:  # >= 4
                for dangle in [0, 90, 180, 270]:
                    xi = x0 + (d / 2) * cos(radians(angle + dangle)) + blocks / 4
                    yi = y0 + (d / 2) * sin(radians(angle + dangle)) + blocks / 4
                    display.blit(img, (xi, yi))


# ── HUD / effects ─────────────────────────────────────────────────────────────

def draw_effects(state: GameState) -> None:
    """Draw shockwaves, particles, sparks, and the chain banner."""
    for sw in state.active_shockwaves:
        sw.draw(display)
    for p in state.active_particles:
        p.draw(display)
        p.draw_sparks(display)
    if state.active_chain is not None:
        state.active_chain.draw(display)


# ── Winner overlay ────────────────────────────────────────────────────────────

def draw_win_overlay(state: GameState) -> None:
    """Animated winner card rendered on top of the still-running game."""
    winner_idx = state.game_over_winner
    t          = state.win_anim_t
    w_color    = state.players[winner_idx]

    try:
        ci = PLAYER_COLORS.index(w_color)
    except ValueError:
        ci = winner_idx

    winner_name = PLAYER_NAMES[winner_idx] if winner_idx < len(PLAYER_NAMES) else "PLAYER"
    color_name  = COLOR_NAMES[ci]           if ci        < len(COLOR_NAMES)   else ""

    # Semi-transparent dim
    dim = min(int(180 * min(t / 30.0, 1.0)), 180)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, dim))
    display.blit(overlay, (0, 0))

    if t < 12:
        return

    pulse = 0.5 + 0.5 * sin(t * 0.07 * pi)

    card_w, card_h = 340, 230
    card_rect = pygame.Rect(0, 0, card_w, card_h)
    card_rect.center = (WIDTH // 2, HEIGHT // 2)

    # Card shadow
    shadow_surf = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 90),
                     (0, 0, card_w + 20, card_h + 20), border_radius=22)
    display.blit(shadow_surf, (card_rect.left - 10, card_rect.top - 10))

    # Card body
    pygame.draw.rect(display, (18, 18, 32), card_rect, border_radius=18)

    # Pulsing glowing border
    glow_alpha = int(160 + 95 * pulse)
    for thickness, alpha_mod in [(6, 40), (4, 80), (2, 180)]:
        sz    = card_w + thickness * 4, card_h + thickness * 4
        ring  = pygame.Surface(sz, pygame.SRCALPHA)
        pygame.draw.rect(
            ring,
            (*w_color, int(glow_alpha * alpha_mod // 255)),
            (0, 0, *sz),
            thickness, border_radius=20,
        )
        display.blit(ring, (card_rect.left - thickness * 2,
                            card_rect.top  - thickness * 2))

    # Crown star
    crown_y  = card_rect.top + 34
    star_pts = []
    for k in range(10):
        ang = radians(-90 + k * 36)
        r2  = 13 if k % 2 == 0 else 5
        star_pts.append((WIDTH // 2 + r2 * cos(ang), crown_y + r2 * sin(ang)))
    pygame.draw.polygon(display, w_color, star_pts)

    # Winner name
    name_surf = title_font.render(winner_name, True, w_color)
    display.blit(name_surf, name_surf.get_rect(
        center=(WIDTH // 2, card_rect.top + 100)))

    # "WINS!" subtitle
    sub_col = tuple(min(255, int(c * 0.7 + 255 * 0.3 * pulse)) for c in w_color)
    wins_s  = label_font.render(f"{color_name}  •  WINS!", True, sub_col)
    display.blit(wins_s, wins_s.get_rect(
        center=(WIDTH // 2, card_rect.top + 148)))

    # Divider
    pygame.draw.line(display, (*w_color, 80),
                     (card_rect.left + 30, card_rect.top + 172),
                     (card_rect.right - 30, card_rect.top + 172), 1)

    # Hints
    hint1 = small_font.render("SPACE  restart", True, (180, 180, 200))
    hint2 = small_font.render("ESC  main menu", True, (180, 180, 200))
    display.blit(hint1, hint1.get_rect(center=(WIDTH // 2 - 75, card_rect.top + 205)))
    display.blit(hint2, hint2.get_rect(center=(WIDTH // 2 + 75, card_rect.top + 205)))
    pygame.draw.circle(display, (100, 100, 130), (WIDTH // 2, card_rect.top + 205), 2)


# ── Full frame ────────────────────────────────────────────────────────────────

def render_frame(state: GameState) -> None:
    """Composite one complete game frame onto ``display``."""
    display.fill(BACKGROUND)
    if state.active_players:
        draw_grid(state)
        draw_cells(state)
    draw_effects(state)
    if state.game_over_winner >= 0:
        draw_win_overlay(state)
    pygame.display.update()
