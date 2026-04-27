# game.py — Core game logic (snake, food, power-ups, obstacles)
# No rendering here — pure state management so screens stay clean.

import random
import pygame
from config import (
    GRID_COLS, GRID_ROWS, CELL_SIZE,
    FPS_BASE, FPS_MAX, SPEED_INCREMENT,
    FOOD_PER_LEVEL,
    FOOD_TIMEOUT, POISON_TIMEOUT,
    FOOD_WEIGHTS, FOOD_POINTS,
    POWERUP_FIELD_TTL, POWERUP_EFFECT_TTL,
    SPEED_BOOST_BONUS, SLOW_MOTION_PENALTY,
    OBSTACLE_MIN_PER_LEVEL, OBSTACLE_MAX_PER_LEVEL,
)

# ── Direction vectors ───────────────────────────────────────────────────────
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# ── Small data classes ──────────────────────────────────────────────────────

class Food:
    def __init__(self, pos, kind, spawn_time):
        self.pos   = pos          # (col, row)
        self.kind  = kind         # "normal" | "bonus" | "rare" | "poison"
        self.spawn = spawn_time
        self.ttl   = POISON_TIMEOUT if kind == "poison" else FOOD_TIMEOUT

    def is_expired(self, now):
        return (now - self.spawn) > self.ttl

    @property
    def points(self):
        return FOOD_POINTS[self.kind]


class PowerUp:
    def __init__(self, pos, kind, spawn_time):
        self.pos   = pos
        self.kind  = kind   # "speed" | "slow" | "shield"
        self.spawn = spawn_time

    def is_expired(self, now):
        return (now - self.spawn) > POWERUP_FIELD_TTL


# ── Main game state ─────────────────────────────────────────────────────────

