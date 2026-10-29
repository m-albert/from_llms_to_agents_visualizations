"""
Shared pieces for the "from next-word prediction to agentic AI" scenes:
software and chat windows, the 3b1b model drawing, the software loop shown
as a loop through the model (input panel and arrows), special-word chips,
bar charts and chat bubbles.

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
    def __init__(self, top_left, width, font_size=24, line_height=None, **kwargs):
        super().__init__(**kwargs)
        self.top_left = np.array(top_left)
        self.max_width = width
        self.font_size = font_size
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
            full = text("A" + stripped, font_size=self.font_size, color=color)
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


# The scene base class

class AgenticScene(BuildStills, PredictTheNextWord):
    """
    Layout shared by the four stage scenes. The software window on the left
    is a loop around the model: the input text (bottom) goes up into the
    model, the next word comes out, and the software adds it back to the
    input (and shows it in the chat on the right) until its stop rule says
    otherwise.
    """
    machine_name = "Large\nLanguage\nModel"
    stage_number = 1
    stage_title = ""
    stage_subtitle = ""
    question = "What do recent papers say about microplastics and health?"
    # Stop rule of the software: after 10 words ("count") or at STOP ("stop")
    loop_rule = "count"
    # Stages 1 and 2 show the next-word probabilities and the pick
    show_bars = False
    trained = True
    window_left, window_right = -6.85, 1.35
    chat_left, chat_right = 1.6, 6.9
    window_top, window_bottom = 2.75, -3.4
    model_center = (-5.0, 0.8)
    input_top = -0.95
    answer_font_size = 26
    input_font_size = 22

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

    def get_software_window(self):
        return self.get_window(self.window_left, self.window_right, "Software")

    def get_chat_window(self):
        return self.get_window(self.chat_left, self.chat_right, "Chat")

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
        machine.set_height(2.0)
        machine.move_to([*self.model_center, 0])
        self.blocks = blocks
        self.dials = last_dials
        return machine

    def get_weights_label(self, string):
        label = text(string, font_size=22, color=MUTED)
        label.next_to(self.machine[0], UP, buff=0.12)
        return label

    def get_out_arrow(self, machine):
        arrow = Arrow(
            machine[0].get_right() + 0.05 * RIGHT,
            machine[0].get_right() + 0.8 * RIGHT,
            buff=0, thickness=4,
        )
        arrow.set_fill(MUTED)
        return arrow

    def get_out_point(self):
        """Where the next word appears, right of the model."""
        return self.out_arrow.get_end() + 0.8 * RIGHT

    def get_input_panel(self):
        left, right = self.window_left + 0.15, self.window_right - 0.15
        bottom = self.window_bottom + 0.15
        bg = RoundedRectangle(right - left, self.input_top - bottom, corner_radius=0.1)
        bg.set_fill(PANEL_FILL, 1).set_stroke(width=0)
        bg.move_to([left, self.input_top, 0], UL)
        title = text("Input to the model", font_size=17, color=MUTED, weight=BOLD)
        title.move_to(bg.get_corner(UL) + [0.2, -0.2, 0], UL)
        self.input_flow = FlowText(
            [left + 0.2, title.get_bottom()[1] - 0.12, 0], right - left - 0.4,
            font_size=self.input_font_size,
        )
        panel = VGroup(bg, title)
        panel.bg = bg
        panel.title = title
        return panel

    def get_in_arrow(self):
        x = self.machine[0].get_x()
        return flow_arrow([x, self.input_top, 0], [x, self.machine[0].get_bottom()[1] - 0.03, 0])

    def get_return_arrow(self):
        """Output word back into the input: '+ word'."""
        x = self.get_out_point()[0]
        top = -0.3 if self.show_bars else self.get_out_point()[1] - 0.35
        arrow = flow_arrow([x, top, 0], [x, self.input_top, 0])
        label = text("+ word", font_size=18, color=ACCENT)
        label.move_to([x - 0.15, -0.3, 0], RIGHT)
        return VGroup(arrow, label)

    def get_rule_label(self):
        if self.loop_rule == "count":
            self.counter = mono("0/10", font_size=17, color=MUTED)
            parts = VGroup(text("repeat 10 times", font_size=18, color=MUTED), self.counter)
        else:
            parts = VGroup(text("repeat until", font_size=18, color=MUTED), chip("STOP", font_size=14))
        parts.arrange(RIGHT, buff=0.12)
        parts.move_to([self.get_out_point()[0] - 0.15, -0.65, 0], RIGHT)
        return parts

    def get_counter(self, n, total=10):
        return mono(f"{n}/{total}", font_size=17, color=MUTED).move_to(self.counter)

    def update_counter(self, n, animate=True):
        new = self.get_counter(n)
        if animate:
            self.play(Transform(self.counter, new), run_time=0.3)
        else:
            self.counter.become(new)

    def get_user_bubble(self, string=None, font_size=None):
        font_size = font_size or self.answer_font_size
        string = string or self.question
        icon = person_icon(0.42)
        icon.move_to([self.chat_right - 0.4, 0, 0])
        flow = FlowText(ORIGIN, 3.9, font_size=font_size)
        flow.add_words(string.split(" "))
        flow.move_to([self.chat_right - 0.85, window_content_top(self.chat_window, 0.35), 0], UR)
        flow.top_left = np.array([flow.get_left()[0], flow.get_top()[1], 0])
        bubble = ChatBubble(flow, USER_FILL)
        icon.match_y(bubble.bg)
        return VGroup(bubble, icon)

    def get_answer(self, top_y, width=4.1, fill=PANEL_FILL):
        """Empty assistant bubble with the robot icon; returns (group, flow, bubble)."""
        icon = robot_icon(0.4)
        icon.move_to([self.chat_left + 0.35, top_y - 0.2, 0])
        flow = FlowText([self.chat_left + 0.85, top_y - 0.1, 0], width, font_size=self.answer_font_size)
        bubble = ChatBubble(flow, fill)
        bubble.bg.set_opacity(0)
        return VGroup(icon, bubble), flow, bubble

    def setup_stage(self):
        self.software_window = self.get_software_window()
        self.chat_window = self.get_chat_window()
        self.machine = self.get_model()
        self.out_arrow = self.get_out_arrow(self.machine)
        self.input_panel = self.get_input_panel()
        self.in_arrow = self.get_in_arrow()
        self.return_arrow = self.get_return_arrow()
        self.rule_label = self.get_rule_label()
        self.loop_parts = VGroup(self.in_arrow, self.out_arrow, self.return_arrow, self.rule_label)
        self.title_group = self.get_title()
        self.user_bubble = self.get_user_bubble()

    def build_loop(self, run_time=2.5):
        """Input panel, then the arrows around the model."""
        return LaggedStart(
            FadeIn(self.input_panel),
            ShowCreation(self.in_arrow, lag_ratio=0),
            GrowArrow(self.out_arrow),
            ShowCreation(self.return_arrow[0], lag_ratio=0),
            FadeIn(self.return_arrow[1]),
            FadeIn(self.rule_label),
            lag_ratio=0.3,
            run_time=run_time,
        )

    def send_question(self, run_time=1.5):
        """The chat message is copied into the (so far empty) input."""
        targets = self.input_flow.add_words(self.question.split(" "))
        self.play(
            TransformFromCopy(self.user_bubble[0].flow, targets, path_arc=30 * DEGREES, lag_ratio=0.01),
            run_time=run_time,
        )

    # One pass through the loop

    def pulse(self, mob, color=BAR_COLOR, **kwargs):
        return mob.animate.set_color(color).set_anim_args(rate_func=there_and_back, **kwargs)

    def feed_model(self, run_time=1.2):
        """A copy of the input flies up into the model, whose layers light up."""
        point = VGroup(VectorizedPoint(self.machine[0].get_bottom()))
        self.play(
            LaggedStart(
                self.pulse(self.in_arrow),
                Transform(self.input_flow.copy(), point, lag_ratio=0.002, remover=True),
                self.block_flash(),
                lag_ratio=0.3,
            ),
            run_time=run_time,
        )

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

    def show_distribution(self, words, probs, pct_labels=None, max_len=1.5, n_main=None, run_time=0.8):
        chart = bar_chart(words, probs, max_len=max_len, pct_labels=pct_labels, n_main=n_main, font_size=22)
        # Bars, not labels, start a fixed distance right of the arrow
        chart.shift((self.out_arrow.get_end()[0] + 1.3 - chart.rows[0][1].get_left()[0]) * RIGHT)
        chart.shift((window_content_top(self.software_window, 0.15) - chart.get_top()[1]) * UP)
        self.play(
            LaggedStart(
                (FadeInFromPoint(row, self.out_arrow.get_end()) for row in chart),
                lag_ratio=0.04,
            ),
            run_time=run_time,
        )
        return chart

    def pick(self, chart, index, run_time=1.0, seed=0):
        """Highlight hops around the bars, weighted by size, and lands on index."""
        rows = chart.rows
        widths = np.array([row[1].get_width() for row in rows])
        dist = widths / widths.sum()
        rect = SurroundingRectangle(rows[index], buff=0.04)
        rect.set_stroke(WARN, 2).set_fill(WARN, 0.15)

        def update(mob, alpha):
            np.random.seed(seed + int(8 * alpha))
            i = index if alpha > 0.85 else np.random.choice(len(rows), p=dist)
            mob.surround(rows[i], buff=0.04)

        self.play(UpdateFromAlphaFunc(rect, update), run_time=run_time)
        chart.add(rect)
        return rect

    def add_targets(self, word, chat_flow, color=INK):
        """The word's places at the end of the chat answer and of the input."""
        chat_target = chat_flow.next_word(word, color) if chat_flow is not None else None
        input_target = self.input_flow.next_word(word, color)
        return chat_target, input_target

    def place_word(self, source, chat_flow, bubble, word, color=INK, run_time=0.8, extra_anims=()):
        """source moves into the input (down the '+ word' arrow) and into the chat."""
        chat_target, input_target = self.add_targets(word, chat_flow, color)
        anims = [
            FadeTransform(source.copy(), input_target),
            self.pulse(self.return_arrow[0]),
            *extra_anims,
        ]
        if chat_target is not None:
            anims += [
                FadeTransform(source, chat_target),
                UpdateFromFunc(bubble.bg, lambda m: m.set_opacity(1)),
            ]
        else:
            anims.append(FadeOut(source))
        self.play(*anims, run_time=run_time)
        self.input_flow.add(input_target)
        if chat_target is not None:
            chat_flow.add(chat_target)
            bubble.refresh()
            self.add(bubble)

    def append_word(self, chart, index, chat_flow, bubble, word, run_time=0.8):
        """The picked word moves from the chart into the input and the chat."""
        source = chart.rows[index][0].copy()
        self.place_word(source, chat_flow, bubble, word, run_time=run_time)
        self.play(FadeOut(chart), run_time=0.3)

    def emit_word(self, word, chat_flow, bubble, run_time=0.35, color=INK, slow=False):
        """
        One pass without bars: the model lights up, the next word appears to
        its right, and goes into the input and the chat. slow=True shows
        the steps one at a time.
        """
        mob = word_mob(word, font_size=self.answer_font_size, color=color)
        mob.move_to(self.get_out_point())
        if slow:
            self.feed_model(run_time=1.0)
            self.play(FadeInFromPoint(mob, self.out_arrow.get_end()), run_time=0.5)
            self.place_word(mob, chat_flow, bubble, word, color, run_time=0.7)
            return
        chat_target, input_target = self.add_targets(word, chat_flow, color)
        start = self.out_arrow.get_end()
        anims = [
            self.pulse(self.in_arrow),
            self.block_flash(run_time=run_time),
            FadeTransform(VectorizedPoint(start), input_target),
            self.pulse(self.return_arrow[0]),
        ]
        if chat_target is not None:
            anims.append(FadeTransform(VectorizedPoint(start), chat_target))
            bubble.bg.set_opacity(1)
        self.play(*anims, run_time=run_time)
        self.input_flow.add(input_target)
        if chat_target is not None:
            chat_flow.add(chat_target)
            bubble.refresh()
            self.add(bubble)

    def flash_rule(self):
        rect = SurroundingRectangle(self.rule_label, buff=0.08).set_stroke(WARN, 2)
        self.play(ShowCreation(rect))
        return rect

    def randomize_dials(self, run_time=2, lag_factor=0.5):
        dials = self.dials
        return LaggedStart(
            (dial.animate_set_value(dial.get_random_value()) for dial in dials),
            lag_ratio=lag_factor / len(dials),
            run_time=run_time,
        )

    # System prompt: joined with the chat on its way into the input

    system_prompt = [("You are a helpful assistant. Answer clearly and concisely.", INK)]
    system_pill_label = "System prompt"

    def get_system_prompt_card(self, width=5.2, font_size=19):
        """The developer's instructions, waiting in the (empty) input panel."""
        title = text("System prompt", font_size=font_size + 1, color=MUTED, weight=BOLD)
        flow = FlowText(ORIGIN, width - 0.4, font_size=font_size)
        segments = VGroup()
        for string, color in self.system_prompt:
            segments.add(flow.add_words(string.split(" "), color=color))
            flow.line_break()
        note = text("Set by the developer, not shown in the chat", font_size=font_size - 4, color=MUTED, slant=ITALIC)
        title.move_to(ORIGIN, UL)
        flow.shift(title.get_corner(DL) + 0.12 * DOWN - flow.top_left)
        note.next_to(flow, DOWN, buff=0.15, aligned_edge=LEFT)
        content = VGroup(title, flow, note)
        bg = SurroundingRectangle(content, buff=0.18).round_corners(0.1)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1.5)
        card = VGroup(bg, content)
        card.move_to(self.input_panel.bg).shift(0.15 * DOWN)
        card.flow = flow
        card.segments = segments
        card.frame = VGroup(bg, title, note)
        return card

    def get_system_pill(self, font_size=16):
        icon = doc_icon(0.24)
        label = text(self.system_pill_label, font_size=font_size, color=MUTED)
        content = VGroup(icon, label).arrange(RIGHT, buff=0.1)
        bg = SurroundingRectangle(content, buff=0.06).round_corners(0.06)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1)
        return VGroup(bg, content)

    def join_system_prompt(self, card):
        """
        The chat message travels into the input; the software puts the
        system prompt in front of it and adds the roles and STOPs.
        """
        flow = self.input_flow
        pill = flow.add_word(self.get_system_pill())
        flow.line_break()
        user_label = flow.add_word("User:", color=MUTED)
        user_words = flow.add_words(self.question.split(" "))
        user_stop = flow.add_word("STOP")
        flow.line_break()
        assistant_label = flow.add_word("Assistant:", color=MUTED)
        note = text("System prompt + chat, joined by the software", font_size=15, color=MUTED, slant=ITALIC)
        note.next_to(self.input_panel.title, RIGHT, buff=0.3, aligned_edge=DOWN)

        self.play(
            LaggedStart(
                FadeTransform(card, pill),
                TransformFromCopy(self.user_bubble[0].flow, user_words, path_arc=30 * DEGREES, lag_ratio=0.01),
                lag_ratio=0.35,
            ),
            FadeIn(note),
            run_time=2.2,
        )
        self.play(
            LaggedStartMap(FadeIn, VGroup(user_label, user_stop, assistant_label), lag_ratio=0.4),
            run_time=1.2,
        )
        self.wait()
        self.play(FadeOut(note))
