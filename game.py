"""Snake game"""
import logging
import random

LOGGER = logging.getLogger(__name__)


class Game:
    """Snake game class"""

    def __init__(self, width, height, snake_head_pos=None, apples=2):
        """Initialize a snake game with the specified width and height.

        The initial position of the snake's head can be specified by
        `snake_head_pos` which should be a tuple of the form `(x, y)`.

        The number of apples initially place on the board is specified by
        `apples`.

        """
        self.width = width
        self.height = height
        self.ended = False

        if snake_head_pos is None:
            snake_head_pos = (width // 2, height // 2)
        self.snake = [
            snake_head_pos,
            (snake_head_pos[0], snake_head_pos[1] + 1),
            (snake_head_pos[0], snake_head_pos[1] + 2),
        ]
        self.apples = set()
        self.health = 100
        self.digesting = 0

        self.whole_space = set(
            (i, j) for i in range(self.width) for j in range(self.height)
        )

        for _ in range(apples):
            self.make_apple()

    @property
    def snake_length(self):
        """Length of the snake"""
        return len(self.snake)

    @property
    def empty_spaces(self):
        """Return the set of indices corresponding to empty sites."""
        empty_spaces = self.whole_space - self.apples - set(self.snake)
        LOGGER.debug(f"Empty spaces: {len(empty_spaces)}")
        return empty_spaces

    def make_apple(self):
        """Add an apple to the game"""
        if len(self.empty_spaces) == 0:
            LOGGER.warn(f"There are no empty spaces to place an apple.")
            self.ended = True
        else:
            self.apples.add(random.choice(tuple(self.empty_spaces)))

    def move_up(self, costly=True):
        """Make the snake's head up by one"""
        if self.digesting > 0:
            self.snake = [(self.snake[0][0], self.snake[0][1] - 1)] + self.snake
            self.digesting -= 1
        else:
            self.snake = [(self.snake[0][0], self.snake[0][1] - 1)] + self.snake[:-1]

        self.check_move()
        if costly:
            self.health -= 1

    def move_down(self, costly=True):
        """Move the snake's head down by one"""
        if self.digesting > 0:
            self.snake = [(self.snake[0][0], self.snake[0][1] + 1)] + self.snake
            self.digesting -= 1
        else:
            self.snake = [(self.snake[0][0], self.snake[0][1] + 1)] + self.snake[:-1]

        self.check_move()
        if costly:
            self.health -= 1

    def move_left(self, costly=True):
        """Move the snake's head left by one"""
        if self.digesting > 0:
            self.snake = [(self.snake[0][0] - 1, self.snake[0][1])] + self.snake
            self.digesting -= 1
        else:
            self.snake = [(self.snake[0][0] - 1, self.snake[0][1])] + self.snake[:-1]

        self.check_move()
        if costly:
            self.health -= 1

    def move_right(self, costly=True):
        """Move the snake's head right by one"""
        if self.digesting > 0:
            self.snake = [(self.snake[0][0] + 1, self.snake[0][1])] + self.snake
            self.digesting -= 1
        else:
            self.snake = [(self.snake[0][0] + 1, self.snake[0][1])] + self.snake[:-1]

        self.check_move()
        if costly:
            self.health -= 1

    def check_move(self):
        """Perform checks after a move has been performed."""
        if self.has_collision():
            self.ended = True

        self.eat_apple()

    def has_collision(self):
        """Check if there has been a collision and return the position of the collision and type"""
        snake_head = self.snake[0]

        # Self collision of the snake
        if snake_head in self.snake[1:]:
            LOGGER.info(f"Self-collision at {snake_head}.")
            return True

        # Collision with boundary
        if (
            snake_head[0] < 0
            or snake_head[1] < 0
            or snake_head[0] >= self.width
            or snake_head[1] >= self.height
        ):
            LOGGER.info(f"Boundary collision at {snake_head}")
            return True

        return False

    def eat_apple(self):
        """Eat the apple if the head just move onto an apple's position"""
        if self.snake[0] in self.apples:
            LOGGER.info(f"Ate apple at position {self.snake[0]}.")
            self.apples.remove(self.snake[0])
            self.digesting += 1
            self.health += 10
            self.make_apple()

    def draw(self, win):
        win.write("O", fgcolor="orange", x=self.snake[0][0], y=self.snake[0][1])
        if len(self.snake) > 1:
            for segment in self.snake[1:-1]:
                win.write("#", fgcolor="red", x=segment[0], y=segment[1])
        win.write("#", fgcolor="yellow", x=self.snake[-1][0], y=self.snake[-1][1])
        if len(self.apples) != []:
            for apple in self.apples:
                win.write("@", fgcolor="green", x=apple[0], y=apple[1])

        win.colors = ("black", "black")
        win.fill("x", region=(0, self.height, self.width, 4))
        win.colors = ("white", "black")
        win.write(
            "snake length is {0}".format(self.snake_length),
            x=self.width // 2 - 9,
            y=self.height,
        )
