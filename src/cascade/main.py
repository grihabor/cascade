import itertools
import queue
import random
from typing import Tuple, Dict

import pygame
from pygame.sprite import Sprite
from pygame import Rect


SCREENRECT = Rect(0, 0, 900, 600)

EVENT_CASCADE_TICK = pygame.USEREVENT + 1
pygame.time.set_timer(EVENT_CASCADE_TICK, 100)


class Surfaces:
    def __init__(self):
        self.surfaces = [
            self._new(self._right, self._down),
            self._new(self._down, self._left),
            self._new(self._left, self._up),
            self._new(self._up, self._right),
        ]

    def __getitem__(self, item):
        return self.surfaces[item]

    def _down(self, small, big):
        return Rect(big - small, big - small, 2 * small, small + big)

    def _right(self, small, big):
        return Rect(big - small, big - small, small + big, 2 * small,)

    def _left(self, small, big):
        return Rect(0, big - small, small + big, 2 * small,)

    def _up(self, small, big):
        return Rect(big - small, 0, 2 * small, small + big,)

    def _new(self, rect1, rect2):
        return [
            self._new_color(rect1, rect2, (0, 0, 255)),
            self._new_color(rect1, rect2, (0, 255, 0)),
            self._new_color(rect1, rect2, (255, 0, 0)),
        ]

    def _new_color(self, rect1, rect2, color):
        surf = pygame.Surface((50, 50))
        pygame.draw.circle(surf, color, (25, 25), 25)
        small = 2
        big = 25
        pygame.draw.rect(surf, (255, 255, 255), rect1(small, big))
        pygame.draw.rect(surf, (255, 255, 255), rect2(small, big))
        return surf


class Ball(Sprite):
    def __init__(
        self,
        surfaces: Surfaces,
        rotation: int,
        center,
        balls_to_rotate: queue.Queue,
        color: int,
    ):
        super().__init__()
        self.center = center
        self.rotation = rotation
        self.center_pos = (50 + center[0] * 50, 50 + center[1] * 50)
        self.surfaces = surfaces
        self.neighbors: Dict[int, Ball] = {}
        self.balls_to_rotate = balls_to_rotate
        self.color = color

    def rect(self):
        surf = self.surfaces[self.rotation][self.color]
        return surf.get_rect(center=self.center_pos)

    def surf(self) -> Tuple[pygame.Surface, Rect]:
        surf = self.surfaces[self.rotation][self.color]
        return surf, surf.get_rect(center=self.center_pos)

    def move_ip(self, x, y):
        self.center_pos = (self.center_pos[0] + x, self.center_pos[1] + y)

    def rotate(self, color=None):
        i = (self.rotation + 1) % 4
        self.rotation = i
        neighbor = self.neighbors.get(i)
        if neighbor is not None:
            if self.match(neighbor):
                self.balls_to_rotate.put((neighbor, self.color))

        if color is not None:
            self.color = color

    def set_left(self, ball: "Ball"):
        self.neighbors[3] = ball

    def set_down(self, ball: "Ball"):
        self.neighbors[0] = ball

    def set_right(self, ball: "Ball"):
        self.neighbors[1] = ball

    def set_up(self, ball: "Ball"):
        self.neighbors[2] = ball

    def match(self, other: "Ball"):
        if other.rotation == self.rotation:
            return False
        if other.rotation == (self.rotation + 1) % 4:
            return False
        return True


class App:
    def __init__(self):
        winstyle = 0
        bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
        pygame.display.set_caption("Cascade")
        self.running = True

        self.balls_to_rotate = queue.LifoQueue()

        surfaces = Surfaces()
        balls = {}

        grid_size = 10
        grid = list(itertools.product(range(grid_size), range(grid_size)))
        for i, j in grid:
            balls[i, j] = Ball(
                surfaces=surfaces,
                rotation=random.randint(0, 3),
                center=(i, j),
                balls_to_rotate=self.balls_to_rotate,
                color=random.randint(0, 2),
            )

        grid_rect = Rect(0, 0, 0, 0)
        for ball in balls.values():
            grid_rect.union_ip(ball.rect())
        shift = (
            SCREENRECT.width / 2 - grid_rect.width / 2,
            SCREENRECT.height / 2 - grid_rect.height / 2,
        )

        for ball in balls.values():  # type: Ball
            ball.move_ip(*shift)

        def ok(i, j):
            return i >= 0 and j >= 0 and i < grid_size and j < grid_size

        for i, j in grid:
            if ok(i + 1, j):
                balls[i, j].set_left(balls[i + 1, j])
            if ok(i, j + 1):
                balls[i, j].set_down(balls[i, j + 1])
            if ok(i - 1, j):
                balls[i, j].set_right(balls[i - 1, j])
            if ok(i, j - 1):
                balls[i, j].set_up(balls[i, j - 1])

        self.balls = pygame.sprite.Group(*[b for b in balls.values()])

    def run(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for ball in self.balls:
                        assert isinstance(ball, Ball)
                        if ball.rect().collidepoint(event.pos):
                            ball.rotate()
                elif event.type == EVENT_CASCADE_TICK:
                    if not self.balls_to_rotate.empty():
                        ball, color = self.balls_to_rotate.get()
                        ball.rotate(color=color)

            for ball in self.balls:  # type: Ball
                surf, rect = ball.surf()
                self.screen.blit(surf, rect)

            pygame.display.flip()

        pygame.quit()


def main(winstyle=0):
    pygame.init()
    app = App()
    app.run()
    pygame.quit()
