"""
main.py
-------
Entry point -- keeps this file intentionally thin.

Module layout
-------------
constants.py   window / colour / font configuration
assets.py      sound and image loading
effects.py     Particle, Shockwave, ChainDisplay
board.py       Spot cell model + Board grid container
state.py       GameState dataclass (shared mutable session data)
renderer.py    all Pygame drawing routines
menu.py        menu screens and navigation
game.py        game logic, chain-reaction simulation, game loop
"""
import asyncio

import pygame

from .game import game_loop
from .menu import run_menu


async def main() -> None:
    try:
        selection = await run_menu()
        while selection is not None:
            result = await game_loop(*selection)
            if result is None:
                break
            selection = await run_menu() if result == "menu" else result
    finally:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
