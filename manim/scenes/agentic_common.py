"""
Shared pieces for the "from next-word prediction to agentic AI" scenes:
software and chat windows, the 3b1b model drawing, the input the software
assembles for it, next-word bar charts (real model data), special-word
chips, chat bubbles and the dashed box for a reasoning model's thoughts.

New code here uses explicit hex colors (PALETTE below) rather than the
theme-rebound 3b1b names, so what you read is what you get.
"""
import json
from pathlib import Path

from manim_imports_ext import *
from _2024.transformers.chm import PredictTheNextWord
from scenes.stills import BuildStills

# Palette (matches the light 3b1b renders and the schematic's roles)
INK = "#1B1F2A"            # text
MUTED = "#6B7280"          # secondary text
FRAME_GREY = "#9AA0A6"     # window outlines
PANEL_FILL = "#F4F5F7"     # code panel, bot bubbles
ACCENT = "#2F6FB0"         # progression, trained model
TRAINED_FILL = "#A9C6E8"   # trained model blocks
UNTRAINED_FILL = "#C4C4C4" # untrained model blocks
USER_FILL = "#E2EDF8"      # user bubbles
TOOL_COLOR = "#2A9D8F"     # tool use (teal)
WARN = "#C77700"           # hallucination warnings (amber)
WARN_FILL = "#FCEBC9"
CHIP_FILL = "#262A33"      # special words
BAR_COLOR = "#5CC4AC"
MONO = "Menlo"

SPECIAL_WORDS = ("STOP", "TOOL", "THINK", "ANSWER")


# Small building blocks

def text(string, font_size=24, color=INK, **kwargs):
    return Text(string, font_size=font_size, **kwargs).set_color(color)


def mono(string, font_size=20, color=INK):
    return Text(string, font=MONO, font_size=font_size).set_color(color)


def chip(word, font_size=20):
    """Dark rounded tag for a special word like STOP or TOOL."""
    label = Text(word, font=MONO, font_size=font_size, weight=BOLD)
    label.set_color(TRUE_WHITE)
    bg = RoundedRectangle(
        label.get_width() + 0.3 * font_size / 20,
        label.get_height() + 0.2 * font_size / 20,
        corner_radius=0.06 * font_size / 20,
    )
    bg.set_fill(CHIP_FILL, 1).set_stroke(width=0)
    bg.move_to(label)
    result = VGroup(bg, label)
    result.word = word
    return result


def word_mob(word, font_size=24, color=INK):
    """A word for running text; special words become chips."""
    stripped = word.strip()
    if stripped in SPECIAL_WORDS:
        return chip(stripped, font_size=0.8 * font_size)
    return text(stripped, font_size=font_size, color=color)


def bubble_around(mob, fill, buff=0.18, corner_radius=0.15):
    bg = RoundedRectangle(
        mob.get_width() + 2 * buff,
        mob.get_height() + 2 * buff,
        corner_radius=corner_radius,
    )
    bg.set_fill(fill, 1).set_stroke(width=0)
    bg.move_to(mob)
    return bg


def person_icon(height=0.4, color=MUTED):
    body = Circle(radius=0.5).set_fill(color, 1).set_stroke(width=0)
    head = Circle(radius=0.17).set_fill(TRUE_WHITE, 1).set_stroke(width=0)
    head.move_to(0.12 * UP)
    shoulders = Arc(start_angle=0, angle=PI, radius=0.3)
    shoulders.close_path()
    shoulders.set_fill(TRUE_WHITE, 1).set_stroke(width=0)
    shoulders.move_to(0.3 * DOWN)
    icon = VGroup(body, head, shoulders)
    # Clip the shoulders to the disc by drawing a ring over them
    ring = Annulus(inner_radius=0.5, outer_radius=0.62).set_fill(TRUE_WHITE, 1).set_stroke(width=0)
    icon.add(ring)
    return icon.set_height(height)


def robot_icon(height=0.4, color=ACCENT):
    head = RoundedRectangle(1.0, 0.75, corner_radius=0.18)
    head.set_fill(color, 1).set_stroke(width=0)
    eyes = VGroup(Dot(radius=0.09), Dot(radius=0.09)).arrange(RIGHT, buff=0.28)
    eyes.set_fill(TRUE_WHITE, 1).move_to(head).shift(0.03 * UP)
    antenna = Line(head.get_top(), head.get_top() + 0.22 * UP).set_stroke(color, 6)
    knob = Dot(antenna.get_end(), radius=0.08).set_fill(color, 1)
    ears = VGroup(
        RoundedRectangle(0.1, 0.3, corner_radius=0.04).next_to(head, side, buff=0)
        for side in [LEFT, RIGHT]
    ).set_fill(color, 1).set_stroke(width=0)
    return VGroup(head, eyes, antenna, knob, ears).set_height(height)


