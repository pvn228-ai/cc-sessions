"""The persistent world: a grid of connected areas.

The world is a dict keyed by ``(col, row)`` grid coordinates. Walking off
the LEFT border of area ``(col, row)`` takes you WEST to ``(col - 1, row)``;
the RIGHT border takes you EAST to ``(col + 1, row)``; the TOP border takes
you NORTH to ``(col, row - 1)``; the BOTTOM border (a pit) drops you SOUTH
to ``(col, row + 1)``. If there is no area in that direction, the border is
solid and you simply stop.

Each area is authored as 15 rows. Rows are padded/truncated to 24 columns by
the parser, so only the placed glyphs need to line up.

Legend:
    #  solid tile        C  coin            E  patrolling enemy
    P  player spawn      (space) empty
"""

from . import settings as cfg

# Grid coordinate the player starts in, and the four areas around it.
START_AREA = (1, 1)

# Convenience strings (exactly 24 chars) for full and pitted floors.
FLOOR = "#" * cfg.AREA_COLS                       # solid ground, no exits below
PIT_R = "#" * 16 + " " * 3 + "#" * 5              # gap at cols 16-18 -> drops south
PIT_L = "#" * 5 + " " * 3 + "#" * 16              # gap at cols 5-7  -> drops south


WORLD = {
    # ---------------------------------------------------------------- HOME (1,1)
    # A meadow with a staircase up the left wall (jump off the top to go NORTH)
    # and a pit on the right of the floor (fall in to go SOUTH). Walk off the
    # left/right edges to reach the WEST grove / EAST dunes.
    (1, 1): {
        "name": "Meadow",
        "rows": [
            "                        ",
            " C                      ",
            " ###                    ",
            "                        ",
            "          C C           ",
            "        #######         ",
            "  ###                   ",
            "                 C      ",
            "             E   ###     ",
            "   ###                  ",
            "                        ",
            "     ###          C     ",
            "                 ###    ",
            "       C C   P          ",
            PIT_R,
        ],
    },

    # ---------------------------------------------------------------- WEST (0,1)
    (0, 1): {
        "name": "Grove",
        "rows": [
            "                        ",
            "                        ",
            "        C   C   C        ",
            "       #########        ",
            "                        ",
            "                        ",
            "   C            E        ",
            "  ###        #######     ",
            "                        ",
            "          C             ",
            "        #####           ",
            "  E                C     ",
            "#####            ###     ",
            "                        ",
            FLOOR,
        ],
    },

    # ---------------------------------------------------------------- EAST (2,1)
    (2, 1): {
        "name": "Dunes",
        "rows": [
            "                        ",
            "                        ",
            "             C C C       ",
            "            #######      ",
            "                        ",
            "      C                  ",
            "     ###          E      ",
            "               #####     ",
            "                        ",
            "  C        E             ",
            " ###    #######          ",
            "                   C C   ",
            "                  #####   ",
            "                        ",
            FLOOR,
        ],
    },

    # --------------------------------------------------------------- NORTH (1,0)
    # Reached by climbing Home's staircase and leaving through the top. A pit on
    # the left of the floor drops you back SOUTH to Home.
    (1, 0): {
        "name": "Sky Bluffs",
        "rows": [
            "                        ",
            "      C            C     ",
            "     ###          ###    ",
            "                        ",
            "           C C          ",
            "         #########      ",
            "   C                    ",
            "  ###             C      ",
            "               #####     ",
            "         E              ",
            "      #######           ",
            "                  C     ",
            "   C             ###    ",
            "  ###                   ",
            PIT_L,
        ],
    },

    # --------------------------------------------------------------- SOUTH (1,2)
    # Reached by dropping through Home's right pit. You land on platforms; climb
    # the staircase on the right and leave through the top to return to Home.
    (1, 2): {
        "name": "Cavern",
        "rows": [
            "                        ",
            "                  C      ",
            "                 ###     ",
            "             C          ",
            "            ###     ###  ",
            "       C                 ",
            "      ###          ###   ",
            "  C                      ",
            " ###            ###      ",
            "          E              ",
            "       #######     ###   ",
            "   C                     ",
            "  ###       C C          ",
            "          #######        ",
            FLOOR,
        ],
    },
}
