#!/usr/bin/env python
"""Curse GUI for the Snake game"""

import logging
import sys

import coloredlogs
import pygame
import pygame.locals as pl
import pygcurse

from game import Game

LOGGER = logging.getLogger(__name__)

WINWIDTH = 10
WINHEIGHT = 10

FPS = 40


def main():
    """Main function"""
    log_fmt = "%(asctime)s %(name)s[%(lineno)d] %(levelname)s %(message)s"
    coloredlogs.install(level=logging.DEBUG, fmt=log_fmt)
    win = pygcurse.PygcurseWindow(WINWIDTH, WINHEIGHT + 4, fullscreen=False)
    pygame.display.set_caption("Window Title")
    win.autoupdate = False
    clock = pygame.time.Clock()

    game = Game(WINWIDTH, WINHEIGHT)

    while not game.ended:
        win.fill(bgcolor="blue")
        handle_events(game)
        game.draw(win)
        win.update()
        clock.tick(FPS)


def handle_events(game):
    for event in pygame.event.get():
        LOGGER.log(5, "event: {0}".format(event))

        # Escape to quit
        if event.type == pl.QUIT or (
            event.type == pl.KEYDOWN and event.key == pl.K_ESCAPE
        ):
            terminate()

        # Check all other key presses
        if event.type == pl.KEYDOWN:
            if event.key == pl.K_UP or event.key == pl.K_w:
                game.move_up()
            elif event.key == pl.K_DOWN or event.key == pl.K_s:
                game.move_down()
            elif event.key == pl.K_LEFT or event.key == pl.K_a:
                game.move_left()
            elif event.key == pl.K_RIGHT or event.key == pl.K_d:
                game.move_right()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