def warning_sign(height=0.3):
    tri = RegularPolygon(3, start_angle=PI / 2)
    tri.set_fill(WARN, 1).set_stroke(WARN, 2)
    mark = Text("!", font_size=40, weight=BOLD).set_color(TRUE_WHITE)
    mark.set_height(0.5 * tri.get_height()).move_to(tri).shift(0.1 * tri.get_height() * DOWN)
    return VGroup(tri, mark).set_height(height)


def warning_label(lines, font_size=22, width=None):
    words = VGroup(text(line, font_size=font_size, color=WARN, weight=BOLD) for line in lines)
    words.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    sign = warning_sign(height=0.35 * font_size / 22 * 1.0)
    sign.next_to(words[0], LEFT, buff=0.15)
    return VGroup(sign, words)


def app_window(width, height, title="", title_font_size=18, bar_height=0.38):
    """Rounded window with a title bar: the software (or chat) the model lives in."""
    body = RoundedRectangle(width, height, corner_radius=0.14)
    body.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 2)
    bar_line = Line(LEFT, RIGHT).set_width(width).set_stroke(FRAME_GREY, 1.5)
    bar_line.move_to(body.get_top() + bar_height * DOWN)
    dots = VGroup(Dot(radius=0.045) for _ in range(3)).arrange(RIGHT, buff=0.07)
    dots.set_fill(FRAME_GREY, 1)
    dots.move_to(body.get_corner(UL) + 0.5 * bar_height * DOWN, LEFT).shift(0.18 * RIGHT)
    code_mark = text("</>", font_size=title_font_size, color=FRAME_GREY)
    code_mark.move_to(body.get_corner(UR) + 0.5 * bar_height * DOWN, RIGHT).shift(0.18 * LEFT)
    title_mob = text(title, font_size=title_font_size, color=MUTED)
    title_mob.move_to(body.get_top() + 0.5 * bar_height * DOWN)
    window = VGroup(body, bar_line, dots, code_mark, title_mob)
    window.body = body
    window.title = title_mob
    window.bar_height = bar_height
    return window


def window_content_top(window, buff=0.25):
    return window.body.get_top()[1] - window.bar_height - buff


def flow_arrow(*points, color=MUTED, stroke_width=2.5, tip=True):
    """Right-angled connector through the given points, with an arrow tip."""
    points = [np.array(p, dtype=float) for p in points]
    line = Polyline(*points).set_stroke(color, stroke_width)
    result = VGroup(line)
    if tip:
        direction = points[-1] - points[-2]
        tip_mob = ArrowTip(angle=angle_of_vector(direction), width=0.16, length=0.16)
        tip_mob.set_fill(color, 1)
        tip_mob.shift(points[-1] - tip_mob.get_tip_point())
        line.set_points_as_corners([*points[:-1], points[-1] - 0.12 * normalize(direction)])
        result.add(tip_mob)
    return result


def doc_icon(height=0.38, color=MUTED):
    page = RoundedRectangle(0.8 * height, height, corner_radius=0.04)
    page.set_fill(TRUE_WHITE, 1).set_stroke(color, 2)
    lines = VGroup(
        Line(ORIGIN, w * 0.5 * height * RIGHT) for w in [1, 0.8, 1, 0.6]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.12 * height)
    lines.set_stroke(color, 1.5).move_to(page)
    return VGroup(page, lines)


def bar_chart(words, probs, max_len=1.8, bar_height=0.27, font_size=24, pct_labels=None, n_main=None):
    """
    Next-word distribution: label | bar | percentage, plus a vdots row.
    Rows after the first n_main go below the dots (e.g. a rare word worth showing).
    """
    n_main = n_main or len(words)
    rows = VGroup()
    top = max(probs)
    for n, (word, prob) in enumerate(zip(words, probs)):
        label = word_mob(word, font_size=font_size)
        bar = Rectangle(max(prob / top * max_len, 0.02), bar_height)
        bar.set_fill(BAR_COLOR, 1).set_stroke(TRUE_WHITE, 1)
        pct = pct_labels[n] if pct_labels else f"{100 * prob:.0f}%"
        pct_mob = text(pct, font_size=0.8 * font_size, color=MUTED)
        rows.add(VGroup(label, bar, pct_mob))
    for n, row in enumerate(rows):
        label, bar, pct = row
        bar.move_to((n + (n >= n_main)) * 1.4 * bar_height * DOWN, LEFT)
        label.next_to(bar, LEFT, buff=0.12)
        pct.next_to(bar, RIGHT, buff=0.08)
    dots = Tex(R"\vdots", font_size=font_size).set_color(MUTED)
    dots.next_to(rows[n_main - 1][0], DOWN, buff=0.12)
    chart = VGroup(*rows, dots)
    chart.rows = rows
    return chart


