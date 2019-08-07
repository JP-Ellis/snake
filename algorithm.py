#!/usr/bin/env python
"""Curse GUI for the Snake game"""

import logging
import random
import sys
import time
from multiprocessing import Pool

import coloredlogs
import matplotlib.pyplot as pyplot
import numpy as np
import pygame
import pygame.locals as pl
import pygcurse

from game import Game

LOGGER = logging.getLogger(__name__)

WINWIDTH = 10
WINHEIGHT = 10

FPS = 100


def main():
    """Main function"""
    log_fmt = "%(asctime)s %(name)s[%(lineno)d] %(levelname)s %(message)s"
    # coloredlogs.install(level=logging.DEBUG, fmt=log_fmt)
    coloredlogs.install(level=1000, fmt=log_fmt)

    size = 10_000
    results = np.zeros(size)
    with Pool() as pool:
        for idx, result in enumerate(
            pool.imap_unordered(run_random_walk, (False for _ in range(size)))
        ):
            results[idx] = result

    lengths, freqs = np.unique(results, return_counts=True)
    fig, ax = pyplot.subplots()
    ax.plot(lengths, freqs / size)
    ax.set_xlabel("Snake length")
    ax.set_ylabel("Frequency")
    fig.savefig("snake_lengths.pdf")


def run_random_walk(draw=False):
    """Run the random walk and return the final snake length.

    Drawing may be enabled.

    """
    game = Game(WINWIDTH, WINHEIGHT)
    game.drawing_enabled = draw

    if game.drawing_enabled:
        win = pygcurse.PygcurseWindow(WINWIDTH, WINHEIGHT + 4, fullscreen=False)
        pygame.display.set_caption("Window Title")
        win.autoupdate = False
        clock = pygame.time.Clock()

        while not game.ended:
            for event in pygame.event.get():
                LOGGER.log(5, f"event: {event}")

                # Escape to quit
                if event.type == pl.QUIT or (
                    event.type == pl.KEYDOWN and event.key == pl.K_ESCAPE
                ):
                    terminate()

            win.fill(bgcolor="blue")
            random_walk(game)
            game.draw(win)
            win.update()
            clock.tick(FPS)
    else:
        while not game.ended:
            random_walk(game)
    return game.snake_length


def random_walk(game):
    """A nearly random walk.

    If there is an apple, in the immediate vicinity, it will eat it; otherwise,
    it will just do a random walk until there are no more moves available while
    avoiding itself and walls.

    """
    LOGGER.info(f"Final snake length: {game.snake_length}")
    # Get a random direction
    directions = {
        (game.snake_head[0] + 1, game.snake_head[1]),
        (game.snake_head[0] - 1, game.snake_head[1]),
        (game.snake_head[0], game.snake_head[1] + 1),
        (game.snake_head[0], game.snake_head[1] - 1),
    }

    apple_directions = directions & game.apples
    if apple_directions:
        game.move_to(random.sample(apple_directions, 1)[0])
    else:
        valid_directions = directions & game.empty_spaces
        if valid_directions:
            game.move_to(random.sample(valid_directions, 1)[0])
        else:
            LOGGER.warning("No more moves available.")
            game.ended = True

    # time.sleep(0.1)


def terminate():
    sys.exit()


if __name__ == "__main__":
    main()
