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
from menu import run_menu
from game import game_loop


def main() -> None:
    num_players, block_size, chosen_colors = run_menu()
    game_loop(num_players, block_size, chosen_colors)


if __name__ == "__main__":
    main()