class FlowText(VGroup):
    """
    Running text that wraps inside a fixed width; words (and special-word
    chips) are added one at a time without moving the earlier ones.
    """
    def __init__(self, top_left, width, font_size=24, line_height=None, slant=NORMAL, **kwargs):
        super().__init__(**kwargs)
        self.top_left = np.array(top_left)
        self.max_width = width
        self.font_size = font_size
        self.slant = slant
        self.line_height = line_height or 0.42 * font_size / 24
        self.space = 0.09 * font_size / 24
        self.n_lines = 1
        self.break_pending = False

    def next_word(self, word, color=INK):
        """
        Create the next word, already in its final position (not added).
        word can also be a mobject (e.g. a pill), placed like a special-word chip.
        """
        if isinstance(word, Mobject):
            mob = word
            strut = None
            width = mob.get_width()
        elif word.strip() in SPECIAL_WORDS:
            stripped = word.strip()
            mob = chip(stripped, font_size=0.8 * self.font_size)
            strut = None
            width = mob.get_width()
        else:
            stripped = word.strip()
            # Lay the word out after an "A" (no descender) so that every
            # word shares a baseline: the A's bottom is the baseline
            full = text("A" + stripped, font_size=self.font_size, color=color, slant=self.slant)
            strut = full[0]
            width = full[1:].get_width()
        line_start = len(self) == 0
        if self.break_pending and len(self) > 0:
            self.n_lines += 1
            line_start = True
        self.break_pending = False
        baseline_y = self.top_left[1] - self.n_lines * self.line_height + 0.3 * self.line_height
        if line_start:
            x = self.top_left[0]
        else:
            x = self[-1].get_right()[0] + self.space
            if x + width > self.top_left[0] + self.max_width:
                self.n_lines += 1
                baseline_y -= self.line_height
                x = self.top_left[0]
        if strut is None:
            x_height = 0.12 * self.font_size / 24
            mob.move_to([x, baseline_y + x_height, 0], LEFT)
        else:
            full.shift([x - full[1:].get_left()[0], baseline_y - strut.get_bottom()[1], 0])
            # Slice after moving: a slice caches its bounding box
            mob = full[1:]
        return mob

    def add_word(self, word, color=INK):
        mob = self.next_word(word, color)
        self.add(mob)
        return mob

    def add_words(self, words, color=INK):
        return VGroup(self.add_word(word, color) for word in words)

    def line_break(self):
        """Start the next word on a new line."""
        self.break_pending = True

    def get_bottom_y(self):
        return self.top_left[1] - self.n_lines * self.line_height


class ChatBubble(VGroup):
    """Bubble whose background follows the FlowText inside it."""
    def __init__(self, flow, fill, buff=0.16, **kwargs):
        self.flow = flow
        self.fill = fill
        self.buff = buff
        self.bg = self.get_bg()
        super().__init__(self.bg, flow, **kwargs)

    def get_bg(self):
        flow = self.flow
        if len(flow) == 0:
            width, height = 0.4, flow.line_height
            center = flow.top_left + np.array([width / 2, -height / 2, 0])
        else:
            width = flow.get_width()
            height = flow.top_left[1] - flow.get_bottom()[1]
            height = max(height, flow.line_height * flow.n_lines)
            center = np.array([flow.get_center()[0], flow.top_left[1] - height / 2, 0])
        bg = RoundedRectangle(width + 2 * self.buff, height + 1.4 * self.buff, corner_radius=0.15)
        bg.set_fill(self.fill, 1).set_stroke(width=0)
        bg.move_to(center)
        return bg

    def refresh(self):
        self.bg.become(self.get_bg())
        return self

    def reveal(self):
        self.bg.set_opacity(1)


