"""
constants.py
────────────
Centralised configuration: window, colours, fonts, and tuning knobs.
All other modules import from here — no game logic lives here.
"""
import sys

import pygame

# Browser builds have no sound effects, so initialize only the modules they use.
# pygame.init() also initializes the mixer, which can stall the Pygbag startup gate.
if sys.platform == "emscripten":
    pygame.display.init()
    pygame.font.init()
else:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

# ── Window ────────────────────────────────────────────────────────────────────
WIDTH  = 600
HEIGHT = 600

display = pygame.display.set_mode((WIDTH, HEIGHT))
clock   = pygame.time.Clock()
pygame.display.set_caption("Contagious")

# ── Gameplay colours ──────────────────────────────────────────────────────────
BACKGROUND = (50,  50,  50)
BORDER     = (208, 211, 212)
RED        = (231, 76,  60)
WHITE      = (244, 246, 247)
VIOLET     = (136, 78,  160)
BLUE       = (52,  152, 219)
GREEN      = (88,  214, 141)

PLAYER_COLORS = [RED, GREEN, VIOLET, BLUE]
COLOR_LABELS  = ["Red",    "Green",  "Purple", "Blue"]
COLOR_NAMES   = ["RED",    "GREEN",  "PURPLE", "BLUE"]
PLAYER_NAMES  = ["PLAYER 1", "PLAYER 2", "PLAYER 3", "PLAYER 4"]

# ── Menu palette ─────────────────────────────────────────────────────────────
MENU_BG    = (14,  14,  26)
C_ACCENT   = (72,  214, 188)
C_DIM      = (90,  90,  115)
C_CARD_BG  = (26,  26,  44)
C_CARD_HOV = (38,  38,  62)
C_SEP      = (48,  48,  72)

# ── Fonts ────────────────────────────────────────────────────────────────────
font       = pygame.font.SysFont("Times New Roman", 30)
chain_font = pygame.font.SysFont("Times New Roman", 42, bold=True)
title_font = pygame.font.SysFont("Times New Roman", 56, bold=True)
sub_font   = pygame.font.SysFont("Times New Roman", 17)
label_font = pygame.font.SysFont("Times New Roman", 22)
small_font = pygame.font.SysFont("Times New Roman", 14)

# ── Animation settings ────────────────────────────────────────────────────────
ANIM_FPS     = 60   # target framerate
PARTICLE_DUR = 12   # frames a particle travels
