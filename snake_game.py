"""A simple Snake game built with pygame.

Controls:
- Arrow keys or WASD: change direction
- P: pause/resume
- R: restart after game over, or restart any time
- Esc: quit
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
import pygame

CELL_SIZE = 24
GRID_WIDTH = 30
GRID_HEIGHT = 22
SIDEBAR_HEIGHT = 56
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + SIDEBAR_HEIGHT
FPS = 12

BACKGROUND = (24, 27, 35)
GRID_LINE = (36, 40, 51)
SNAKE_HEAD = (78, 205, 196)
SNAKE_BODY = (50, 168, 154)
FOOD = (255, 99, 99)
TEXT = (235, 239, 245)
MUTED_TEXT = (170, 178, 191)
OVERLAY = (8, 10, 14)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self) -> "Direction":
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def move(self, direction: Direction) -> "Point":
        dx, dy = direction.value
        return Point(self.x + dx, self.y + dy)


class SnakeGame:
    """Encapsulates Snake game state and rendering."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Python Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.reset()

    def reset(self) -> None:
        center = Point(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [center, Point(center.x - 1, center.y), Point(center.x - 2, center.y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self._spawn_food()
        self.score = 0
        self.paused = False
        self.game_over = False

    def _spawn_food(self) -> Point:
        occupied = set(self.snake)
        empty_cells = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in occupied
        ]
        if not empty_cells:
            return Point(-1, -1)
        return random.choice(empty_cells)

    def run(self) -> None:
        running = True
        while running:
            running = self._handle_events()
            if not self.paused and not self.game_over:
                self._update()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()

    def _handle_events(self) -> bool:
        key_to_direction = {
            pygame.K_UP: Direction.UP,
            pygame.K_w: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_s: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_a: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_d: Direction.RIGHT,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_p and not self.game_over:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key in key_to_direction:
                new_direction = key_to_direction[event.key]
                if new_direction != self.direction.opposite():
                    self.next_direction = new_direction
        return True

    def _update(self) -> None:
        self.direction = self.next_direction
        new_head = self.snake[0].move(self.direction)

        hit_wall = not (0 <= new_head.x < GRID_WIDTH and 0 <= new_head.y < GRID_HEIGHT)
        hit_self = new_head in self.snake[:-1]
        if hit_wall or hit_self:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self._spawn_food()
        else:
            self.snake.pop()

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._draw_status_bar()

        if self.paused:
            self._draw_center_message("Paused", "Press P to resume or R to restart")
        elif self.game_over:
            self._draw_center_message("Game Over", "Press R to restart or Esc to quit")

        pygame.display.flip()

    def _draw_grid(self) -> None:
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, SIDEBAR_HEIGHT), (x, WINDOW_HEIGHT))
        for y in range(SIDEBAR_HEIGHT, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (WINDOW_WIDTH, y))

    def _draw_food(self) -> None:
        if self.food.x < 0:
            return
        pygame.draw.ellipse(self.screen, FOOD, self._cell_rect(self.food).inflate(-6, -6))

    def _draw_snake(self) -> None:
        for index, point in enumerate(self.snake):
            color = SNAKE_HEAD if index == 0 else SNAKE_BODY
            pygame.draw.rect(self.screen, color, self._cell_rect(point).inflate(-3, -3), border_radius=6)

    def _draw_status_bar(self) -> None:
        pygame.draw.rect(self.screen, (18, 20, 28), (0, 0, WINDOW_WIDTH, SIDEBAR_HEIGHT))
        score_surface = self.font.render(f"Score: {self.score}", True, TEXT)
        help_surface = self.small_font.render("Move: arrows/WASD  Pause: P  Restart: R  Quit: Esc", True, MUTED_TEXT)
        self.screen.blit(score_surface, (18, 8))
        self.screen.blit(help_surface, (18, 34))

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - SIDEBAR_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*OVERLAY, 185))
        self.screen.blit(overlay, (0, SIDEBAR_HEIGHT))

        title_surface = self.font.render(title, True, TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, MUTED_TEXT)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 18))
        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

    @staticmethod
    def _cell_rect(point: Point) -> pygame.Rect:
        return pygame.Rect(point.x * CELL_SIZE, point.y * CELL_SIZE + SIDEBAR_HEIGHT, CELL_SIZE, CELL_SIZE)


def main() -> None:
    SnakeGame().run()


if __name__ == "__main__":
    main()