class GameState:
    def __init__(self, settings: dict):
        self.settings = settings
        self.reset()

    # ── Public reset ───────────────────────────────────────────────────────
    def reset(self):
        mid_col = GRID_COLS // 2
        mid_row = GRID_ROWS // 2
        self.snake     = [(mid_col, mid_row),
                          (mid_col - 1, mid_row),
                          (mid_col - 2, mid_row)]
        self.direction  = RIGHT
        self.next_dir   = RIGHT

        self.score      = 0
        self.level      = 1
        self.foods_eaten = 0
        self.game_over  = False

        self.foods:    list[Food]   = []
        self.powerup:  PowerUp | None = None
        self.obstacles: set[tuple]  = set()

        # Active effects
        self.shield_active   = False
        self.active_effect   = None        # "speed" | "slow" | None
        self.effect_end_time = 0

        # Timing
        self._powerup_spawn_timer = pygame.time.get_ticks() + 5_000  # first pu after 5 s

        self._spawn_food()
        self._spawn_food()   # start with 2 foods

    # ── Properties ─────────────────────────────────────────────────────────
    @property
    def current_fps(self) -> int:
        base = FPS_BASE + (self.level - 1) * SPEED_INCREMENT
        if self.active_effect == "speed":
            base = min(base + SPEED_BOOST_BONUS, FPS_MAX)
        elif self.active_effect == "slow":
            base = max(base - SLOW_MOTION_PENALTY, 2)
        return min(base, FPS_MAX)

    @property
    def head(self):
        return self.snake[0]

    # ── Update (called once per game tick) ─────────────────────────────────
    def update(self) -> str | None:
        """
        Advance one tick. Returns an event string or None:
          "game_over" | "level_up" | "ate_food" | "ate_powerup" | None
        """
        if self.game_over:
            return None

        now = pygame.time.get_ticks()

        # Check effect expiry
        if self.active_effect and now >= self.effect_end_time:
            self.active_effect = None

        # Expire foods
        self.foods = [f for f in self.foods if not f.is_expired(now)]

        # Expire powerup on field
        if self.powerup and self.powerup.is_expired(now):
            self.powerup = None

        # Ensure at least 2 foods on field at all times
        while len(self.foods) < 2:
            self._spawn_food()

        # Maybe spawn a power-up
        if self.powerup is None and now >= self._powerup_spawn_timer:
            self._spawn_powerup()
            self._powerup_spawn_timer = now + random.randint(8_000, 15_000)

        # Move snake
        self.direction = self.next_dir
        hc, hr = self.head
        dc, dr = self.direction
        new_head = (hc + dc, hr + dr)

        # Wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            return self._handle_collision()

        # Obstacle collision
        if new_head in self.obstacles:
            return self._handle_collision()

        # Self collision
        if new_head in self.snake[:-1]:
            return self._handle_collision()

        # Advance body
        self.snake.insert(0, new_head)
        ate_something = False

        # Check food
        for food in list(self.foods):
            if food.pos == new_head:
                self.foods.remove(food)
                ate_something = True
                if food.kind == "poison":
                    # Shorten by 2 (head already inserted, so remove 2 extra from tail)
                    for _ in range(3):   # 1 normal + 2 extra removal
                        if len(self.snake) > 1:
                            self.snake.pop()
                    if len(self.snake) <= 1:
                        self.game_over = True
                        return "game_over"
                else:
                    self.score      += food.points
                    self.foods_eaten += 1
                    # Don't pop tail → snake grows
                    self._spawn_food()
                    if self.foods_eaten % FOOD_PER_LEVEL == 0:
                        self.level += 1
                        self._place_obstacles()
                        return "level_up"
                    return "ate_food"
                break

        # Check power-up
        if self.powerup and self.powerup.pos == new_head:
            self._apply_powerup(self.powerup.kind, now)
            self.powerup = None
            ate_something = True
            if not self._ate_food_this_tick:
                self.snake.pop()   # no growth
            return "ate_powerup"

        if not ate_something:
            self.snake.pop()   # normal move: remove tail

        return None

    # Hack flag used to coordinate growth vs no-growth when powerup eaten same tick
    _ate_food_this_tick = False

    # ── Direction input ─────────────────────────────────────────────────────
    def set_direction(self, new_dir):
        if new_dir != OPPOSITES.get(self.direction):
            self.next_dir = new_dir

    # ── Internal helpers ────────────────────────────────────────────────────
    def _occupied(self) -> set:
        """All cells that must not receive a new item."""
        occupied = set(self.snake) | self.obstacles
        occupied.update(f.pos for f in self.foods)
        if self.powerup:
            occupied.add(self.powerup.pos)
        return occupied

    def _random_free_cell(self) -> tuple | None:
        occupied = self._occupied()
        free = [
            (c, r)
            for c in range(GRID_COLS)
            for r in range(GRID_ROWS)
            if (c, r) not in occupied
        ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        pos = self._random_free_cell()
        if pos is None:
            return
        now = pygame.time.get_ticks()
        kinds  = list(FOOD_WEIGHTS.keys())
        weights = list(FOOD_WEIGHTS.values())
        kind = random.choices(kinds, weights=weights, k=1)[0]
        self.foods.append(Food(pos, kind, now))

    def _spawn_powerup(self):
        pos = self._random_free_cell()
        if pos is None:
            return
        kind = random.choice(["speed", "slow", "shield"])
        self.powerup = PowerUp(pos, kind, pygame.time.get_ticks())

    def _apply_powerup(self, kind, now):
        if kind == "shield":
            self.shield_active = True
        else:
            self.active_effect   = kind
            self.effect_end_time = now + POWERUP_EFFECT_TTL

    def _handle_collision(self) -> str:
        if self.shield_active:
            self.shield_active = False
            # Let the move still happen by placing head at clamped position
            # (snake already has new_head inserted by caller — just remove tail)
            return None
        self.game_over = True
        return "game_over"

    def _place_obstacles(self):
        """Place obstacles for new level (Level 3+)."""
        if self.level < 3:
            return
        count = random.randint(OBSTACLE_MIN_PER_LEVEL, OBSTACLE_MAX_PER_LEVEL)
        occupied = set(self.snake) | {f.pos for f in self.foods}
        if self.powerup:
            occupied.add(self.powerup.pos)
        # Keep a safety zone around snake head
        hc, hr = self.head
        safe_zone = {
            (hc + dc, hr + dr)
            for dc in range(-3, 4)
            for dr in range(-3, 4)
        }
        candidates = [
            (c, r)
            for c in range(GRID_COLS)
            for r in range(GRID_ROWS)
            if (c, r) not in occupied and (c, r) not in safe_zone
               and (c, r) not in self.obstacles
        ]
        random.shuffle(candidates)
        for pos in candidates[:count]:
            self.obstacles.add(pos)