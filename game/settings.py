"""Central tunable constants for the game (v1 vertical slice).

Side-view action-platformer RPG. Keeping these in one place makes it easy to
tweak the feel without hunting through the rest of the code.
"""

# --- Display ---------------------------------------------------------------
TILE_SIZE = 40
# A "room" is exactly one screen. 24 x 15 tiles == 960 x 600 px. You cross a
# border (or take stairs) to reach the next room.
AREA_COLS = 24
AREA_ROWS = 15
SCREEN_WIDTH = AREA_COLS * TILE_SIZE   # 960
SCREEN_HEIGHT = AREA_ROWS * TILE_SIZE  # 600
FPS = 60
TITLE = "Larkhollow — a Delver's Tale"

# When you enter a new room through a border, you appear this far in from the
# opposite border so you are not instantly pushed back.
BORDER_ENTRY_MARGIN = 14

# --- Platformer physics ----------------------------------------------------
GRAVITY = 0.8
MAX_FALL_SPEED = 18
PLAYER_SPEED = 5
JUMP_SPEED = 16
COYOTE_FRAMES = 6
JUMP_BUFFER_FRAMES = 6
JUMP_CUT_MULTIPLIER = 0.45

# --- Player combat / survival ----------------------------------------------
PLAYER_MAX_HP = 6
PLAYER_IFRAMES = 45          # invulnerability after taking a hit (frames)
PLAYER_KNOCKBACK = 9

STAMINA_MAX = 100
STAMINA_REGEN = 0.9         # per frame
DASH_COST = 28
HEAVY_COST = 42

# Light swing — fast, cheap, short reach.
SWING_FRAMES = 12           # how long the hitbox is live
SWING_DAMAGE = 1
SWING_REACH = 34            # pixels the arc extends in front
# Heavy "Shellbreaker" — slow wind-up, breaks guard / cracks shell.
HEAVY_WINDUP = 16
HEAVY_FRAMES = 14
HEAVY_DAMAGE = 2
HEAVY_REACH = 40
# Plunge / down-attack — aerial strike onto the shell from above (ignores guard).
PLUNGE_DAMAGE = 2
PLUNGE_SPEED = 20

# Dash — burst of speed with invulnerability frames.
DASH_SPEED = 13
DASH_FRAMES = 10
DASH_IFRAMES = 12
DASH_COOLDOWN = 22

# --- Karcite Searing (environmental hazard) --------------------------------
SEARING_INTERVAL = 30       # frames between Searing ticks
SEARING_DAMAGE = 1

# --- Pinchling (enemy) -----------------------------------------------------
PINCHLING_HP = 4
PINCHLING_SPEED = 1.4
PINCHLING_TOUCH_DAMAGE = 1
PINCHLING_STAGGER_FRAMES = 70   # window of vulnerability after a guard break
PINCHLING_WINDUP_FRAMES = 28    # claw-raise telegraph (guard is dropped = punish)
PINCHLING_LUNGE_FRAMES = 12
PINCHLING_LUNGE_SPEED = 6
PINCHLING_ATTACK_COOLDOWN = 90

# --- Clawknight (plated enemy, Depth 2+) -----------------------------------
# A Lower Karcon in intact plate: flanks and light swings clatter off until the
# carapace is breached by CLAWKNIGHT_PLATE cracking hits (Shellbreaker/plunge).
CLAWKNIGHT_HP = 7
CLAWKNIGHT_PLATE = 2
CLAWKNIGHT_SPEED = 1.1
CLAWKNIGHT_TOUCH_DAMAGE = 2
CLAWKNIGHT_STAGGER_FRAMES = 90
CLAWKNIGHT_WINDUP_FRAMES = 34
CLAWKNIGHT_LUNGE_FRAMES = 16
CLAWKNIGHT_LUNGE_SPEED = 7
CLAWKNIGHT_ATTACK_COOLDOWN = 80

# --- Colors ----------------------------------------------------------------
SKY_TOP = (44, 62, 90)
SKY_BOTTOM = (96, 128, 168)
CAVE_TOP = (28, 22, 38)
CAVE_BOTTOM = (16, 12, 24)
TILE_COLOR = (70, 84, 64)
TILE_TOP_COLOR = (110, 150, 80)
CAVE_TILE_COLOR = (54, 48, 64)
CAVE_TILE_TOP = (78, 66, 92)
PLAYER_COLOR = (235, 110, 95)
PLAYER_DASH_COLOR = (255, 200, 120)
PLAYER_EYE_COLOR = (255, 255, 255)
PLAYER_IFRAME_COLOR = (235, 160, 150)
KARCITE_COLOR = (170, 80, 220)        # the signature purple glow
KARCITE_GLOW = (210, 140, 255)
KARCITE_DARK = (90, 40, 130)
LOOT_COLOR = (200, 150, 250)
COIN_COLOR = (250, 205, 70)
PINCHLING_COLOR = (210, 95, 80)
PINCHLING_SHELL_COLOR = (150, 60, 50)
PINCHLING_STAGGER_COLOR = (250, 220, 120)
CLAWKNIGHT_COLOR = (150, 110, 170)
CLAWKNIGHT_SHELL_COLOR = (95, 70, 120)
PLATE_COLOR = (215, 200, 235)
NPC_COLOR = (110, 180, 220)
SMITH_COLOR = (230, 175, 95)
XP_COLOR = (150, 200, 250)
ENTRANCE_COLOR = (40, 30, 50)
STAIRS_COLOR = (180, 160, 120)
TEXT_COLOR = (240, 240, 240)
DIM_TEXT = (170, 178, 190)
SWING_COLOR = (245, 245, 235)
HP_COLOR = (225, 80, 80)
HP_EMPTY = (70, 50, 55)
STAMINA_COLOR = (110, 200, 160)
SHADOW_COLOR = (20, 24, 32)
TREE_TRUNK = (84, 60, 44)
TREE_LEAF = (70, 130, 70)
BUILDING_WALL = (150, 120, 95)
BUILDING_ROOF = (170, 90, 80)
