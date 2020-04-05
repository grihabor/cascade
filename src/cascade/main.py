import itertools

import pygame
import pygame.examples.aliens as aliens
from pygame.sprite import Sprite
from pygame import Rect


SCREENRECT = Rect(0, 0, 900, 600)


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
        surf = pygame.Surface((50, 50))
        pygame.draw.circle(surf, (0, 0, 255), (25, 25), 25)
        small = 2
        big = 25
        pygame.draw.rect(surf, (255, 255, 255), rect1(small, big))
        pygame.draw.rect(surf, (255, 255, 255), rect2(small, big))
        return surf


class Ball(Sprite):
    def __init__(self, surfaces: Surfaces, i: int, center):
        super().__init__()
        self.i = i
        self.center = (50 + center[0] * 50, 50 + center[1] * 50)
        self.surfaces = surfaces

    def rect(self):
        surf = self.surfaces[self.i]
        return surf.get_rect(center=self.center)

    def surf(self):
        surf = self.surfaces[self.i]
        return surf, surf.get_rect(center=self.center)

    def rotate(self):
        self.i = (self.i + 1) % 4


class App:
    def __init__(self):
        winstyle = 0
        bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
        pygame.display.set_caption("Cascade")
        self.running = True

    def run(self):

        surfaces = Surfaces()
        balls = pygame.sprite.Group()

        grid_size = 5
        for i, j in itertools.product(range(grid_size), range(grid_size)):
            balls.add(Ball(surfaces, 0, (i, j)))

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for s in balls:
                        assert isinstance(s, Ball)
                        if s.rect().collidepoint(event.pos):
                            s.rotate()

            for ball in balls:
                surf, rect = ball.surf()
                self.screen.blit(surf, rect)
            pygame.display.flip()
        pygame.quit()


def main(winstyle=0):
    pygame.init()
    App().run()
    pygame.quit()
