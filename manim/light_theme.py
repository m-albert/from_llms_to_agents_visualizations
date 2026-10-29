"""
Light theme for the vendored 3b1b scene code.

The 3b1b scenes assume a black background: WHITE means "foreground",
BLACK means "background" (e.g. set_backstroke(BLACK)), and the pale
tints (*_A, *_B, YELLOW) are chosen to pop against black. Rather than
editing every scene, this module rebinds those names so the same code
reads well on white. manim_imports_ext star-imports it last, so every
module doing `from manim_imports_ext import *` sees these values.

If you really mean the literal color, use TRUE_WHITE / TRUE_BLACK
(or a hex string).

Background and default text colors are set in custom_config.yml.
"""
from manimlib import constants as _c

TRUE_WHITE = _c.WHITE
TRUE_BLACK = _c.BLACK

# Foreground <-> background
WHITE = _c.BLACK
BLACK = _c.WHITE

# Grey scale flips around GREY_C
GREY_A, GREY_E = _c.GREY_E, _c.GREY_A
GREY_B, GREY_D = _c.GREY_D, _c.GREY_B

# Pale tints become their dark counterparts
BLUE_A, BLUE_B = _c.BLUE_E, _c.BLUE_D
TEAL_A, TEAL_B = _c.TEAL_E, _c.TEAL_D
GREEN_A, GREEN_B = _c.GREEN_E, _c.GREEN_D
RED_A, RED_B = _c.RED_E, _c.RED_D
MAROON_A, MAROON_B = _c.MAROON_E, _c.MAROON_D
PURPLE_A, PURPLE_B = _c.PURPLE_E, _c.PURPLE_D
GOLD_A, GOLD_B = _c.GOLD_E, _c.GOLD_D

# Pure yellow is unreadable on white; use a dark gold family instead
YELLOW_A = "#E8B400"
YELLOW_B = "#DDA800"
YELLOW = YELLOW_C = "#D49B00"
YELLOW_D = "#B88600"
YELLOW_E = "#9C7100"
