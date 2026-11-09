"""
Line icons of the schematics (ported from llm_to_agentic_ai.svg), shared by
the stills and the animations, so that a tool looks the same everywhere.
"""
from manim_imports_ext import *
from manimlib.mobject.svg.svg_mobject import VMobjectFromSVGPath
import svgelements as se

ICON_ACCENT = "#2F6FB0"

# One unit of the llm_to_agentic_ai.svg grid, whose icons are ported below
UNIT = FRAME_WIDTH / 1980


# Icons, in the coordinates of llm_to_agentic_ai.svg (y pointing down)

def rect_d(x, y, w, h, r=0):
    if r == 0:
        return f"M{x} {y}H{x + w}V{y + h}H{x}Z"
    return (
        f"M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}"
        f"A{r} {r} 0 0 1 {x + w - r} {y + h}H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}"
        f"V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z"
    )


def ellipse_d(cx, cy, rx, ry):
    return f"M{cx - rx} {cy}A{rx} {ry} 0 1 1 {cx + rx} {cy}A{rx} {ry} 0 1 1 {cx - rx} {cy}Z"


def circle_d(cx, cy, r):
    return ellipse_d(cx, cy, r, r)


def icon_part(d, fill=None, stroke=None, width=2.0):
    """One path of an icon: filled and/or stroked; widths are in manim's units."""
    part = VMobjectFromSVGPath(se.Path(d))
    part.set_fill(fill or TRUE_WHITE, 1 if fill else 0)
    part.set_stroke(stroke or TRUE_WHITE, width if stroke else 0)
    part.flip(RIGHT, about_point=ORIGIN)
    part.scale(UNIT, about_point=ORIGIN)
    return part


def icon_letter(string, x, y, font_size, color):
    letter = Text(string, font_size=font_size, weight=BOLD).set_color(color)
    return letter.move_to([x * UNIT, -y * UNIT, 0])


def get_icon(name, color=ICON_ACCENT, height=None, width=2.0):
    """A line icon. Without a height, it has the size of the schematic's icons."""
    def line(d, stroke_width=width):
        return icon_part(d, stroke=color, width=stroke_width)

    def outline(d):
        return icon_part(d, fill=TRUE_WHITE, stroke=color, width=width)

    def solid(d):
        return icon_part(d, fill=color)

    def knockout(d, stroke_width=width):
        return icon_part(d, stroke=TRUE_WHITE, width=stroke_width)

    if name == "books":
        parts = [
            outline(rect_d(-17, 5, 34, 10, 2)), outline(rect_d(-13, -6, 30, 10, 2)),
            outline(rect_d(-16, -17, 31, 10, 2)),
            line("M-10 5V15"), line("M10 -6V4"), line("M-9 -17V-7"),
        ]
    elif name == "web":
        parts = [
            outline(circle_d(0, 0, 17)), outline(ellipse_d(0, 0, 7.5, 17)),
            line("M-17 0H17"), line("M-14.5 -8.5H14.5"), line("M-14.5 8.5H14.5"),
        ]
    elif name == "code":
        parts = [
            outline(rect_d(-19, -15, 38, 30, 4)),
            line("M-6 -6L-12 0L-6 6"), line("M6 -6L12 0L6 6"), line("M2.5 -8L-2.5 8"),
        ]
    elif name == "papers":
        parts = [
            outline("M-13 -18H5L13 -10V18H-13Z"), line("M5 -18V-10H13"),
            line("M-8 -10H0"), line("M-8 -4H8"),
            line("M-6 13V8", 2.8), line("M0 13V3", 2.8), line("M6 13V6", 2.8),
        ]
    elif name == "examples":
        parts = [
            outline(rect_d(-21, -18, 28, 21, 5)), icon_letter("Q", -7, -7.5, 9, color),
            solid(rect_d(-6, -1, 28, 21, 5)), icon_letter("A", 8, 9.5, 9, TRUE_WHITE),
        ]
    elif name == "feedback":
        parts = [
            outline(circle_d(-5, -9, 7.5)), line("M-19 16C-19 2 9 2 9 16"),
            solid(circle_d(12, 8, 9.5)), knockout("M7.5 8.5L10.5 11.5L16 5"),
        ]
    elif name == "problems":
        parts = [outline(rect_d(-19, -15, 38, 30, 4)), icon_letter("x=?", 0, 0, 9, color)]
    elif name == "rewards":
        parts = [solid(circle_d(0, 0, 17)), knockout("M-7 0.5L-2 5.5L8 -5", 2.6)]
    elif name == "folder":
        parts = [outline("M-17 -12H-5L-1 -7H17V14H-17Z"), line("M-17 -2H17")]
    elif name == "person":
        parts = [
            solid(circle_d(0, 0, 13)),
            icon_part(circle_d(0, -3.5, 4.2), fill=TRUE_WHITE),
            icon_part("M-7.5 8.5C-7.5 2.5 7.5 2.5 7.5 8.5Z", fill=TRUE_WHITE),
        ]
    elif name == "robot":
        parts = [
            line("M0 -9.5V-13"), solid(circle_d(0, -14, 2.4)),
            solid(rect_d(-13, -4, 3, 8, 1.5)), solid(rect_d(10, -4, 3, 8, 1.5)),
            solid(rect_d(-10, -10, 20, 19, 5)),
            icon_part(circle_d(-4, -2, 2.4), fill=TRUE_WHITE),
            icon_part(circle_d(4, -2, 2.4), fill=TRUE_WHITE),
            knockout("M-3.5 4H3.5", 1.8),
        ]
    elif name == "cloud":
        parts = [outline(
            "M-12 12H13A9 9 0 0 0 14 -6A12 12 0 0 0 -8 -9A9 9 0 0 0 -12 12Z"
        )]
    elif name == "laptop":
        parts = [
            outline(rect_d(-14, -14, 28, 19, 2.5)),
            outline("M-19 9H19L16 14H-16Z"),
        ]
    else:
        raise ValueError(name)
    icon = VGroup(*parts)
    if height is not None:
        icon.set_height(height)
    return icon
