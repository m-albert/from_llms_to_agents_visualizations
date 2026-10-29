"""
Shared pieces for the "from next-word prediction to agentic AI" scenes:
software and chat windows, the 3b1b model drawing, the software loop shown
as pseudo-code, special-word chips, bar charts and chat bubbles.

New code here uses explicit hex colors (PALETTE below) rather than the
theme-rebound 3b1b names, so what you read is what you get.
"""
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

SPECIAL_WORDS = ("STOP", "TOOL")


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


class CodePanel(VGroup):
    """The software's loop, as pseudo-code, with a line highlighter."""
    def __init__(self, lines, width, height=None, font_size=20, line_buff=0.2, **kwargs):
        line_mobs = VGroup(
            mono(line if line.strip() else ".", font_size=font_size)
            for line in lines
        )
        for line, mob in zip(lines, line_mobs):
            if not line.strip():
                mob.set_opacity(0)
            # Indentation in monospace: shift by the width of a character
        line_mobs.arrange(DOWN, aligned_edge=LEFT, buff=line_buff)
        char_width = mono("x" * 10, font_size=font_size).get_width() / 10
        for line, mob in zip(lines, line_mobs):
            indent = len(line) - len(line.lstrip(" "))
            mob.shift(indent * char_width * RIGHT)
        self.recolor_special_words(lines, line_mobs)

        height = height or line_mobs.get_height() + 0.5
        bg = RoundedRectangle(width, height, corner_radius=0.1)
        bg.set_fill(PANEL_FILL, 1).set_stroke(width=0)
        line_mobs.move_to(bg, LEFT).shift(0.25 * RIGHT)

        highlight = Rectangle(width - 0.2, line_mobs[0].get_height() + 0.14)
        highlight.set_fill(BAR_COLOR, 0.3).set_stroke(BAR_COLOR, 1.5)
        highlight.move_to(line_mobs[0]).match_x(bg)
        highlight.set_opacity(0)

        super().__init__(bg, line_mobs, highlight, **kwargs)
        self.bg = bg
        self.lines = line_mobs
        self.highlight = highlight

    def recolor_special_words(self, lines, line_mobs):
        for line, mob in zip(lines, line_mobs):
            if "#" in line:
                mob[line[line.index("#"):].strip()].set_color(MUTED)
            for word in SPECIAL_WORDS:
                if word in line:
                    for part in mob[word]:
                        part.set_color(WARN if word == "STOP" else TOOL_COLOR)
                        part.set_fill(CHIP_FILL)

    def highlight_line(self, index, **kwargs):
        target = self.highlight.generate_target()
        target.match_y(self.lines[index])
        target.set_fill(opacity=0.3).set_stroke(opacity=1)
        return MoveToTarget(self.highlight, **kwargs)

    def unhighlight(self):
        return self.highlight.animate.set_opacity(0)


def bar_chart(words, probs, max_len=1.8, bar_height=0.27, font_size=24, pct_labels=None):
    """Next-word distribution: label | bar | percentage, plus a vdots row."""
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
        bar.move_to(n * 1.4 * bar_height * DOWN, LEFT)
        label.next_to(bar, LEFT, buff=0.12)
        pct.next_to(bar, RIGHT, buff=0.08)
    dots = Tex(R"\vdots", font_size=font_size).set_color(MUTED)
    dots.next_to(rows[-1][0], DOWN, buff=0.12)
    chart = VGroup(*rows, dots)
    chart.rows = rows
    return chart


class FlowText(VGroup):
    """
    Running text that wraps inside a fixed width; words (and special-word
    chips) are added one at a time without moving the earlier ones.
    """
    def __init__(self, top_left, width, font_size=24, line_height=None, **kwargs):
        super().__init__(**kwargs)
        self.top_left = np.array(top_left)
        self.max_width = width
        self.font_size = font_size
        self.line_height = line_height or 0.42 * font_size / 24
        self.space = 0.09 * font_size / 24
        self.n_lines = 1

    def next_word(self, word, color=INK):
        """Create the next word, already in its final position (not added)."""
        stripped = word.strip()
        if stripped in SPECIAL_WORDS:
            mob = chip(stripped, font_size=0.8 * self.font_size)
            strut = None
            width = mob.get_width()
        else:
            # Lay the word out after an "A" (no descender) so that every
            # word shares a baseline: the A's bottom is the baseline
            full = text("A" + stripped, font_size=self.font_size, color=color)
            strut = full[0]
            width = full[1:].get_width()
        baseline_y = self.top_left[1] - self.n_lines * self.line_height + 0.3 * self.line_height
        if len(self) == 0:
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


