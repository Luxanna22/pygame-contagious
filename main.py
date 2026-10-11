# /// script
# dependencies = [
#   "pygame-ce",
# ]
# ///
"""Pygbag entry point for the Contagious browser build."""
import asyncio
import pygame  # Load the browser Pygame package before project modules.

from contagious.main import main


asyncio.run(main())
