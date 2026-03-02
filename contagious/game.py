"""
game.py
───────
Game logic: state construction, atom mutation, chain-reaction simulation,
and the main game loop.

Public API
----------
game_loop(num_players, block_size, chosen_color_indices)
    Starts (or restarts) a complete game session.  Blocks until the
    player quits or returns to the menu.
"""
from __future__ import annotations

import sys

import pygame

from assets import pop_sound, base_player_imgs, build_player_imgs_for_indices
from board import Board
from constants import (
    clock,
    WIDTH, HEIGHT,
    PLAYER_COLORS, BORDER,
    ANIM_FPS,
)
from effects import ChainDisplay, Particle, Shockwave
from menu import run_menu
from renderer import render_frame
from state import GameState


# ── State factory ─────────────────────────────────────────────────────────────

def build_game_state(
    num_players: int,
    block_size: int,
    chosen_color_indices: list[int],
) -> GameState:
    """Construct a fresh ``GameState`` for the given configuration."""
    blocks = block_size
    cols   = WIDTH  // blocks
    rows   = HEIGHT // blocks
    d      = blocks // 2 - 2
    img_sz = max(16, blocks - 13)

    players     = [PLAYER_COLORS[ci] for ci in chosen_color_indices]
    player_imgs = build_player_imgs_for_indices(chosen_color_indices, img_sz)
    board       = Board(cols, rows)

    return GameState(
        board             = board,
        blocks            = blocks,
        cols              = cols,
        rows              = rows,
        d                 = d,
        num_players       = num_players,
        players           = players,
        player_imgs       = player_imgs,
        active_players    = list(range(num_players)),
        scores            = [0] * num_players,
        last_block_size   = block_size,
        last_color_indices = chosen_color_indices,
    )


# ── Atom / overflow logic ─────────────────────────────────────────────────────

def add_atom(
    state: GameState,
    i: int, j: int,
    color: tuple[int, int, int],
) -> None:
    """
    Place one atom of *color* at (i, j).
    Enqueues an overflow explosion if the cell is now at or over its limit.
    """
    cell = state.board.cell(i, j)
    if cell.noAtoms < cell.limit:
        cell.noAtoms += 1
        cell.color    = color
        if cell.noAtoms >= len(cell.neighbors):
            cell.noAtoms = 0
            state.overflow_queue.append((i, j, color))


def _apply_atom(
    state: GameState,
    i: int, j: int,
    color: tuple[int, int, int],
) -> None:
    """Direct atom addition used by the animation system (particles landing)."""
    cell = state.board.cell(i, j)
    if cell.noAtoms < cell.limit:
        cell.noAtoms += 1
        cell.color    = color
        if cell.noAtoms >= len(cell.neighbors):
            cell.noAtoms = 0
            state.overflow_queue.append((i, j, color))


def _trigger_explosion(state: GameState) -> None:
    """Pop the next overflow from the queue and spawn its animations."""
    if not state.overflow_queue:
        return

    i, j, color = state.overflow_queue.pop(0)

    if pop_sound and not state.pop_played_this_frame:
        pop_sound.play()
        state.pop_played_this_frame = True

    cell        = state.board.cell(i, j)
    cell.noAtoms = 0

    state.chain_count += 1
    cx = i * state.blocks + state.blocks // 2
    cy = j * state.blocks + state.blocks // 2

    state.active_shockwaves.append(Shockwave(cx, cy, color, state.blocks))

    for ni, nj in state.board.get_neighbors(i, j):
        tx = ni * state.blocks + state.blocks // 2
        ty = nj * state.blocks + state.blocks // 2
        state.active_particles.append(Particle(cx, cy, tx, ty, color))
        state.pending_adds.append((ni, nj, color))

    if state.chain_count >= 2:
        state.shake_frames    = max(state.shake_frames, 6)
        state.shake_intensity = max(state.shake_intensity,
                                    min(state.chain_count + 1, 4))

    if state.chain_count == 2:
        state.active_chain = ChainDisplay(
            state.chain_count, WIDTH // 2, 28, color
        )
    elif state.chain_count > 2 and state.active_chain is not None:
        state.active_chain.update_n(state.chain_count, color)


# ── Score / active-player helpers ─────────────────────────────────────────────

def _refresh_scores(state: GameState) -> None:
    """Recount atoms per player, update ``state.scores``."""
    scores = [0] * state.num_players
    for col in state.board.grid:
        for cell in col:
            if cell.noAtoms > 0 and cell.color in state.players:
                idx = state.players.index(cell.color)
                scores[idx] += cell.noAtoms
    state.scores = scores