# The scene base class

class AgenticScene(BuildStills, PredictTheNextWord):
    """
    Layout shared by the four stage scenes: a software window on the left
    (the model, its next-word distribution and the loop that drives it),
    a chat window on the right, and a title on top.
    """
    machine_name = "Large\nLanguage\nModel"
    stage_number = 1
    stage_title = ""
    stage_subtitle = ""
    question = "What do recent papers say about microplastics and health?"
    code_lines = [
        "repeat 10 times:",
        "    probabilities = model(text)",
        "    word = pick(probabilities)",
        "    text = text + word",
    ]
    code_width = 7.8
    # Which code line each step of the loop highlights
    model_line, pick_line, append_line = 1, 2, 3
    trained = True
    window_left, window_right = -6.85, 1.35
    chat_left, chat_right = 1.6, 6.9
    window_top, window_bottom = 2.75, -3.4
    answer_font_size = 26

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

    def get_software_window(self):
        window = app_window(
            self.window_right - self.window_left,
            self.window_top - self.window_bottom,
            title="Software",
        )
        window.move_to([
            (self.window_left + self.window_right) / 2,
            (self.window_top + self.window_bottom) / 2, 0
        ])
        return window

    def get_chat_window(self):
        window = app_window(
            self.chat_right - self.chat_left,
            self.window_top - self.window_bottom,
            title="Chat",
        )
        window.move_to([
            (self.chat_left + self.chat_right) / 2,
            (self.window_top + self.window_bottom) / 2, 0
        ])
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
        machine.set_height(2.2)
        machine.move_to([self.window_left + 1.85, 1.05, 0])
        self.blocks = blocks
        self.dials = last_dials
        return machine

    def get_out_arrow(self, machine):
        arrow = Arrow(
            machine[0].get_right() + 0.05 * RIGHT,
            machine[0].get_right() + 1.0 * RIGHT,
            buff=0, thickness=4,
        )
        arrow.set_fill(MUTED)
        return arrow

    code_font_size = 23

    def get_code_panel(self):
        panel = CodePanel(self.code_lines, width=self.code_width, font_size=self.code_font_size, line_buff=0.24 * self.code_font_size / 23)
        panel.move_to([self.window_left + 0.15, -0.55, 0], UL)
        return panel

    def get_user_bubble(self, string=None, font_size=None):
        font_size = font_size or self.answer_font_size
        string = string or self.question
        icon = person_icon(0.42)
        icon.move_to([self.chat_right - 0.4, 0, 0])
        width = 3.9
        flow = FlowText(ORIGIN, width, font_size=font_size)
        flow.add_words(string.split(" "))
        flow.move_to([self.chat_right - 0.85, window_content_top(self.chat_window, 0.35), 0], UR)
        flow.top_left = np.array([flow.get_left()[0], flow.get_top()[1], 0])
        bubble = ChatBubble(flow, USER_FILL)
        icon.match_y(bubble.bg)
        return VGroup(bubble, icon)

    def get_answer(self, top_y, width=4.1, fill=PANEL_FILL):
        """Empty assistant bubble with the robot icon; returns (group, flow)."""
        icon = robot_icon(0.4)
        icon.move_to([self.chat_left + 0.35, top_y - 0.2, 0])
        flow = FlowText([self.chat_left + 0.85, top_y - 0.1, 0], width, font_size=self.answer_font_size)
        bubble = ChatBubble(flow, fill)
        bubble.bg.set_opacity(0)
        return VGroup(icon, bubble), flow, bubble

    def setup_stage(self, show=True):
        self.software_window = self.get_software_window()
        self.chat_window = self.get_chat_window()
        self.machine = self.get_model()
        self.out_arrow = self.get_out_arrow(self.machine)
        self.code = self.get_code_panel()
        self.title_group = self.get_title()
        self.user_bubble = self.get_user_bubble()
        if show:
            self.add(
                self.title_group,
                self.software_window, self.chat_window,
                self.machine, self.out_arrow, self.code,
                self.user_bubble,
            )

    # Animations of one pass through the loop

    def feed_model(self, source, run_time=1.2, line_index="default"):
        """A copy of the text flies into the model, whose layers light up."""
        if line_index == "default":
            line_index = self.model_line
        copy = source.copy()
        anims = [
            Transform(copy, VGroup(VectorizedPoint(self.machine[0].get_top())), lag_ratio=0.01, remover=True, path_arc=30 * DEGREES),
            self.block_flash(),
        ]
        if line_index is not None:
            anims.insert(0, self.code.highlight_line(line_index))
        self.play(LaggedStart(*anims, lag_ratio=0.4), run_time=run_time)

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

    def show_distribution(self, words, probs, pct_labels=None, max_len=1.5, run_time=0.8):
        chart = bar_chart(words, probs, max_len=max_len, pct_labels=pct_labels)
        chart.move_to(self.out_arrow.get_end() + 0.35 * RIGHT, LEFT)
        # Bars, not labels, start right of the arrow
        chart.shift((self.out_arrow.get_end()[0] + 1.3 - chart.rows[0][1].get_left()[0]) * RIGHT)
        chart.match_y(self.machine[0])
        self.play(
            LaggedStart(
                (FadeInFromPoint(row, self.out_arrow.get_end()) for row in chart),
                lag_ratio=0.04,
            ),
            run_time=run_time,
        )
        return chart

    def pick(self, chart, index, run_time=1.0, line_index="default", seed=0):
        """Highlight hops around the bars, weighted by size, and lands on index."""
        if line_index == "default":
            line_index = self.pick_line
        rows = chart.rows
        widths = np.array([row[1].get_width() for row in rows])
        dist = widths / widths.sum()
        rect = SurroundingRectangle(rows[index], buff=0.04)
        rect.set_stroke(WARN, 2).set_fill(WARN, 0.15)

        def update(mob, alpha):
            np.random.seed(seed + int(8 * alpha))
            i = index if alpha > 0.85 else np.random.choice(len(rows), p=dist)
            mob.surround(rows[i], buff=0.04)

        anims = [UpdateFromAlphaFunc(rect, update)]
        if line_index is not None:
            anims.append(self.code.highlight_line(line_index))
        self.play(*anims, run_time=run_time)
        chart.add(rect)
        return rect

    def append_word(self, chart, index, flow, bubble, word, run_time=0.8, line_index="default"):
        """The chosen word moves from the chart into the chat."""
        if line_index == "default":
            line_index = self.append_line
        target = flow.next_word(word)
        source = chart.rows[index][0].copy()
        anims = [
            FadeTransform(source, target),
            UpdateFromFunc(bubble.bg, lambda m: m.set_opacity(1)),
        ]
        if line_index is not None:
            anims.append(self.code.highlight_line(line_index))
        self.play(*anims, run_time=run_time)
        self.remove(source)
        flow.add(target)
        bubble.refresh()
        self.add(bubble)
        self.play(FadeOut(chart), run_time=0.3)
        return target

    def quick_word(self, flow, bubble, word, run_time=0.35, color=INK):
        """A full loop pass in a fraction of a second: pulse, word out."""
        target = flow.next_word(word, color)
        bubble.bg.set_opacity(1)
        start = VectorizedPoint(self.out_arrow.get_end())
        self.play(
            self.block_flash(run_time=run_time),
            FadeTransform(start, target),
            run_time=run_time,
        )
        self.remove(start)
        flow.add(target)
        bubble.refresh()
        self.add(bubble)
        return target

    def randomize_dials(self, run_time=2, lag_factor=0.5):
        dials = self.dials
        return LaggedStart(
            (dial.animate_set_value(dial.get_random_value()) for dial in dials),
            lag_ratio=lag_factor / len(dials),
            run_time=run_time,
        )
