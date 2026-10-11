"""
menu.py
───────
Main-menu presentation and navigation logic.

Public API
----------
run_menu() -> tuple[int, int, list[int]]
    Blocks until the player finishes the three-step menu and returns
    (num_players, block_size, chosen_color_indices).
"""
from __future__ import annotations

import random
import asyncio
from math import cos, sin, radians

import pygame

from .constants import (
    display,
    WIDTH, HEIGHT,
    WHITE,
    PLAYER_COLORS, COLOR_LABELS,
    MENU_BG,
    C_ACCENT, C_DIM, C_CARD_BG, C_CARD_HOV, C_SEP,
    title_font, sub_font, label_font, small_font,
)


# ── Background floating particles ─────────────────────────────────────────────

class MenuParticle:
    """A single drifting virus icon shown behind the menu."""

    def __init__(self) -> None:
        self._reset(initial=True)

    def _reset(self, initial: bool = False) -> None:
        self.x     = random.uniform(0, WIDTH)
        self.y     = random.uniform(0, HEIGHT) if initial else float(HEIGHT + 12)
        self.r     = random.randint(4, 13)
        self.spd   = random.uniform(0.18, 0.60)
        self.col   = random.choice(PLAYER_COLORS)
        self.alpha = random.randint(22, 62)
        self.drift = random.uniform(-0.25, 0.25)
        self.rot   = random.uniform(0, 360)
        self.rot_s = random.uniform(-0.4, 0.4)

    def update(self) -> None:
        self.y   -= self.spd
        self.x   += self.drift
        self.rot  = (self.rot + self.rot_s) % 360
        if self.y < -20:
            self._reset()

    def draw(self, surf: pygame.Surface) -> None:
        sz = (self.r + 6) * 2 + 4
        s  = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = cy = sz // 2
        pygame.draw.circle(s, (*self.col, self.alpha), (cx, cy), self.r)
        for k in range(6):
            ang = radians(self.rot + k * 60)
            x1  = cx + int(self.r       * cos(ang))
            y1  = cy + int(self.r       * sin(ang))
            x2  = cx + int((self.r + 5) * cos(ang))
            y2  = cy + int((self.r + 5) * sin(ang))
            pygame.draw.line(s, (*self.col, self.alpha), (x1, y1), (x2, y2), 1)
        surf.blit(s, (int(self.x) - cx, int(self.y) - cy))


_menu_particles: list[MenuParticle] = [MenuParticle() for _ in range(38)]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _draw_menu_bg() -> None:
    display.fill(MENU_BG)
    for mp in _menu_particles:
        mp.update()
        mp.draw(display)


def _draw_card(
    rect: pygame.Rect,
    hovered: bool,
    accent_override: tuple[int, int, int] | None = None,
) -> None:
    col     = C_CARD_HOV if hovered else C_CARD_BG
    brd_col = (accent_override or C_ACCENT) if hovered else C_SEP
    brd_w   = 2 if hovered else 1
    pygame.draw.rect(display, col,     rect, border_radius=14)
    pygame.draw.rect(display, brd_col, rect, brd_w, border_radius=14)


# ── Sub-screen drawers ────────────────────────────────────────────────────────