class ThoughtBubble(VGroup):
    """
    Dashed box for a reasoning model's private thoughts, as wide as the chat.
    It grows with its parts: running text (FlowText) and e.g. tool results.
    """
    def __init__(self, top_left, width, buff=0.12, **kwargs):
        self.top_left = np.array(top_left)
        self.box_width = width
        self.buff = buff
        self.parts = []
        self.keep = VGroup()  # parts that stay visible when the thoughts are folded away
        self.bg = self.get_bg()
        super().__init__(self.bg, **kwargs)

    def add_flow(self, top_y, font_size):
        flow = FlowText(
            [self.top_left[0] + self.buff, top_y, 0], self.box_width - 2 * self.buff,
            font_size=font_size, slant=ITALIC,
        )
        self.add_part(flow)
        return flow

    def add_part(self, part):
        self.parts.append(part)
        self.add(part)

    def get_bottom_y(self):
        ys = [
            part.get_bottom_y() if isinstance(part, FlowText) else part.get_bottom()[1]
            for part in self.parts
        ]
        return min(ys, default=self.top_left[1] - 0.3)

    def get_bg(self):
        height = self.top_left[1] - self.get_bottom_y() + self.buff
        rect = RoundedRectangle(self.box_width, height, corner_radius=0.15)
        rect.set_fill(opacity=0).set_stroke(FRAME_GREY, 1.5)
        rect.move_to(self.top_left, UL)
        return DashedVMobject(rect, num_dashes=80)

    def refresh(self):
        self.bg.become(self.get_bg())
        return self

    def reveal(self):
        pass


# Next-word distributions computed with real models (tools/compute_distributions.py)

DISTRIBUTIONS = json.loads(Path(__file__).parents[1].joinpath("data", "agentic_distributions.json").read_text())


def pct_label(p):
    if p >= 0.0995:
        return f"{100 * p:.0f}%"
    if p >= 0.01:
        return f"{100 * p:.1f}%".replace(".0%", "%")
    if p >= 0.001:
        return f"{100 * p:.1f}%"
    return "<0.1%"


# The scene base class

