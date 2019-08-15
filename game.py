"""Main board and snake."""
import logging
import random

import numpy as np

LOGGER = logging.getLogger(__name__)


class Snake:
    """Snake object which can move within the board.

    Args:
        location ((int, int)): Initial position of the body's head.
        health (int, optional): Starting health of the body.

    """

    def __init__(self, location, health=100):
        #: int: Snake's health.  If it reaches 0 it is dead.  In general, each
        #: move will cost 1 health and is regenerated when eating apples.
        self.health = health
        #: int: Whether the snake is growing or not.  Whilst growing, each
        #: move will decrease `self.growth` by one and cause the snake's
        #: length to increase by 1 (effectively causing the tail to remain in the
        #: same location).
        self.growth = 0
        #: list((int, int)): List of segments of the snake's body, with
        #: the snake's head location at `self.body[0]` and the snake's tail at
        #: `self.body[-1]`.
        self.body = [location]
        #: (int, int): Previous location of the tail.  This may be None if the tail has not moved.
        self.previous_tail = None

    @property
    def head(self):
        """tuple: Location of the snake's head."""
        return self.body[0]

    @property
    def length(self):
        """int: Length of the snake."""
        return len(self.body)

    def __len__(self):
        return self.length

    def move_to(self, location, cost=0) -> bool:
        """Move the snake's head to the given location.

        Typically, the snake's head will move to location immediately adjacent,
        though this function can allow the snake to move to any other location
        on the board.  In the case of a jump, the snake's body will have a gap.

        Args:
            location ((int, int)): New location of the snake's head
            cost (int): How much health this move will cost.  This cost is
                subtracted from the snake's health and thus a negative cost will in
                fact add to the snake's health.

        Returns:
            A boolean as to whether the snake's move is allowed (``True``) or
            whether it has collided with something (``False``).
        """
        if self.growth > 0:
            self.previous_tail = None
            self.body = [location] + self.body
            self.growth -= 1
        else:
            self.previous_tail = self.body[-1]
            self.body = [location] + self.body[:-1]
        self.health -= cost

    def move_up(self, *args, **kwargs) -> bool:
        """Make the snake's head up by one.

        See :obj:`move_to` for more information.
        """
        self.move_to((self.body[0][0], self.body[0][1] - 1), *args, **kwargs)

    def move_down(self, *args, **kwargs) -> bool:
        """Move the snake's head down by one.

        See :obj:`move_to` for more information.
        """
        self.move_to((self.body[0][0], self.body[0][1] + 1), *args, **kwargs)

    def move_left(self, *args, **kwargs) -> bool:
        """Move the snake's head left by one.

        See :obj:`move_to` for more information.
        """
        self.move_to((self.body[0][0] - 1, self.body[0][1]), *args, **kwargs)

    def move_right(self, *args, **kwargs) -> bool:
        """Move the snake's head right by one.

        See :obj:`move_to` for more information.
        """
        self.move_to((self.body[0][0] + 1, self.body[0][1]), *args, **kwargs)


class Apple:
    """Apple object

    Args:
        location ((int, int)): Position of the apple.
        health (int): How much health the apple provides to the snake.
        growth (int): How much this causes the snake to grow.

    """

    def __init__(self, location, health=10, growth=1):
        self.location = location
        self.health = health
        self.growth = growth


