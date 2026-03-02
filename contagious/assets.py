"""
assets.py
─────────
Loads and owns all external assets: sounds and images.
Call ``load_all()`` once after constants.py has initialised pygame.
"""
import pygame
from pathlib import Path
from constants import display, PLAYER_COLORS

# ── Sound ─────────────────────────────────────────────────────────────────────
_ASSETS_ROOT = Path(__file__).parent
_SOUNDS_DIR = _ASSETS_ROOT / "sounds"
_IMAGES_DIR = _ASSETS_ROOT / "images"

try:
    _pop_path = _SOUNDS_DIR / "pop-sound.mp3"
    pop_sound: pygame.mixer.Sound | None = pygame.mixer.Sound(str(_pop_path))
    pop_sound.set_volume(0.45)
except Exception:
    pop_sound = None

# ── Window icon ───────────────────────────────────────────────────────────────
_icon_raw = pygame.image.load(str(_IMAGES_DIR / "covid_red.png"))
pygame.display.set_icon(_icon_raw)

# ── Per-player source images (full-resolution) ────────────────────────────────
_PLAYER_IMAGE_FILES = [
    _IMAGES_DIR / "covid_red.png",
    _IMAGES_DIR / "covid_green.png",
    _IMAGES_DIR / "covid_purple.png",
    _IMAGES_DIR / "covid_blue.png",
]

base_player_imgs: list[pygame.Surface] = [
    pygame.image.load(str(path)) for path in _PLAYER_IMAGE_FILES
]


def build_player_imgs(size: int) -> list[pygame.Surface]:
    """Return a list of ``size × size`` player images for all four slots."""
    return [pygame.transform.scale(img, (size, size)) for img in base_player_imgs]


def build_player_imgs_for_indices(
    indices: list[int], size: int
) -> list[pygame.Surface]:
    """Return player images scaled to *size* for the chosen colour indices."""
    return [
        pygame.transform.scale(base_player_imgs[ci], (size, size))
        for ci in indices
    ]