class AgenticScene(BuildStills, PredictTheNextWord):
    """
    Layout shared by the four stage scenes. In the software window, the
    input is assembled on the left (system prompt + conversation), passes
    through the model in the middle, and the next-word distribution appears
    on the right; the picked word goes to the chat, which the next input is
    built from. The chat window is on the far right.
    """
    machine_name = "Large\nLanguage\nModel"
    stage_number = 1
    stage_title = ""
    stage_subtitle = ""
    question = "What do recent papers say about microplastics and health?"
    trained = True
    # Chat format: System/User/Assistant turns, each closed by STOP
    roles = False
    system_prompt = None  # list of (string, color)
    # The software's stop rule: "count" (10 words) or "stop" (the word STOP)
    stop_rule = "count"
    # Special words always listed below the bars
    special_rows = ()
    # Passes during which the whole input is visibly re-assembled
    n_detailed = 3
    window_left, window_right = -6.95, 2.65
    chat_left, chat_right = 2.9, 6.95
    window_top, window_bottom = 2.75, -3.4
    input_right = -3.6
    input_bottom = -3.25
    model_center = (-1.85, 0.35)
    input_font_size = 18
    chat_font_size = 20

    def construct(self):
        pass

    # Layout

    def get_title(self):
        number = VGroup(
            Circle(radius=0.26).set_fill(ACCENT, 1).set_stroke(width=0),
            text(str(self.stage_number), font_size=30, color=TRUE_WHITE, weight=BOLD),
        )
        number[1].move_to(number[0])
        title = text(self.stage_title, font_size=40, weight=BOLD)
        subtitle = text(self.stage_subtitle, font_size=26, color=MUTED)
        number.move_to([self.window_left + 0.26, 3.5, 0])
        title.next_to(number, RIGHT, buff=0.2)
        subtitle.next_to(title, RIGHT, buff=0.4, aligned_edge=DOWN)
        return VGroup(number, title, subtitle)

    def get_window(self, left, right, title):
        window = app_window(right - left, self.window_top - self.window_bottom, title=title)
        window.move_to([(left + right) / 2, (self.window_top + self.window_bottom) / 2, 0])
        return window

    def get_model(self, trained=None):
        trained = self.trained if trained is None else trained
        machine = self.get_transformer_drawing()
        blocks, label = machine[:2]
        blocks.set_fill(TRAINED_FILL if trained else UNTRAINED_FILL, 1)
        label.set_color(INK).set_backstroke(TRUE_WHITE, 6)
        label.set_z_index(1)
        label.scale(0.8).shift(0.12 * RIGHT)
        flat_dials, last_dials = self.get_machine_dials(blocks)
        last_dials.set_stroke(opacity=0.12)
        blocks[-1].add(last_dials)
        machine.set_height(1.6)
        machine.move_to([*self.model_center, 0])
        machine.shift((self.input_right + 0.6 - blocks.get_left()[0]) * RIGHT)
        self.blocks = blocks
        self.dials = last_dials
        return machine

    def get_weights_label(self, string):
        label = text(string, font_size=18, color=MUTED)
        label.next_to(self.machine[0], UP, buff=0.15)
        return label

    def get_input_card(self):
        left = self.window_left + 0.15
        top = window_content_top(self.software_window, 0.12)
        bg = RoundedRectangle(self.input_right - left, top - self.input_bottom, corner_radius=0.1)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1.5)
        bg.move_to([left, top, 0], UL)
        title = text("Input", font_size=17, color=MUTED, weight=BOLD)
        title.move_to(bg.get_corner(UL) + [0.15, -0.12, 0], UL)
        card = VGroup(bg, title)
        card.bg = bg
        card.title = title
        return card

    def new_input_flow(self, top_y):
        bg = self.input_card.bg
        return FlowText(
            [bg.get_left()[0] + 0.15, top_y, 0], bg.get_width() - 0.3,
            font_size=self.input_font_size,
        )

    def get_system_block(self):
        """The system prompt, at the top of the input from the start."""
        flow = self.new_input_flow(self.input_card.title.get_bottom()[1] - 0.12)
        flow.add_word("System:", color=MUTED)
        segments = VGroup(flow.add_words(string.split(" "), color=color) for string, color in self.system_prompt)
        flow.add_word("STOP")
        bg = SurroundingRectangle(flow, buff=0.06).round_corners(0.05)
        bg.set_fill(PANEL_FILL, 1).set_stroke(width=0)
        block = VGroup(bg, flow)
        block.flow = flow
        block.segments = segments
        return block

    def get_arrows(self):
        body = self.machine[0]
        y = body.get_y()
        in_arrow = Arrow([self.input_right + 0.05, y, 0], body.get_left() + 0.05 * LEFT, buff=0, thickness=4)
        out_arrow = Arrow(body.get_right() + 0.05 * RIGHT, body.get_right() + 0.5 * RIGHT, buff=0, thickness=4)
        return VGroup(in_arrow, out_arrow).set_fill(MUTED)

    def get_rule_badge(self):
        if self.stop_rule == "count":
            self.counter = mono("0/10", font_size=15, color=MUTED)
            content = VGroup(text("max 10 words", font_size=16, color=MUTED), self.counter)
        else:
            content = VGroup(text("until", font_size=16, color=MUTED), chip("STOP", font_size=13))
        content.arrange(RIGHT, buff=0.1)
        self.rule_target = content[-1]
        rows = [content]
        if "TOOL" in self.special_rows:
            rows.append(VGroup(chip("TOOL", font_size=13), text("call: run tool", font_size=16, color=MUTED)))
        if "THINK" in self.special_rows:
            rows.append(VGroup(chip("THINK", font_size=13), text("private thoughts", font_size=16, color=MUTED)))
            rows.append(VGroup(chip("ANSWER", font_size=13), text("shown as answer", font_size=16, color=MUTED)))
        for row in rows[1:]:
            row.arrange(RIGHT, buff=0.1)
        content = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        bg = SurroundingRectangle(content, buff=0.08).round_corners(0.08)
        bg.set_fill(PANEL_FILL, 1).set_stroke(width=0)
        badge = VGroup(bg, content)
        badge.next_to(self.machine[0], DOWN, buff=0.25)
        return badge

    def get_user_bubble(self):
        icon = person_icon(0.38)
        flow = FlowText(ORIGIN, 3.0, font_size=self.chat_font_size)
        flow.add_words(self.question.split(" "))
        flow.move_to([self.chat_right - 0.75, window_content_top(self.chat_window, 0.3), 0], UR)
        flow.top_left = np.array([flow.get_left()[0], flow.get_top()[1], 0])
        bubble = ChatBubble(flow, USER_FILL, buff=0.13)
        icon.move_to([self.chat_right - 0.35, bubble.bg.get_y(), 0])
        group = VGroup(bubble, icon)
        group.flow = flow
        return group

    def get_answer(self, top_y, with_icon=True):
        """Empty assistant bubble with the robot icon; returns (group, flow, bubble)."""
        icon = robot_icon(0.36)
        icon.move_to([self.chat_left + 0.3, top_y - 0.18, 0])
        if not with_icon:
            icon.set_opacity(0)
        flow = FlowText([self.chat_left + 0.72, top_y - 0.08, 0], 3.1, font_size=self.chat_font_size)
        bubble = ChatBubble(flow, PANEL_FILL, buff=0.12)
        bubble.bg.set_opacity(0)
        return VGroup(icon, bubble), flow, bubble

    def get_thought(self, top_y):
        """
        Empty box for the private thoughts with the robot icon; returns
        (icon, flow, bubble). Picked words go here until ANSWER.
        """
        icon = robot_icon(0.36)
        icon.move_to([self.chat_left + 0.3, top_y - 0.18, 0])
        left = self.chat_left + 0.6
        bubble = ThoughtBubble([left, top_y, 0], self.chat_right - 0.15 - left)
        flow = bubble.add_flow(top_y - 0.06, self.chat_font_size - 2)
        bubble.refresh()
        self.thought_bubble = bubble
        self.chat = (flow, bubble)
        return icon, flow, bubble

    def get_folded_thought(self):
        """What is left of the thoughts once the answer starts: one dashed line."""
        content = VGroup(
            chip("THINK", font_size=0.8 * (self.chat_font_size - 2)),
            text("Private thoughts", font_size=self.chat_font_size - 2, color=MUTED, slant=ITALIC),
            text("▸", font_size=self.chat_font_size - 2, color=MUTED),
        ).arrange(RIGHT, buff=0.1)
        rect = SurroundingRectangle(content, buff=0.1).round_corners(0.12)
        rect.set_fill(opacity=0).set_stroke(FRAME_GREY, 1.5)
        folded = VGroup(DashedVMobject(rect, num_dashes=40), content)
        folded.move_to(self.thought_bubble.top_left, UL)
        return folded

    def start_answer(self):
        """
        ANSWER ends the private thoughts: the software folds them away (they
        stay in the input) and opens the answer bubble. Returns (flow, bubble).
        """
        thought = self.thought_bubble
        anims = []
        if self.pending is not None:
            anims.append(self.append_to_input(*self.pending))
            self.pending = None
        folded = self.get_folded_thought()
        keep = thought.keep
        hidden = VGroup(*(part for part in [thought.bg, *thought.parts] if part not in keep))
        target_keep = keep.copy().next_to(folded, DOWN, buff=0.1, aligned_edge=LEFT)
        anims += [FadeOut(hidden), FadeIn(folded), Transform(keep, target_keep)]
        self.play(*anims, run_time=0.8)
        self.add(folded, keep)
        self.folded_thought = folded
        top_y = VGroup(folded, keep).get_bottom()[1] - 0.12
        group, flow, bubble = self.get_answer(top_y, with_icon=False)
        self.thought_bubble = None
        return flow, bubble

    def setup_stage(self):
        self.software_window = self.get_window(self.window_left, self.window_right, "Software")
        self.chat_window = self.get_window(self.chat_left, self.chat_right, "Chat")
        self.machine = self.get_model()
        self.input_card = self.get_input_card()
        self.system_block = self.get_system_block() if self.system_prompt else None
        top = (self.system_block.get_bottom()[1] - 0.05) if self.system_block else self.input_card.title.get_bottom()[1] - 0.12
        self.convo_top = top
        self.input_flow = self.new_input_flow(top)
        self.input_convo = VGroup()
        self.arrows = self.get_arrows()
        self.rule_badge = self.get_rule_badge()
        self.title_group = self.get_title()
        self.user_bubble = self.get_user_bubble()
        # The conversation, as the software keeps it: turns of (word, color, chat mob)
        self.turns = [dict(role="User:", items=[
            (word, INK, mob) for word, mob in zip(self.question.split(" "), self.user_bubble.flow)
        ], closed=True)]
        self.pending = None
        # Where picked words go: (flow, bubble); switches when ANSWER ends the thoughts
        self.chat = None
        self.thought_bubble = None

    def open_turn(self, role="Assistant:"):
        self.turns.append(dict(role=role, items=[], closed=False))

    # Assembling the input

    def input_specs(self):
        """(word, color, source mob, line break before) for the conversation part of the input."""
        specs = []
        for turn in self.turns:
            if self.roles:
                specs.append((turn["role"], MUTED, None, True))
            specs += [(word, color, source, False) for word, color, source in turn["items"]]
            if self.roles and turn["closed"]:
                specs.append(("STOP", INK, None, False))
        return specs

    def rebuild_input(self, run_time=1.5):
        """
        The software builds the input from scratch: system prompt (already
        there) + the whole conversation so far, copied from the chat.
        """
        old = self.input_convo
        flow = self.new_input_flow(self.convo_top)
        anims = []
        for n, (word, color, source, new_line) in enumerate(self.input_specs()):
            if new_line and n > 0:
                flow.line_break()
            mob = flow.add_word(word, color)
            if source is not None:
                anims.append(TransformFromCopy(source, mob, path_arc=20 * DEGREES))
            else:
                anims.append(FadeIn(mob))
        if len(old) > 0:
            self.play(FadeOut(old), run_time=0.3)
        self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=run_time)
        self.input_flow = flow
        self.input_convo = VGroup(*flow)
        self.pending = None

    def append_to_input(self, word, color, source):
        mob = self.input_flow.add_word(word, color)
        self.input_convo.add(mob)
        return TransformFromCopy(source, mob, path_arc=20 * DEGREES)

    def input_content(self):
        return VGroup(*([self.system_block.flow] if self.system_block else []), self.input_convo)

    # One pass through the model

    def pulse(self, mob, color=BAR_COLOR, **kwargs):
        return mob.animate.set_color(color).set_anim_args(rate_func=there_and_back, **kwargs)

    def block_flash(self, color=BAR_COLOR, run_time=1.0):
        blocks = self.blocks
        return LaggedStart(
            (
                block.animate.set_fill(color).set_anim_args(rate_func=there_and_back)
                for block in blocks[:-1]
            ),
            lag_ratio=0.1,
            run_time=run_time,
            group=blocks,
        )

    def randomize_dials(self, run_time=2, lag_factor=0.5):
        dials = self.dials
        return LaggedStart(
            (dial.animate_set_value(dial.get_random_value()) for dial in dials),
            lag_ratio=lag_factor / len(dials),
            run_time=run_time,
        )

    def distribution_from_record(self, record):
        """Rows for the chart: the picked word and the top others, then the special words."""
        word = record["word"]
        rows = [] if word in SPECIAL_WORDS else [(word, record["p"])]
        rows += [(label, p) for label, p in record["others"] if len(label) <= 12]
        rows = sorted(rows, key=lambda r: -r[1])[:5]
        if word not in SPECIAL_WORDS and word not in [r[0] for r in rows]:
            rows[-1] = (word, record["p"])
        n_main = len(rows)
        rows += [(name, record["special"].get(name, 0)) for name in self.special_rows]
        words = [r[0] for r in rows]
        return words, [r[1] for r in rows], [pct_label(r[1]) for r in rows], n_main, words.index(word)

    def get_chart(self, words, probs, pct_labels, n_main=None):
        chart = bar_chart(words, probs, max_len=1.0, bar_height=0.24, font_size=19, pct_labels=pct_labels, n_main=n_main)
        out_end = self.arrows[1].get_end()
        chart.shift((out_end[0] + 1.2 - chart.rows[0][1].get_left()[0]) * RIGHT)
        chart.match_y(self.machine[0])
        return chart

    def get_pick_rect(self, row):
        return SurroundingRectangle(row, buff=0.04).set_stroke(WARN, 2).set_fill(WARN, 0.15)

    def feed_model(self, run_time=1.2):
        """The whole input flows into the model, whose layers light up."""
        point = VGroup(VectorizedPoint(self.machine[0].get_left()))
        self.play(
            LaggedStart(
                self.pulse(self.arrows[0]),
                TransformFromCopy(self.input_content(), point, lag_ratio=0.002, remover=True),
                self.block_flash(),
                lag_ratio=0.3,
            ),
            run_time=run_time,
        )

    def pick(self, chart, index, run_time=0.9, seed=0):
        """Highlight hops around the bars, weighted by size, and lands on index."""
        rows = chart.rows
        widths = np.array([row[1].get_width() for row in rows])
        dist = widths / widths.sum()
        rect = self.get_pick_rect(rows[index])

        def update(mob, alpha):
            np.random.seed(seed + int(8 * alpha))
            i = index if alpha > 0.85 else np.random.choice(len(rows), p=dist)
            mob.surround(rows[i], buff=0.04)

        self.play(UpdateFromAlphaFunc(rect, update), run_time=run_time)
        chart.add(rect)

    def deliver(self, chart, index, word, color, chat, run_time=0.6):
        """
        The picked word goes to the chat (it becomes part of the
        conversation). STOP instead goes to the software's rule and ends it.
        ANSWER ends the private thoughts and starts the answer.
        """
        if word == "ANSWER" and self.thought_bubble is not None:
            chat = self.chat = self.start_answer()
        source = chart.rows[index][0].copy()
        if word == "STOP":
            self.play(
                source.animate.move_to(self.rule_target).set_opacity(0),
                self.pulse(self.rule_badge[0], color=WARN_FILL),
                FadeOut(chart),
                run_time=run_time,
            )
            self.remove(source)
            return None
        flow, bubble = chat
        target = flow.next_word(word, color)
        self.play(
            FadeTransform(source, target),
            UpdateFromFunc(bubble.bg, lambda m: bubble.reveal()),
            FadeOut(chart),
            run_time=run_time,
        )
        flow.add(target)
        bubble.refresh()
        self.add(bubble)
        self.turns[-1]["items"].append((word, color, target))
        self.pending = (word, color, target)
        return target

    def run_pass(self, n, distribution, chat=None, color=INK, fast_time=0.5):
        """
        Pass n (from 0) through the loop. The first n_detailed passes show
        every step: the input is re-assembled, flows into the model, the
        distribution appears and a word is picked. Later passes only add the
        newest word to the input and go quickly.
        """
        words, probs, pct_labels, n_main, index = distribution
        word = words[index]
        chat = chat or self.chat
        if self.stop_rule == "count":
            self.update_counter(n + 1)
        if n < self.n_detailed:
            self.rebuild_input()
            self.feed_model()
            chart = self.get_chart(words, probs, pct_labels, n_main)
            self.play(LaggedStart((FadeIn(row, 0.1 * RIGHT) for row in chart), lag_ratio=0.05), run_time=0.6)
            self.pick(chart, index, seed=n)
            return self.deliver(chart, index, word, color, chat, run_time=0.7)
        chart = self.get_chart(words, probs, pct_labels, n_main)
        chart.add(self.get_pick_rect(chart.rows[index]))
        anims = [self.pulse(self.arrows[0]), self.block_flash(run_time=fast_time), FadeIn(chart, lag_ratio=0.02)]
        if self.pending is not None:
            anims.insert(0, self.append_to_input(*self.pending))
            self.pending = None
        self.play(*anims, run_time=fast_time)
        return self.deliver(chart, index, word, color, chat, run_time=0.8 * fast_time)

    def skip_pass(self, n_words, run_time=1.6):
        """
        Many passes at once, for the words of the thoughts that are not shown
        one by one: the model runs n_words more times, and the chat and the
        input only get "…".
        """
        anims = []
        if self.pending is not None:
            anims.append(self.append_to_input(*self.pending))
            self.pending = None
        count = Integer(0, font_size=22).set_color(MUTED)
        label = VGroup(text("+", font_size=22, color=MUTED), count, text("words", font_size=22, color=MUTED))
        label.arrange(RIGHT, buff=0.08)
        label.move_to(self.arrows[1].get_end() + 1.3 * RIGHT)
        n_flashes = 5
        flashes = Succession(*(self.block_flash(run_time=run_time / n_flashes) for _ in range(n_flashes)))
        self.add(label)
        self.play(
            *anims, flashes,
            self.pulse(self.arrows[0], run_time=run_time),
            ChangeDecimalToValue(count, n_words, run_time=run_time),
            run_time=run_time,
        )
        flow, bubble = self.chat
        dots = flow.next_word("…", MUTED)
        self.play(FadeIn(dots, scale=0.5), FadeOut(label), run_time=0.4)
        flow.add(dots)
        bubble.refresh()
        self.turns[-1]["items"].append(("…", MUTED, dots))
        self.pending = ("…", MUTED, dots)

    def run_records(self, records, n0=0, colors=None, fast_time=0.35):
        """
        Passes for a list of records (tools/compute_distributions.py), with
        {"skip": n} entries for words that are not shown. colors(record)
        gives each word's color in the chat.
        """
        n = n0
        for record in records:
            if "skip" in record:
                self.skip_pass(record["skip"])
                continue
            color = colors(record) if colors else INK
            self.run_pass(n, self.distribution_from_record(record), color=color, fast_time=fast_time)
            n += 1
        return n

    def thought_color(self, record):
        """Words of the thoughts are grey; the answer is in the normal color."""
        return MUTED if self.thought_bubble is not None and record["word"] != "ANSWER" else INK

    def update_counter(self, n, total=10):
        self.counter.become(mono(f"{n}/{total}", font_size=15, color=MUTED).move_to(self.counter))

    def flash_rule(self):
        rect = SurroundingRectangle(self.rule_badge, buff=0.05).set_stroke(WARN, 2)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))

    def build_software(self, run_time=2.0):
        parts = [FadeIn(self.input_card), GrowArrow(self.arrows[0]), GrowArrow(self.arrows[1]), FadeIn(self.rule_badge)]
        if self.system_block:
            parts.insert(1, FadeIn(self.system_block))
        return LaggedStart(*parts, lag_ratio=0.3, run_time=run_time)

    def highlight_words(self, words, color=WARN, fill=WARN_FILL):
        highlights = VGroup(
            SurroundingRectangle(word, buff=0.035).set_fill(fill, 1).set_stroke(width=0)
            for word in words
        )
        underlines = VGroup(
            DashedLine(word.get_corner(DL), word.get_corner(DR), dash_length=0.05).shift(0.04 * DOWN)
            for word in words
        ).set_stroke(color, 2)
        return highlights, underlines
