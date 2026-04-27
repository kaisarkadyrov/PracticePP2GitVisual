# config.py — Game constants

# Window
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
TITLE         = "Snake Deluxe"

# Grid
CELL_SIZE     = 20
GRID_COLS     = WINDOW_WIDTH  // CELL_SIZE   # 40
GRID_ROWS     = WINDOW_HEIGHT // CELL_SIZE   # 30

# Timing
FPS_BASE      = 10        # starting frames-per-second (snake moves this many cells/sec)
FPS_MAX       = 25        # hard cap

# Scoring / levels
FOOD_PER_LEVEL = 5        # eat this many foods to advance a level
SPEED_INCREMENT = 1       # extra FPS added per level

# Food timers (milliseconds)
FOOD_TIMEOUT   = 8_000    # regular food disappears after 8 s
POISON_TIMEOUT = 6_000    # poison disappears after 6 s

# Power-up
POWERUP_FIELD_TTL  = 8_000   # ms before power-up vanishes from field
POWERUP_EFFECT_TTL = 5_000   # ms the effect lasts after collection
SPEED_BOOST_BONUS  = 5       # extra FPS for speed boost
SLOW_MOTION_PENALTY = 4      # FPS reduction for slow motion

# Obstacles
OBSTACLE_MIN_PER_LEVEL = 3
OBSTACLE_MAX_PER_LEVEL = 7

# Colors
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (128, 128, 128)
DARK_GRAY   = ( 40,  40,  40)
GREEN       = ( 50, 200,  50)
DARK_GREEN  = ( 30, 140,  30)
RED         = (220,  50,  50)
DARK_RED    = (120,  10,  10)
YELLOW      = (240, 200,  30)
ORANGE      = (230, 130,  20)
CYAN        = ( 30, 220, 220)
PURPLE      = (160,  40, 220)
BLUE        = ( 40, 100, 220)
BROWN       = (120,  70,  20)

# Food color map  {kind: color}
FOOD_COLORS = {
    "normal":  GREEN,
    "bonus":   YELLOW,
    "rare":    ORANGE,
    "poison":  DARK_RED,
}

# Food point weights  {kind: points}
FOOD_POINTS = {
    "normal": 10,
    "bonus":  25,
    "rare":   50,
    "poison":  0,   # handled specially
}

# Food spawn weights (probability ratios)
FOOD_WEIGHTS = {
    "normal": 55,
    "bonus":  25,
    "rare":   10,
    "poison": 10,
}

# Power-up colors
POWERUP_COLORS = {
    "speed":   CYAN,
    "slow":    PURPLE,
    "shield":  BLUE,
}

# Obstacle color
OBSTACLE_COLOR = (100, 80, 60)

# UI
BG_COLOR        = ( 15,  15,  20)
PANEL_COLOR     = ( 25,  25,  35)
ACCENT_COLOR    = ( 70, 200, 120)
BUTTON_COLOR    = ( 40,  40,  60)
BUTTON_HOVER    = ( 60,  60,  90)
TEXT_COLOR      = (220, 220, 220)
MUTED_COLOR     = (120, 120, 140)
BORDER_COLOR    = ( 70,  70,  90)

# DB — override with env vars if needed
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASS = "k14062007"