def _draw_main(mx: int, my: int) -> pygame.Rect:
    """Draw the landing screen; returns the PLAY button rect."""
    t1 = title_font.render("CONTAGIOUS", True, WHITE)
    t2 = sub_font.render("spread. infect. dominate.", True, C_ACCENT)
    display.blit(t1, t1.get_rect(center=(WIDTH // 2, 168)))
    display.blit(t2, t2.get_rect(center=(WIDTH // 2, 222)))
    pygame.draw.line(display, C_SEP,
                     (WIDTH // 2 - 130, 244), (WIDTH // 2 + 130, 244), 1)

    play_rect = pygame.Rect(0, 0, 186, 52)
    play_rect.center = (WIDTH // 2, 318)
    hov = play_rect.collidepoint(mx, my)
    pygame.draw.rect(display, C_CARD_HOV if hov else C_CARD_BG,
                     play_rect, border_radius=26)
    pygame.draw.rect(display, C_ACCENT, play_rect, 2, border_radius=26)
    pt = label_font.render("PLAY", True, C_ACCENT if hov else WHITE)
    display.blit(pt, pt.get_rect(center=play_rect.center))

    cr  = small_font.render("(c) 2024  Rusiana", True, C_DIM)
    hnt = small_font.render("ESC to quit", True, C_DIM)
    display.blit(cr,  cr .get_rect(bottomright=(WIDTH - 14, HEIGHT - 10)))
    display.blit(hnt, hnt.get_rect(bottomleft=(14, HEIGHT - 10)))
    return play_rect


def _draw_players(
    mx: int, my: int,
    p_cards: list[dict],
) -> list[pygame.Rect]:
    """Draw the player-count selection screen; returns card rects."""
    h1 = label_font.render("SELECT PLAYERS", True, WHITE)
    display.blit(h1, h1.get_rect(center=(WIDTH // 2, 78)))
    pygame.draw.line(display, C_SEP,
                     (WIDTH // 2 - 100, 98), (WIDTH // 2 + 100, 98), 1)

    cw, ch  = 148, 188
    gap     = 22
    total_w = 3 * cw + 2 * gap
    sx      = (WIDTH - total_w) // 2
    p_rects: list[pygame.Rect] = []

    for idx, card in enumerate(p_cards):
        rect = pygame.Rect(sx + idx * (cw + gap), (HEIGHT - ch) // 2 - 14, cw, ch)
        p_rects.append(rect)
        hov = rect.collidepoint(mx, my)
        _draw_card(rect, hov)

        num_s = title_font.render(str(card["n"]), True,
                                  C_ACCENT if hov else WHITE)
        display.blit(num_s, num_s.get_rect(center=(rect.centerx, rect.top + 54)))

        dot_r, spc = 8, 22
        n_dots = len(card["colors"])
        dot_sx = rect.centerx - (n_dots * spc - spc + dot_r * 2) // 2 + dot_r
        for ci, col in enumerate(card["colors"]):
            dx = dot_sx + ci * spc
            pygame.draw.circle(display, col,   (dx, rect.top + 108), dot_r)
            pygame.draw.circle(display, WHITE, (dx, rect.top + 108), dot_r, 1)

        lbl_s = small_font.render(f"{card['n']} Players", True,
                                  C_ACCENT if hov else C_DIM)
        display.blit(lbl_s,
                     lbl_s.get_rect(center=(rect.centerx, rect.bottom - 18)))

    hnt = small_font.render("ESC to go back", True, C_DIM)
    display.blit(hnt, hnt.get_rect(bottomleft=(14, HEIGHT - 10)))
    return p_rects


def _draw_colors(
    mx: int, my: int,
    chosen_p: int,
    chosen_ci: list[int],
) -> tuple[list[list[pygame.Rect]], pygame.Rect]:
    """Draw the colour-picker screen; returns (swatch_rects, next_rect)."""
    h1 = label_font.render("CUSTOMIZE COLORS", True, WHITE)
    display.blit(h1, h1.get_rect(center=(WIDTH // 2, 52)))
    pygame.draw.line(display, C_SEP,
                     (WIDTH // 2 - 120, 70), (WIDTH // 2 + 120, 70), 1)

    p_names  = ["PLAYER 1", "PLAYER 2", "PLAYER 3", "PLAYER 4"]
    swatch_r = 16
    per_row  = chosen_p if chosen_p <= 3 else 2
    cw       = (WIDTH - 40) // per_row - 14
    ch       = 178
    rows_of_cards = (chosen_p + per_row - 1) // per_row
    gap      = 14
    total_w  = per_row * cw + (per_row - 1) * gap
    start_x  = (WIDTH  - total_w) // 2
    start_y  = 86

    swatch_rects: list[list[pygame.Rect]] = []

    for pi in range(chosen_p):
        row_i   = pi // per_row
        col_i   = pi %  per_row
        cx_card = start_x + col_i * (cw + gap)
        cy_card = start_y + row_i * (ch + gap)
        rect    = pygame.Rect(cx_card, cy_card, cw, ch)

        sel_color = PLAYER_COLORS[chosen_ci[pi]]

        pygame.draw.rect(display, C_CARD_BG, rect, border_radius=14)
        pygame.draw.rect(display, (*sel_color, 180), rect, 2, border_radius=14)

        strip = pygame.Rect(cx_card + 2, cy_card + 2, cw - 4, 28)
        strip_surf = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
        strip_surf.fill((*sel_color, 40))
        display.blit(strip_surf, strip.topleft)
        plbl = small_font.render(p_names[pi], True, sel_color)
        display.blit(plbl, plbl.get_rect(center=(rect.centerx, cy_card + 16)))

        big_r  = 28
        big_cx = rect.centerx
        big_cy = cy_card + 82
        pygame.draw.circle(display, sel_color, (big_cx, big_cy), big_r)
        pygame.draw.circle(display, WHITE,     (big_cx, big_cy), big_r, 2)
        cn_big = small_font.render(COLOR_LABELS[chosen_ci[pi]], True, WHITE)
        display.blit(cn_big, cn_big.get_rect(center=(big_cx, big_cy + big_r + 12)))

        n_sw    = len(PLAYER_COLORS)
        sw_spc  = min(swatch_r * 2 + 12, (cw - 20) // n_sw)
        sw_total = sw_spc * n_sw - (sw_spc - swatch_r * 2)
        sw_x0   = rect.centerx - sw_total // 2 + swatch_r
        sw_y    = cy_card + ch - 22

        row_sw: list[pygame.Rect] = []
        for ci in range(n_sw):
            scx     = sw_x0 + ci * sw_spc
            r_rect  = pygame.Rect(scx - swatch_r, sw_y - swatch_r,
                                  swatch_r * 2, swatch_r * 2)
            row_sw.append(r_rect)

            used_by_other = any(chosen_ci[k] == ci
                                for k in range(chosen_p) if k != pi)
            selected      = (chosen_ci[pi] == ci)
            hov_sw        = r_rect.collidepoint(mx, my)

            if used_by_other:
                dim_s = pygame.Surface((swatch_r * 2, swatch_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(dim_s, (*PLAYER_COLORS[ci], 45),
                                   (swatch_r, swatch_r), swatch_r)
                display.blit(dim_s, r_rect.topleft)
            else:
                pygame.draw.circle(display, PLAYER_COLORS[ci], (scx, sw_y), swatch_r)
                if selected:
                    pygame.draw.circle(display, WHITE,        (scx, sw_y), swatch_r + 4, 2)
                    pygame.draw.circle(display, (*sel_color, 120),
                                       (scx, sw_y), swatch_r + 7, 1)
                elif hov_sw:
                    pygame.draw.circle(display, C_ACCENT, (scx, sw_y), swatch_r + 3, 1)

        swatch_rects.append(row_sw)

    btn_y     = start_y + rows_of_cards * ch + rows_of_cards * gap + 4
    next_rect = pygame.Rect(0, 0, 160, 44)
    next_rect.center = (WIDTH // 2, btn_y + 22)
    hn = next_rect.collidepoint(mx, my)
    pygame.draw.rect(display, C_CARD_HOV if hn else C_CARD_BG,
                     next_rect, border_radius=22)
    pygame.draw.rect(display, C_ACCENT, next_rect, 2, border_radius=22)
    nt = label_font.render("NEXT  →", True, C_ACCENT if hn else WHITE)
    display.blit(nt, nt.get_rect(center=next_rect.center))

    hnt = small_font.render("ESC to go back", True, C_DIM)
    display.blit(hnt, hnt.get_rect(bottomleft=(14, HEIGHT - 10)))
    return swatch_rects, next_rect


def _draw_board(
    mx: int, my: int,
    chosen_p: int,
    board_cards: list[dict],
) -> list[pygame.Rect]:
    """Draw the board-size selection screen; returns card rects."""
    h1 = label_font.render("SELECT BOARD SIZE", True, WHITE)
    display.blit(h1, h1.get_rect(center=(WIDTH // 2, 78)))
    pygame.draw.line(display, C_SEP,
                     (WIDTH // 2 - 112, 98), (WIDTH // 2 + 112, 98), 1)

    cw, ch  = 148, 198
    gap     = 22
    total_w = 3 * cw + 2 * gap
    sx      = (WIDTH - total_w) // 2
    b_rects: list[pygame.Rect] = []

    for idx, card in enumerate(board_cards):
        rect = pygame.Rect(sx + idx * (cw + gap),
                           (HEIGHT - ch) // 2 - 14, cw, ch)
        b_rects.append(rect)
        hov = rect.collidepoint(mx, my)
        _draw_card(rect, hov)

        bl = label_font.render(card["label"], True, C_ACCENT if hov else WHITE)
        display.blit(bl, bl.get_rect(center=(rect.centerx, rect.top + 38)))

        gs = sub_font.render(card["grid"], True, WHITE if hov else C_DIM)
        display.blit(gs, gs.get_rect(center=(rect.centerx, rect.top + 68)))

        g_sz = 52
        cn   = card["cells"]
        cs   = g_sz // cn
        gx0  = rect.centerx - g_sz // 2
        gy0  = rect.top + 90
        for gr in range(cn):
            for gc in range(cn):
                cr2 = pygame.Rect(gx0 + gc * cs, gy0 + gr * cs, cs - 1, cs - 1)
                pygame.draw.rect(display, C_SEP, cr2, border_radius=1)

        dc = small_font.render(card["desc"], True, C_ACCENT if hov else C_DIM)
        display.blit(dc, dc.get_rect(center=(rect.centerx, rect.bottom - 18)))

    hnt  = small_font.render("ESC to go back", True, C_DIM)
    ps_t = small_font.render(f"{chosen_p} Players", True, C_ACCENT)
    display.blit(hnt,  hnt .get_rect(bottomleft=(14, HEIGHT - 10)))
    display.blit(ps_t, ps_t.get_rect(topright=(WIDTH - 14, 14)))
    return b_rects


# ── Public entry point ────────────────────────────────────────────────────────

async def run_menu() -> tuple[int, int, list[int]] | None:
    """
    Four-screen flow: Main → Players → Colors → Board size.

    Returns
    -------
    (num_players, block_size, chosen_color_indices)
    """
    MAIN, PLAYERS, COLOR, BOARD = 0, 1, 2, 3

    state       = MAIN
    chosen_p    = 2
    chosen_ci   = [0, 1]
    play_rect   = pygame.Rect(0, 0, 0, 0)
    p_rects:     list[pygame.Rect]             = []
    b_rects:     list[pygame.Rect]             = []
    swatch_rects: list[list[pygame.Rect]]      = []
    next_rect    = pygame.Rect(0, 0, 0, 0)

    p_cards = [
        {"n": 2, "colors": [PLAYER_COLORS[0], PLAYER_COLORS[1]]},
        {"n": 3, "colors": [PLAYER_COLORS[0], PLAYER_COLORS[1], PLAYER_COLORS[2]]},
        {"n": 4, "colors": PLAYER_COLORS[:]},
    ]
    board_cards = [
        {"bs": 75, "label": "Small",  "grid": "8 x 8",   "desc": "Intimate",  "cells": 4},
        {"bs": 50, "label": "Medium", "grid": "12 x 12", "desc": "Classic",   "cells": 5},
        {"bs": 40, "label": "Large",  "grid": "15 x 15", "desc": "Epic",      "cells": 6},
    ]

    mk = pygame.time.Clock()

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state > MAIN:
                    state -= 1
                else:
                    return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == MAIN:
                    if play_rect.collidepoint(mx, my):
                        state = PLAYERS

                elif state == PLAYERS:
                    for idx, card in enumerate(p_cards):
                        if idx < len(p_rects) and p_rects[idx].collidepoint(mx, my):
                            chosen_p  = card["n"]
                            chosen_ci = list(range(chosen_p))
                            swatch_rects = []
                            state     = COLOR

                elif state == COLOR:
                    for pi in range(chosen_p):
                        if pi < len(swatch_rects):
                            for ci in range(len(PLAYER_COLORS)):
                                if ci < len(swatch_rects[pi]):
                                    if swatch_rects[pi][ci].collidepoint(mx, my):
                                        used = [chosen_ci[k] for k in range(chosen_p) if k != pi]
                                        if ci not in used:
                                            chosen_ci[pi] = ci
                    if next_rect.collidepoint(mx, my):
                        state = BOARD

                elif state == BOARD:
                    for idx, card in enumerate(board_cards):
                        if idx < len(b_rects) and b_rects[idx].collidepoint(mx, my):
                            return chosen_p, card["bs"], chosen_ci

        _draw_menu_bg()

        if state == MAIN:
            play_rect = _draw_main(mx, my)
        elif state == PLAYERS:
            p_rects = _draw_players(mx, my, p_cards)
        elif state == COLOR:
            swatch_rects, next_rect = _draw_colors(mx, my, chosen_p, chosen_ci)
        elif state == BOARD:
            b_rects = _draw_board(mx, my, chosen_p, board_cards)

        pygame.display.update()
        mk.tick(60)
        await asyncio.sleep(0)