def _active_players_after_turn(state: GameState) -> list[int]:
    """Return indices of players still alive (score > 0)."""
    _refresh_scores(state)
    return [i for i in range(state.num_players) if state.scores[i] > 0]


def _count_active_colors(state: GameState) -> set[tuple[int, int, int]]:
    """All player colours present on the board or in-flight."""
    present: set[tuple[int, int, int]] = set()
    for col in state.board.grid:
        for cell in col:
            if cell.noAtoms > 0 and cell.color != BORDER:
                present.add(cell.color)
    for p in state.active_particles:
        if p.color in state.players:
            present.add(p.color)
    for _, _, color in state.pending_adds:
        if color in state.players:
            present.add(color)
    for _, _, color in state.overflow_queue:
        if color in state.players:
            present.add(color)
    return present


# ── Animation tick ────────────────────────────────────────────────────────────

def _tick_animations(state: GameState) -> None:
    """Advance all active animation objects by one frame."""
    for p  in state.active_particles:   p.update()
    for sw in state.active_shockwaves:  sw.update()
    state.active_particles[:]  = [p  for p  in state.active_particles  if not p.done]
    state.active_shockwaves[:] = [sw for sw in state.active_shockwaves if not sw.done]

    # Particles landed → commit pending neighbour additions
    if not state.active_particles and state.pending_adds:
        for ai, aj, acol in state.pending_adds:
            _apply_atom(state, ai, aj, acol)
        state.pending_adds.clear()

    # All particles committed → trigger queued explosions
    if not state.active_particles and not state.pending_adds:
        while state.overflow_queue:
            _trigger_explosion(state)

    # Chain fully resolved
    if not state.overflow_queue and not state.active_particles and not state.pending_adds:
        if state.need_score_update:
            state.need_score_update = False
            state.active_players    = _active_players_after_turn(state)
            if state.current_player >= len(state.active_players):
                state.current_player = max(0, len(state.active_players) - 1)
        state.chain_count = 0

    # Chain banner fade
    if state.active_chain is not None:
        if not state.is_animating:
            state.active_chain.start_fade()
        state.active_chain.update()
        if state.active_chain.done:
            state.active_chain = None


# ── Win detection ─────────────────────────────────────────────────────────────

def _check_win(state: GameState) -> None:
    """Set ``state.game_over_winner`` if a single colour has won."""
    if state.game_over_winner >= 0 or state.turns < state.num_players:
        return
    present = _count_active_colors(state)
    if len(present) == 1:
        winning_color = next(iter(present))
        if winning_color in state.players:
            state.game_over_winner = state.players.index(winning_color)
            state.win_anim_t       = 0


# ── Main game loop ────────────────────────────────────────────────────────────

def game_loop(
    num_players: int,
    block_size: int = 40,
    chosen_color_indices: list[int] | None = None,
) -> None:
    """
    Run one complete game session.  Calls itself recursively on restart, or
    re-runs the menu on ESC.  Returns only when the player quits to menu and
    that menu returns (control handed back to ``main``).
    """
    if chosen_color_indices is None:
        chosen_color_indices = list(range(num_players))

    state = build_game_state(num_players, block_size, chosen_color_indices)

    while True:
        # ── Input ─────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if state.game_over_winner >= 0:
                    if event.key == pygame.K_SPACE:
                        game_loop(
                            state.num_players,
                            state.last_block_size,
                            state.last_color_indices,
                        )
                        return
                    if event.key == pygame.K_ESCAPE:
                        n, bs, cc = run_menu()
                        game_loop(n, bs, cc)
                        return

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and not state.is_animating
                and state.game_over_winner < 0
            ):
                mx, my = event.pos
                i = mx // state.blocks
                j = my // state.blocks
                cur_color = state.players[state.active_players[state.current_player]]
                cell      = state.board.cell(i, j)
                if cell.color == cur_color or cell.color == BORDER:
                    state.turns += 1
                    add_atom(state, i, j, cur_color)
                    state.current_player += 1
                    if state.current_player >= len(state.active_players):
                        state.current_player = 0
                    if state.turns >= state.num_players:
                        state.need_score_update = True

        # ── Animate ───────────────────────────────────────────────────────────
        state.pop_played_this_frame = False
        state.frame_count          += 1
        _tick_animations(state)
        _check_win(state)

        if state.game_over_winner >= 0:
            state.win_anim_t += 1

        # ── Render ────────────────────────────────────────────────────────────
        render_frame(state)
        clock.tick(ANIM_FPS)
