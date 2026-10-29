from manimlib import *
from manimlib.mobject.svg.old_tex_mobject import *

from custom.backdrops import *
from custom.banner import *
from custom.characters.pi_creature import *
from custom.characters.pi_creature_animations import *
from custom.characters.pi_creature_scene import *
from custom.deprecated import *
from custom.drawings import *
from custom.end_screen import *
from custom.filler import *
from custom.logo import *
from custom.opening_quote import *

# Local additions (not upstream)
import manimpango as _manimpango

for _font in Path(__file__).parent.joinpath("assets", "fonts").glob("*.otf"):
    _manimpango.register_font(str(_font))

from light_theme import *