class Board:
    """Board on which the game plays.

    Args:
        width (int): Width of the board
        height (int): Height of the board
        snakes (int): Number of snakes to add to the board.
        apples (int): Number of apples to be placed on the board at the
            beginning.
    """

    def __init__(self, width, height, snakes=1, apples=2):
        #: int: Board width
        self.width = width
        #: int: Board height
        self.height = height

        #: bool: Toggle to enable or disable drawing of the board and snakes.
        self.drawing_enabled = True

        #: list(Snake): List of snakes in the game.
        self.snakes = []
        for _ in range(snakes):
            self.add_snake()

        #: set(Apple): Location of the apples in the board
        self.apples = set()

        #: ndarray(bool): Grid of all locations which are occupied (``False``)
        #: or empty (``True``).
        self.empty = np.full((self.width, self.height), True, dtype=bool)

        for _ in range(apples):
            self.add_apple()

    @property
    def ended(self):
        """bool: Whether the game has ended or not.  A game is considered ended if all
        the snakes are dead."""
        return sum(snake.health for snake in self.snakes) == 0

    @property
    def empty_spaces(self):
        """list((int, int)): List of indices of empty spaces."""
        return np.argwhere(self.empty)

    def add_apple(self, location=None, **kwargs):
        """Add an apple to the game.

        Args:
            location ((int, int), option), optional: Location at which the
                apples should be placed. If this is specified and location is
                already occupied, an error is raised.

                If unspecified, the location will be chosen at random from the
                list of available sites, and if there are no available sites,
                no apple will be added.
            kwargs: Arguments passed on to the :obj:`Apple` initialization.

        """
        if location:
            if self.empty[location]:
                self.apples.add(Apple(location=location, **kwargs))
                self.empty[location] = False
            else:
                raise RuntimeError(f"Location {location} is already occupied.")
        else:
            try:
                location = random.choice(self.empty_spaces)
            except IndexError:
                raise RuntimeWarning(
                    f"There are no more empty locations to place the apple."
                )
            self.add_apple(location, **kwargs)

    def add_snake(self, location=None, **kwargs):
        """Add a snake to the game.

        Args:
            location ((int, int)), optional: Location at which the snake's head
                should be placed.  If this is specified and location is already
                occupied, an error is raised.

                If unspecified, the location will be chosen at random from the list of
                available sites, and if there are no available sites, no snake will be
                added.
            kwargs: Arguments passed on to the :obj:`Snake` initialization.

        """
        if location:
            if self.empty[location]:
                self.snakes.append(Snake(location=location, **kwargs))
                self.empty[location] = False
            else:
                raise RuntimeError(f"Location {location} is already occupied.")
        else:
            try:
                location = random.choice(self.empty_spaces)
            except IndexError:
                raise RuntimeWarning(
                    f"There are no more empty locations to place the snake."
                )
            self.add_snake(location, **kwargs)

    def process_move(self, snake):
        """Process the move from a particular snake.

        """
        # Remove the tail of the snake from the list of occupied spaces if it
        # has moved.
        if snake.previous_tail:
            self.empty[snake.previous_tail] = True

        # Check whether the snake's head is still on the grid
        if snake.head[0] < 0 or snake.head[1] < 0:
            snake.health = 0
            return
        if snake.head[0] >= self.width or snake.head[1] >= self.height:
            snake.health = 0
            return

        # Process whether the snake has eaten an apple
        for apple in self.apples:
            if snake.head == apple.location:
                snake.health += apple.health
                snake.growth += apple.growth
                self.apples.remove(apple)
                self.empty[snake.head] = True
                self.add_apple()
                return

        # Process whether the snake has collided with something
        if not self.empty[snake.head]:
            snake.health = 0
            return

        # Otherwise, mark the snake's new head location as occupied
        self.empty[snake.head] = False

    def draw(self, win):
        """Draw the game in the window."""
        if not self.drawing_enabled:
            return

        for snake in self.snakes:
            win.write("O", fgcolor="orange", x=snake[0][0], y=snake[0][1])
            if len(snake) > 1:
                for segment in snake[1:-1]:
                    win.write("#", fgcolor="red", x=segment[0], y=segment[1])
            win.write("#", fgcolor="yellow", x=snake[-1][0], y=snake[-1][1])

        for apple in self.apples:
            win.write("@", fgcolor="green", x=apple[0], y=apple[1])

        win.colors = ("black", "black")
        win.fill("x", region=(0, self.height, self.width, 4 + len(self.snakes)))
        win.colors = ("white", "black")
        for i, snake in enumerate(self.snakes):
            win.write(
                f"snake length is {len(snake)}",
                x=self.width // 2 - 9,
                y=self.height + i,
            )
