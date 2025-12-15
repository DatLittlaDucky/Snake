import pygame
import sys
import os
from collections import deque
import random

# ---------------- CONFIG ----------------
CELL = 32                      # grid cell size (16x16 images scale cleanly to 32)
GRID_W, GRID_H = 15, 15
WIDTH, HEIGHT = GRID_W * CELL, GRID_H * CELL
FPS = 10

# ---------------- PATH FIX ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

# ---------------- DIRECTIONS ----------------
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ---------------- INIT ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake V1")
clock = pygame.time.Clock()

# ---------------- LOAD IMAGES ----------------
def load_img(name):
    path = os.path.join(ASSETS_DIR, f"{name}.png")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing asset: {path}")
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (CELL, CELL))

IMG_HEAD = load_img("head")
IMG_BODY = load_img("body")
IMG_TAIL = load_img("tail")
IMG_TURN = load_img("turn")

# ---------------- HELPERS ----------------
def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def clamp_dir(d):
    return (max(-1, min(1, d[0])), max(-1, min(1, d[1])))

def rotate(img, d):
    # images face RIGHT by default
    if d == RIGHT: return img
    if d == DOWN:  return pygame.transform.rotate(img, -90)
    if d == LEFT:  return pygame.transform.rotate(img, 180)
    if d == UP:    return pygame.transform.rotate(img, 90)
    return img

# Corner rotations
CORNER_ROT = {
    (UP, RIGHT): 0,   (LEFT, DOWN): 0,
    (RIGHT, DOWN): -90, (UP, LEFT): -90,
    (DOWN, LEFT): 180, (RIGHT, UP): 180,
    (LEFT, UP): 90, (DOWN, RIGHT): 90,
}

# ---------------- SNAKE ----------------
class Snake:
    def __init__(self):
        self.body = deque([(5, 7), (4, 7), (3, 7)])
        self.dir = RIGHT
        self.grow = 0

    def set_dir(self, d):
        if add(d, self.dir) != (0, 0):
            self.dir = d

    def step(self):
        new_head = add(self.body[0], self.dir)
        new_head = (new_head[0] % GRID_W, new_head[1] % GRID_H)

        if new_head in self.body:
            return False

        self.body.appendleft(new_head)

        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

        return True

    def draw(self, surf):
        # ---- HEAD ----
        head_dir = clamp_dir((
            self.body[0][0] - self.body[1][0],
            self.body[0][1] - self.body[1][1]
        ))
        surf.blit(
            rotate(IMG_HEAD, head_dir),
            (self.body[0][0] * CELL, self.body[0][1] * CELL)
        )

        # ---- BODY ----
        for i in range(1, len(self.body) - 1):
            prev = self.body[i - 1]
            curr = self.body[i]
            nxt  = self.body[i + 1]

            d1 = clamp_dir((curr[0] - prev[0], curr[1] - prev[1]))
            d2 = clamp_dir((nxt[0] - curr[0], nxt[1] - curr[1]))

            if d1 == d2 or d1 == (-d2[0], -d2[1]):
                # straight OR accidental reversal → draw body
                img = rotate(IMG_BODY, d1)
            else:
                # proper corner
                rot = CORNER_ROT.get((d1, d2))
                if rot is None:
                    img = rotate(IMG_BODY, d1)  # final safety fallback
                else:
                    img = pygame.transform.rotate(IMG_TURN, rot)

            surf.blit(img, (curr[0] * CELL, curr[1] * CELL))

        # ---- TAIL ----
        tail_dir = clamp_dir((
            self.body[-2][0] - self.body[-1][0],
            self.body[-2][1] - self.body[-1][1]
        ))
        surf.blit(
            rotate(IMG_TAIL, tail_dir),
            (self.body[-1][0] * CELL, self.body[-1][1] * CELL)
        )

# ---------------- FOOD ----------------
class Food:
    def __init__(self, snake):
        self.pos = self.spawn(snake)

    def spawn(self, snake):
        while True:
            p = (random.randrange(GRID_W), random.randrange(GRID_H))
            if p not in snake.body:
                return p

    def draw(self, surf):
        pygame.draw.rect(
            surf,
            (200, 50, 50),
            (self.pos[0] * CELL, self.pos[1] * CELL, CELL, CELL)
        )

# ---------------- GAME ----------------
snake = Snake()
food = Food(snake)

DARK_GREEN  = (20, 60, 20)
LIGHT_GREEN = (30, 90, 30)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_w, pygame.K_UP):    snake.set_dir(UP)
            if e.key in (pygame.K_s, pygame.K_DOWN):  snake.set_dir(DOWN)
            if e.key in (pygame.K_a, pygame.K_LEFT):  snake.set_dir(LEFT)
            if e.key in (pygame.K_d, pygame.K_RIGHT): snake.set_dir(RIGHT)

    if not snake.step():
        snake = Snake()
        food = Food(snake)

    if snake.body[0] == food.pos:
        snake.grow += 2
        food = Food(snake)

    # ---- BACKGROUND ----
    for y in range(GRID_H):
        for x in range(GRID_W):
            color = DARK_GREEN if (x + y) % 2 == 0 else LIGHT_GREEN
            pygame.draw.rect(
                screen,
                color,
                (x * CELL, y * CELL, CELL, CELL)
            )

    food.draw(screen)
    snake.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)