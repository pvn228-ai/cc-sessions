"""Central tunable constants for the platformer.

Keeping these in one place makes it easy to tweak the feel of the game
without hunting through the rest of the code.
"""

# --- Display ---------------------------------------------------------------
TILE_SIZE = 40
# Each "area" is exactly one screen. 24 x 15 tiles == 960 x 600 px, so there
# is no scrolling within an area -- you cross a border to reach the next one.
AREA_COLS = 24
AREA_ROWS = 15
SCREEN_WIDTH = AREA_COLS * TILE_SIZE   # 960
SCREEN_HEIGHT = AREA_ROWS * TILE_SIZE  # 600
FPS = 60
TITLE = "World Map Platformer"

# When you enter a new area through a border, you appear this many pixels in
# from the opposite border so you are not instantly pushed back.
BORDER_ENTRY_MARGIN = 12

# --- Physics ---------------------------------------------------------------
# Tuned for a snappy, slightly floaty feel. Values are in pixels / frame.
GRAVITY = 0.8
MAX_FALL_SPEED = 18
PLAYER_SPEED = 5
JUMP_SPEED = 16

# Forgiveness windows (in frames) that make the controls feel good.
COYOTE_FRAMES = 6        # jump shortly after walking off a ledge
JUMP_BUFFER_FRAMES = 6   # jump press registers slightly before landing

# Holding jump rises higher; releasing early cuts the jump short.
JUMP_CUT_MULTIPLIER = 0.45

# --- Enemies ---------------------------------------------------------------
ENEMY_SPEED = 2

# --- Colors ----------------------------------------------------------------
SKY_TOP = (44, 62, 90)
SKY_BOTTOM = (90, 120, 160)
TILE_COLOR = (70, 84, 64)
TILE_TOP_COLOR = (110, 140, 80)
PLAYER_COLOR = (235, 110, 95)
PLAYER_EYE_COLOR = (255, 255, 255)
COIN_COLOR = (250, 205, 70)
COIN_SHINE = (255, 240, 180)
ENEMY_COLOR = (150, 80, 170)
GOAL_COLOR = (90, 200, 130)
TEXT_COLOR = (240, 240, 240)
SHADOW_COLOR = (20, 24, 32)
