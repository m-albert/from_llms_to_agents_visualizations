from manim_imports_ext import *
from manimlib.mobject.svg.svg_mobject import VMobjectFromSVGPath
from manimlib.utils.svg_export import _get_path_data
import svgelements as se
from scenes.agentic_common import *


STEP_FILL = "#EDF2FA"
STEP_STROKE = "#B9CBE6"
TITLE_BAR_FILL = "#F1F2F5"
CHAT_STROKE = "#D3D8E1"
TOOL_FILL = "#DDF1EE"

# One unit of the llm_to_agentic_ai.svg grid, whose icons are ported below
UNIT = FRAME_WIDTH / 1980


def export_svg(mobjects, filename, pixel_width=1920, pixel_height=1080, background=TRUE_WHITE):
    """
    Like manimlib.utils.svg_export.vmobject_to_svg, plus: even-odd fill (keeps
    holes in letters open), strokes drawn behind fills for back-strokes, and
    a background rectangle.
    """
    fw, fh = FRAME_WIDTH, FRAME_HEIGHT
    stroke_scale = pixel_width / fw
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="{-fw / 2} {-fh / 2} {fw} {fh}" width="{pixel_width}" height="{pixel_height}">',
        f'  <rect x="{-fw / 2}" y="{-fh / 2}" width="{fw}" height="{fh}" fill="{background}"/>',
    ]
    for mob in it.chain(*(m.family_members_with_points() for m in mobjects)):
        if not isinstance(mob, VMobject):
            continue
        path_data = _get_path_data(mob)
        if not path_data:
            continue
        fill_opacity = mob.get_fill_opacity()
        stroke_opacity = mob.get_stroke_opacity()
        stroke_width = mob.get_stroke_width() / stroke_scale
        if fill_opacity == 0 and (stroke_opacity == 0 or stroke_width == 0):
            continue
        attrs = [f'd="{path_data}"', 'fill-rule="evenodd"']
        attrs.append(f'fill="{mob.get_fill_color() if fill_opacity > 0 else "none"}"')
        if 0 < fill_opacity < 1:
            attrs.append(f'fill-opacity="{fill_opacity:.4g}"')
        if stroke_opacity > 0 and stroke_width > 0:
            attrs.append(f'stroke="{mob.get_stroke_color()}" stroke-width="{stroke_width:.4g}"')
            attrs.append('stroke-linejoin="round" stroke-linecap="round"')
            if stroke_opacity < 1:
                attrs.append(f'stroke-opacity="{stroke_opacity:.4g}"')
            if getattr(mob, "stroke_behind", False):
                attrs.append('paint-order="stroke"')
        lines.append(f'  <path {" ".join(attrs)}/>')
    lines.append('</svg>')
    Path(filename).write_text("\n".join(lines))


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
    letter = text(string, font_size=font_size, color=color, weight=BOLD)
    return letter.move_to([x * UNIT, -y * UNIT, 0])


def get_icon(name, color=ACCENT, height=None, width=2.0):
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
    else:
        raise ValueError(name)
    icon = VGroup(*parts)
    if height is not None:
        icon.set_height(height)
    return icon


def on_baseline(string, x, y, side=LEFT, **kwargs):
    """Text whose baseline is at y, whether or not it has descenders (like FlowText's words)."""
    full = text("A" + string, **kwargs)
    full.shift((y - full[0].get_bottom()[1]) * UP)
    # Slice after moving: a slice caches its bounding box
    mob = full[1:]
    return mob.shift((x - mob.get_edge_center(side)[0]) * RIGHT)


def open_arrow(start, end, color, width=2.0, head=0.05):
    """Thin line with an open arrowhead."""
    start, end = np.array(start, dtype=float), np.array(end, dtype=float)
    direction = normalize(end - start)
    side = rotate_vector(direction, PI / 2)
    shaft = Line(start, end).set_stroke(color, width)
    barbs = Polyline(end - head * (direction - side), end, end - head * (direction + side))
    return VGroup(shaft, barbs.set_stroke(color, width))


def dashed_round_rect(width, height, radius, color, stroke_width=1.0, dash=0.045, gap=0.032):
    """Evenly dashed rounded rectangle, also around the corners (centered at the origin)."""
    w, h, r = width / 2, height / 2, radius
    # Clockwise from the top left, as (start, end) or (center, start angle)
    edges = [
        ((-w + r, h), (w - r, h)), ((w - r, h - r), PI / 2),
        ((w, h - r), (w, -h + r)), ((w - r, -h + r), 0.0),
        ((w - r, -h), (-w + r, -h)), ((-w + r, -h + r), -PI / 2),
        ((-w, -h + r), (-w, h - r)), ((-w + r, h - r), PI),
    ]
    arc_length = r * PI / 2
    lengths = [
        arc_length if isinstance(end, float) else get_norm(np.subtract(end, start))
        for start, end in edges
    ]
    total = sum(lengths)

    def point_at(s):
        s = s % total
        for (start, end), length in zip(edges, lengths):
            if s <= length:
                if isinstance(end, float):
                    angle = end - s / r
                    return np.array([start[0] + r * np.cos(angle), start[1] + r * np.sin(angle), 0])
                x, y = interpolate(np.array(start, dtype=float), np.array(end, dtype=float), s / length)
                return np.array([x, y, 0])
            s -= length
        return np.array([*edges[0][0], 0])

    n_dashes = int(total / (dash + gap))
    period = total / n_dashes
    dashes = VGroup(
        Polyline(*(point_at(n * period + a * dash) for a in [0, 0.5, 1]))
        for n in range(n_dashes)
    )
    return dashes.set_stroke(color, stroke_width)


class AgenticOverview(AgenticScene):
    """
    The five stages side by side (the llm_to_agentic_ai schematic), built up
    stage by stage in the style of the manim scenes. The last frame is also
    written out as an SVG next to the video.

    Horizontally this is the schematic's grid: columns of 340 units with
    gutters of 40, which is what leaves room for the chevrons between them.
    """
    col_xs = [-5.46, -2.73, 0.0, 2.73, 5.46]
    col_width = 2.44
    row_label_x = -6.9
    steps_y = 3.16
    step_height = 1.24
    # Baselines
    year_y, title_y, subtitle_y = 2.29, 2.0, 1.76
    model_y = 0.79
    window_height = 1.66
    bar_height = 0.15
    narrow_window_width = 1.08
    # Left part of the wide windows, with the model; the panels are to its right
    wide_left_width = 0.88
    panel_buff = 0.06
    caption_y = -0.28
    chat_top, chat_bottom = -0.42, -3.27
    warning_y = -3.59
    chat_font_size = 12
    chat_line_height = 0.185
    panel_font_size = 10
    panel_line_height = 0.145
    bubble_left = 0.33  # from the left of the chat
    bubble_width = 2.02
    stages = [
        dict(
            year="2017", year_note="Transformer architecture",
            title="Untrained model", subtitle="Random output: nothing learned yet",
            trained=False, software=["Generate", "10 words"], caption="Random weights",
            answer="orbit lamp the seven glass of whenever banana north quietly",
            note="10 random words",
        ),
        dict(
            year="2018–2020", year_note="GPT-1 to GPT-3",
            title="Pre-trained base model", subtitle="Completes text, not yet an assistant",
            trained=True, software=["Generate", "10 words"], caption="Learned language patterns",
            answer="…and in seafood? What do recent papers say about PFAS",
            note="Continues from input prompt",
        ),
        dict(
            year="2022", year_note="ChatGPT",
            title="AI assistant", subtitle="Helpful answers, but may hallucinate",
            trained=True, software=["Generate until", "STOP"], caption="+ Assistant behavior",
            panel="assistant",
            answer="Studies suggest microplastics may be linked to inflammation.\nA landmark study proved direct harm in humans. STOP",
            claim="A landmark study proved direct harm in humans.",
            warning=["Plausible, but from memory", "and potentially hallucinated"],
        ),
        dict(
            year="2024", year_note="o1, DeepSeek-R1",
            title="Reasoning model", subtitle="Thinks first, but still no sources",
            trained=True, software=["Generate until", "STOP"], caption="+ Thinking, marked by special words",
            panel="split",
            thought="Harm in humans proven? Not yet → don’t overclaim.",
            answer="ANSWER Microplastics are found in human tissue, but harm is still unclear. STOP",
            warning=["More careful, but still", "answers from memory"],
        ),
        dict(
            year="2024–today", year_note="tool use & agents",
            title="Tool-using agent", subtitle="Can retrieve and act; needs oversight",
            trained=True, software=["Generate until", "STOP"], caption="+ Tools, called by a special word",
            panel="tools",
            tools=[("web", "Search web"), ("folder", "Read files"), ("code", "Execute code")],
            thought="Need sources first.",
            tool_call=("web", "Search web", "“microplastics health publication”"),
            results=["Paper 1: Microplastics in hu…", "Paper 2: The effects of micro…"],
            answer=(
                "ANSWER Microplastics are found in human blood and tissue (Paper\u00a01). "
                "Whether they harm health is not yet proven\n(Paper\u00a02). STOP"
            ),
            warning=["Less likely to hallucinate,", "but still possible"],
        ),
    ]
    assistant_prompt = "“What follows is a conver- sation between a human and a helpful, knowledgeable and kind assistant…”"
    short_prompt = "“What follows is a conver- sation between a human…”"
    tool_prompt = "“What follows is a conver…\nThe assistant can use these tools by writing\nTOOL + tool + <input>:"
    steps = [
        dict(title="Pre-training", subtitle="Learn by predicting the next word",
             items=[dict(icon="books", label="Books"), dict(icon="web", label="Web"),
                    dict(icon="code", label="Code"), dict(icon="papers", label="Papers")]),
        dict(title="Post-training", subtitle="Answer helpfully, then stop",
             items=[dict(icon="examples", label="Examples"), dict(icon="feedback", label="Feedback"),
                    dict(chips=["STOP"], prefix="e.g.", label="Special words")]),
        dict(title="Reasoning training", subtitle="Think privately, then answer",
             items=[dict(icon="problems", label="Problems"), dict(icon="rewards", label="Rewards"),
                    dict(chips=["THINK", "ANSWER"], label="Special words")]),
        dict(title="Tools + agent loop", subtitle="Run the model in a loop with tools",
             items=None),
    ]
    export_name = "AgenticOverview.svg"

    def construct(self):
        columns = [self.get_column(n, stage) for n, stage in enumerate(self.stages)]
        step_cards = [self.get_step_card(n, step) for n, step in enumerate(self.steps)]
        row_labels = self.get_row_labels()

        # Stage 1
        self.play(FadeIn(row_labels["MODEL"]), FadeIn(row_labels["CHAT"]))
        self.play(LaggedStartMap(FadeIn, columns[0].header, shift=0.1 * DOWN, lag_ratio=0.2))
        self.play(FadeIn(columns[0].model))
        self.play(FadeIn(columns[0].chat_window), FadeIn(columns[0].question))
        self.play(FadeIn(columns[0].answer, lag_ratio=0.05))
        self.wait()

        # Each step leads to the next stage
        self.play(FadeIn(row_labels["STEPS"]))
        for n in range(1, len(self.stages)):
            card = step_cards[n - 1]
            self.play(FadeIn(card.card, 0.2 * DOWN))
            self.play(ShowCreation(card.connector), FadeIn(card.chevron, scale=0.5))
            self.play(
                LaggedStartMap(FadeIn, columns[n].header, shift=0.1 * DOWN, lag_ratio=0.2),
                TransformFromCopy(columns[n - 1].model, columns[n].model),
            )
            if columns[n].panels is not None:
                self.play(FadeIn(columns[n].panels, lag_ratio=0.1))
            self.play(FadeIn(columns[n].chat_window), FadeIn(columns[n].question))
            self.play(FadeIn(columns[n].answer, lag_ratio=0.05))
            if columns[n].warning is not None:
                self.play(FadeIn(columns[n].warning, 0.1 * UP))
            self.wait()
        self.wait(2)

        if self.file_writer.write_to_movie:
            export_svg(self.mobjects, Path(self.file_writer.output_directory, self.export_name))

    def get_row_labels(self):
        chat_y = (self.chat_top + self.chat_bottom) / 2
        labels = {}
        for name, y, color in [
            ("STEPS", self.steps_y, ACCENT),
            ("MODEL", self.model_y, FRAME_GREY),
            ("CHAT", chat_y, FRAME_GREY),
        ]:
            label = text(name, font_size=11, color=color, weight=BOLD).rotate(PI / 2)
            labels[name] = label.move_to([self.row_label_x, y, 0])
        return labels

    # Columns

    def get_column(self, n, stage):
        x = self.col_xs[n]
        left = x - self.col_width / 2
        column = VGroup()

        # Header: year, number + title, subtitle
        year_number = on_baseline(f"≈ {stage['year']}", left, self.year_y, font_size=12, color=ACCENT, weight=BOLD)
        year_note = on_baseline(
            f"· {stage['year_note']}", year_number.get_right()[0] + 0.06, self.year_y,
            font_size=12, color=MUTED,
        )
        year = VGroup(year_number, year_note)
        number = VGroup(
            Circle(radius=0.11).set_fill(ACCENT, 1).set_stroke(width=0),
            text(str(n + 1), font_size=13, color=TRUE_WHITE, weight=BOLD),
        )
        number[1].move_to(number[0])
        number.move_to([left + 0.11, self.title_y + 0.055, 0])
        title = on_baseline(stage["title"], left + 0.3, self.title_y, font_size=17, weight=BOLD)
        subtitle = on_baseline(stage["subtitle"], left, self.subtitle_y, font_size=13, color=MUTED)
        column.header = VGroup(year, VGroup(number, title), subtitle)

        # Model in its software window, plus caption and panels
        column.model, column.panels = self.get_model_window(n, stage, x)

        # Chat
        chat_window = RoundedRectangle(self.col_width, self.chat_top - self.chat_bottom, corner_radius=0.11)
        chat_window.set_fill(TRUE_WHITE, 1).set_stroke(CHAT_STROKE, 1.5)
        chat_window.move_to([x, (self.chat_top + self.chat_bottom) / 2, 0])
        column.chat_window = chat_window
        column.question = self.get_question(x)
        column.answer, column.warning = self.get_answer_parts(stage, x, column.question)
        return column

    def get_software_window(self, width):
        """App window with a tinted title bar, window dots and a </> mark."""
        height = self.window_height
        bar = self.bar_height
        radius = 0.07
        body = RoundedRectangle(width, height, corner_radius=radius)
        body.set_fill(TRUE_WHITE, 1).set_stroke(INK, 1.5)
        left, right, top = -width / 2, width / 2, height / 2
        points = [
            [left, top - bar, 0], [left, top - radius, 0],
            *([left + radius * (1 - np.cos(a)), top - radius * (1 - np.sin(a)), 0] for a in np.linspace(0, PI / 2, 8)),
            *([right - radius * (1 - np.sin(a)), top - radius * (1 - np.cos(a)), 0] for a in np.linspace(0, PI / 2, 8)),
            [right, top - bar, 0],
        ]
        tint = Polygon(*points).set_fill(TITLE_BAR_FILL, 1).set_stroke(width=0)
        bar_line = Line([left, top - bar, 0], [right, top - bar, 0]).set_stroke(INK, 1)
        outline = body.copy().set_fill(opacity=0)
        dots = VGroup(Dot(radius=0.02) for _ in range(3)).arrange(RIGHT, buff=0.03)
        dots.set_fill(FRAME_GREY, 1).set_stroke(width=0)
        dots.move_to([left + 0.07, top - bar / 2, 0], LEFT)
        code_mark = get_icon("code", color=FRAME_GREY, width=1.0)[1:]
        code_mark.set_height(0.07).move_to([right - 0.08, top - bar / 2, 0], RIGHT)
        return VGroup(body, tint, bar_line, outline, dots, code_mark)

    def get_llm(self, trained):
        """
        The model drawing of the animations (a stack of layers, with dials on
        the front one), but drawn flat so that all its edges are straight.
        The dials are the same in every trained stage: it's one model.
        """
        width, height = 0.56, 0.37
        offset = 0.012 * LEFT + 0.01 * UP
        blocks = VGroup(Rectangle(width, height) for _ in range(10))
        for n, block in enumerate(blocks):
            block.shift((len(blocks) - 1 - n) * offset)
        blocks.set_fill(TRAINED_FILL if trained else UNTRAINED_FILL, 1)
        blocks.set_stroke(TRUE_WHITE, 0.5)
        if trained and hasattr(self, "trained_dials"):
            dials = self.trained_dials.copy()
        else:
            flat_dials, dials = self.get_machine_dials(blocks[-1:])
            dials.set_stroke(width=0.4, opacity=0.5)
            if trained:
                self.trained_dials = dials.copy()
        return VGroup(blocks, dials.move_to(blocks[-1]))

    def get_model_window(self, n, stage, x):
        panel = stage.get("panel")
        width = self.col_width if panel else self.narrow_window_width
        window = self.get_software_window(width)
        window.move_to([x, self.model_y, 0])
        content_top = self.model_y + self.window_height / 2 - self.bar_height
        content_y = self.model_y - self.bar_height / 2
        model_x = x - width / 2 + self.wide_left_width / 2 + 0.01 if panel else x

        llm = self.get_llm(stage["trained"])
        software = self.get_software_label(stage["software"])
        extras = VGroup()
        if panel == "tools":
            # More to fit under the model
            programs = self.get_programs(stage["tools"])
            left_part = VGroup(llm, software, programs).arrange(DOWN, buff=0.1)
            left_part.move_to([model_x, content_y, 0])
            extras.add(programs)
        else:
            # At the same height in every window
            llm.move_to([model_x, content_y + 0.2, 0])
            software.next_to(llm, DOWN, buff=0.09)

        caption = on_baseline(stage["caption"], x, self.caption_y, side=ORIGIN, font_size=13, color=MUTED)
        group = VGroup(window, llm, software, caption)

        if panel:
            panel_left = x - width / 2 + self.wide_left_width
            panel_width = width - self.wide_left_width - self.panel_buff
            if panel == "assistant":
                content = self.get_prompt_panel(self.assistant_prompt, panel_left, panel_width)
                content.move_to([panel_left + panel_width / 2, content_y, 0])
                extras.add(content)
            elif panel == "split":
                prompt = self.get_prompt_panel(self.short_prompt, panel_left, panel_width)
                split = self.get_split_panel(panel_left, panel_width)
                content = VGroup(prompt, split).arrange(DOWN, buff=0.07)
                content.move_to([panel_left + panel_width / 2, content_y, 0])
                extras.add(content)
            else:
                content = self.get_tool_prompt_panel(stage["tools"], panel_left, panel_width)
                content.move_to([panel_left + panel_width / 2, content_y, 0])
                extras.add(content)
        return group, (extras if len(extras) > 0 else None)

    def get_panel(self, content, left, width, fill, stroke, dashed):
        """Background for a panel; content is placed at its top, against the left edge."""
        buff = 0.07
        content.move_to([left + buff, 0, 0], UL)
        height = content.get_height() + 2 * buff
        radius = 0.06
        bg = RoundedRectangle(width, height, corner_radius=radius)
        bg.move_to([left + width / 2, buff - height / 2, 0])
        if dashed:
            bg.set_fill(fill, 1).set_stroke(width=0)
            border = dashed_round_rect(width, height, radius, stroke).move_to(bg)
            return VGroup(bg, border, content)
        bg.set_fill(fill, 1).set_stroke(stroke, 1)
        return VGroup(bg, content)

    def get_panel_title(self, string, color):
        return text(string, font_size=8, color=color, weight=BOLD)

    def get_panel_flow(self, width):
        return FlowText(
            ORIGIN, width - 0.14, font_size=self.panel_font_size,
            line_height=self.panel_line_height, slant=ITALIC,
        )

    def get_prompt_panel(self, prompt, left, width):
        """The hidden text the software puts in front of every conversation."""
        flow = self.get_panel_flow(width)
        self.add_flow_words(flow, prompt.split(" "))
        title = self.get_panel_title("SYSTEM PROMPT", ACCENT)
        content = VGroup(title, flow).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        return self.get_panel(content, left, width, STEP_FILL, STEP_STROKE, dashed=True)

    def get_tool_prompt_panel(self, tools, left, width):
        """The system prompt also lists the tools and how to call them."""
        flow = self.get_panel_flow(width)
        self.add_flow_lines(flow, self.tool_prompt)
        rows = VGroup()
        for icon, name in tools:
            rows.add(VGroup(
                get_icon(icon, color=TOOL_COLOR, height=0.1, width=1.0),
                text(name, font_size=self.panel_font_size, color=TOOL_COLOR),
            ).arrange(RIGHT, buff=0.05))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        closing = text("…”", font_size=self.panel_font_size, color=TOOL_COLOR)
        closing.next_to(rows[-1], RIGHT, buff=0.06, aligned_edge=DOWN)
        title = self.get_panel_title("SYSTEM PROMPT", ACCENT)
        content = VGroup(title, flow, VGroup(rows, closing)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        return self.get_panel(content, left, width, STEP_FILL, STEP_STROKE, dashed=True)

    def get_split_panel(self, left, width):
        """How the software splits the output (not part of the system prompt)."""
        rows = VGroup(
            VGroup(chip(word, font_size=8), text(label, font_size=self.panel_font_size, color=color, slant=slant)).arrange(RIGHT, buff=0.05)
            for word, label, color, slant in [
                ("THINK", "→ Private thoughts", MUTED, ITALIC),
                ("ANSWER", "→ Answer", INK, NORMAL),
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        title = self.get_panel_title("SPLIT OUTPUT", MUTED)
        content = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        return self.get_panel(content, left, width, TRUE_WHITE, CHAT_STROKE, dashed=False)

    def get_programs(self, tools):
        """The same tools, as programs the software can run."""
        tiles = VGroup()
        for icon, name in tools:
            tile = RoundedRectangle(0.2, 0.2, corner_radius=0.04)
            tile.set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 1)
            glyph = get_icon(icon, color=TOOL_COLOR, height=0.12, width=1.0).move_to(tile)
            tiles.add(VGroup(tile, glyph))
        tiles.arrange(RIGHT, buff=0.045)
        label = self.get_panel_title("PROGRAMS", TOOL_COLOR)
        return VGroup(label, tiles).arrange(DOWN, buff=0.05)

    def get_software_label(self, lines):
        top = text(lines[0], font_size=11, color=MUTED)
        if lines[1] in SPECIAL_WORDS:
            bottom = chip(lines[1], font_size=9)
        else:
            bottom = text(lines[1], font_size=11, color=MUTED)
        return VGroup(top, bottom).arrange(DOWN, buff=0.05)

    def add_flow_words(self, flow, words, color=INK):
        """Words of running text; chips are lowered a bit, to the middle of the capitals."""
        mobs = flow.add_words(words, color=color)
        for word, mob in zip(words, mobs):
            if word in SPECIAL_WORDS:
                mob.shift(0.012 * DOWN)
        return mobs

    def add_flow_lines(self, flow, string):
        """Running text; a newline starts a new line."""
        for n, line in enumerate(string.split("\n")):
            if n > 0:
                flow.line_break()
            self.add_flow_words(flow, line.split(" "))

    def get_question(self, x):
        right = x + self.col_width / 2
        flow = FlowText(ORIGIN, 1.76, font_size=self.chat_font_size, line_height=self.chat_line_height)
        flow.add_words(self.question.replace(" and ", " & ").split(" "))
        bubble = self.get_bubble(flow, USER_FILL, flow.get_width() + 0.2)
        icon = get_icon("person", color=MUTED)
        group = VGroup(bubble, icon)
        bubble.move_to([right - 0.33, self.chat_top - 0.1, 0], UR)
        icon.move_to([right - 0.17, bubble.get_y(), 0])
        return group

    def get_bubble(self, flow, fill, width):
        """Bubble of a fixed width around a FlowText that starts at its top left."""
        flow_left, flow_top = flow.top_left[:2]
        height = flow_top - flow.get_bottom_y() + 0.11
        bg = RoundedRectangle(width, height, corner_radius=0.09)
        bg.set_fill(fill, 1).set_stroke(width=0)
        bg.move_to([flow_left - 0.1, flow_top + 0.05, 0], UL)
        return VGroup(bg, flow)

    def get_thought_box(self, stage, left, top, width):
        """Dashed box with the private thoughts (and, for the agent, the tool call and its results)."""
        buff = 0.08
        inner_width = width - 2 * buff
        flow = FlowText(
            [left + buff, top - 0.04, 0], inner_width, font_size=self.chat_font_size - 1,
            line_height=self.chat_line_height, slant=ITALIC,
        )
        self.add_flow_words(flow, ["THINK"])
        self.add_flow_words(flow, stage["thought"].split(" "), color=MUTED)
        content = VGroup(flow)
        bottom = flow.get_bottom_y()
        if "tool_call" in stage:
            icon, name, query = stage["tool_call"]
            row = VGroup(
                chip("TOOL", font_size=8),
                get_icon(icon, color=TOOL_COLOR, height=0.11, width=1.0),
                text(name, font_size=11, color=TOOL_COLOR),
            ).arrange(RIGHT, buff=0.05)
            query_mob = text(query, font_size=10, color=TOOL_COLOR, slant=ITALIC)
            call = VGroup(row, query_mob).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
            pill = RoundedRectangle(inner_width, call.get_height() + 0.1, corner_radius=0.06)
            pill.set_stroke(TOOL_COLOR, 1).set_fill(TOOL_FILL, 1)
            pill.move_to([left + buff, bottom - 0.02, 0], UL)
            call.move_to(pill.get_left() + 0.06 * RIGHT, LEFT)
            results = VGroup(text("↳ " + result, font_size=10, color=MUTED) for result in stage["results"])
            results.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
            results.next_to(pill, DOWN, buff=0.06, aligned_edge=LEFT).shift(0.04 * RIGHT)
            content.add(VGroup(pill, call), results)
            bottom = results.get_bottom()[1]
        height = top - bottom + buff - 0.02
        rect = RoundedRectangle(width, height, corner_radius=0.09)
        rect.set_fill(TRUE_WHITE, 1).set_stroke(width=0)
        rect.move_to([left, top, 0], UL)
        border = dashed_round_rect(width, height, 0.09, FRAME_GREY).move_to(rect)
        return VGroup(rect, border, content)

    def get_answer_parts(self, stage, x, question):
        left = x - self.col_width / 2
        top = question.get_bottom()[1] - 0.1
        icon = get_icon("robot")
        icon.move_to([left + 0.17, top - 0.09, 0])
        parts = VGroup(icon)
        content_left = left + self.bubble_left
        content_width = self.bubble_width

        if "thought" in stage:
            thought = self.get_thought_box(stage, content_left, top, content_width)
            parts.add(thought)
            top = thought.get_bottom()[1] - 0.07

        flow = FlowText(
            [content_left + 0.1, top - 0.05, 0], content_width - 0.18,
            font_size=self.chat_font_size, line_height=self.chat_line_height,
        )
        self.add_flow_lines(flow, stage["answer"])
        bubble = self.get_bubble(flow, PANEL_FILL, content_width)
        parts.add(bubble)

        if "claim" in stage:
            claim_words = flow[-len(stage["claim"].split(" ")) - 1:-1]
            highlights, underlines = self.get_claim_marks(claim_words)
            bubble.remove(flow)
            bubble.add(highlights, underlines, flow)

        if "note" in stage:
            note = text(stage["note"], font_size=12, color=MUTED, slant=ITALIC)
            note.next_to(bubble[0], DOWN, buff=0.11).align_to(flow, LEFT)
            parts.add(note)

        warning = None
        if "warning" in stage:
            warning = warning_label(stage["warning"], font_size=13)
            warning.move_to([x, self.warning_y, 0])
        return parts, warning

    def get_claim_marks(self, words):
        """One amber highlight per line of the claim, with a dotted line underneath."""
        lines = {}
        for word in words:
            lines.setdefault(round(word.get_bottom()[1] / self.chat_line_height), []).append(word)
        highlights = VGroup()
        underlines = VGroup()
        for line_words in lines.values():
            line = VGroup(*line_words)
            height = 0.155
            rect = Rectangle(line.get_width() + 0.05, height)
            rect.move_to(line.get_center() + 0.002 * DOWN)
            rect.round_corners(0.025).set_fill(WARN_FILL, 1).set_stroke(width=0)
            highlights.add(rect)
            y = rect.get_bottom()[1] + 0.008
            n_dots = int(line.get_width() / 0.035)
            underlines.add(*(
                Dot([line.get_left()[0] + (n + 0.5) * line.get_width() / n_dots, y, 0], radius=0.006)
                for n in range(n_dots)
            ))
        underlines.set_fill(WARN, 1).set_stroke(width=0)
        return highlights, underlines

    # Steps

    def get_step_card(self, n, step):
        x = (self.col_xs[n] + self.col_xs[n + 1]) / 2
        card_bg = RoundedRectangle(self.col_width, self.step_height, corner_radius=0.11)
        card_bg.set_fill(STEP_FILL, 1).set_stroke(STEP_STROKE, 1.5)
        card_bg.move_to([x, self.steps_y, 0])
        top, bottom = card_bg.get_top()[1], card_bg.get_bottom()[1]
        title = on_baseline(step["title"], x, top - 0.22, side=ORIGIN, font_size=16, color=ACCENT, weight=BOLD)
        subtitle = on_baseline(step["subtitle"], x, top - 0.4, side=ORIGIN, font_size=12, color=MUTED)
        content = VGroup(title, subtitle)
        if step["items"]:
            items, feeds = self.get_step_items(step["items"], x, top - 0.64, top - 0.95, bottom)
            content.add(items, feeds)
        else:
            content.add(self.get_mini_loop(x, top - 0.72))
        connector = Line(card_bg.get_bottom(), [x, self.model_y, 0]).set_stroke(ACCENT, 2)
        chevron = VGroup(
            Circle(radius=0.11).set_fill(ACCENT, 1).set_stroke(width=0),
            icon_part("M-3 -6L3 0L-3 6", stroke=TRUE_WHITE, width=2.2),
        )
        chevron.move_to([x, self.model_y, 0])
        result = VGroup(card_bg, content, connector, chevron)
        result.card = VGroup(card_bg, content)
        result.connector = connector
        result.chevron = chevron
        return result

    def get_step_items(self, items, x, icon_y, label_y, card_bottom):
        """Icon (or special words) above each label; thin lines lead from the labels to the connector."""
        labels = VGroup(on_baseline(item["label"], 0, label_y, font_size=12) for item in items)
        labels.arrange(RIGHT, buff=0.16, center=False, coor_mask=RIGHT)
        labels.set_x(x)
        result = VGroup()
        feeds = VGroup()
        for item, label in zip(items, labels):
            result.add(self.get_step_item(item).move_to([label.get_x(), icon_y, 0]), label)
            start = np.array([label.get_x(), label_y - 0.06, 0])
            end = np.array([x, card_bottom, 0])
            feeds.add(CubicBezier(
                start, start + 0.11 * DOWN,
                end + 0.04 * UP + 0.25 * (start[0] - x) * RIGHT, end,
            ))
        feeds.set_stroke(STEP_STROKE, 1.2).set_fill(opacity=0)
        return result, feeds

    def get_step_item(self, item):
        """An icon; or special words, stacked, optionally with e.g. in front."""
        if "icon" in item:
            return get_icon(item["icon"])
        chips = VGroup(chip(word, font_size=9) for word in item["chips"]).arrange(DOWN, buff=0.035)
        if "prefix" in item:
            return VGroup(text(item["prefix"], font_size=11, color=MUTED), chips).arrange(RIGHT, buff=0.05)
        return chips

    def get_mini_loop(self, x, y):
        words = VGroup(
            text(word, font_size=13, color=TOOL_COLOR, weight=BOLD)
            for word in ["Decide", "Use tool", "Observe"]
        ).arrange(RIGHT, buff=0.3).move_to([x, y, 0])
        arrows = VGroup(
            open_arrow(w1.get_right() + 0.05 * RIGHT, w2.get_left() + 0.05 * LEFT, TOOL_COLOR, width=1.5)
            for w1, w2 in zip(words[:-1], words[1:])
        )
        # Back from under Observe to under Decide, with the label in the gap
        cont = text("continue", font_size=11, color=TOOL_COLOR, slant=ITALIC)
        loop_y = y - 0.25
        cont.move_to([x, loop_y, 0])
        top_y = y - 0.1
        start = np.array([words[2].get_x(), top_y, 0])
        end = np.array([words[0].get_x(), top_y, 0])
        right = CubicBezier(
            start, start + 0.15 * DOWN,
            [cont.get_right()[0] + 0.25, loop_y, 0], cont.get_right() + 0.05 * RIGHT,
        )
        left = CubicBezier(
            cont.get_left() + 0.05 * LEFT, [cont.get_left()[0] - 0.25, loop_y, 0],
            end + 0.15 * DOWN, end,
        )
        tip = Polyline(end + [-0.04, -0.05, 0], end, end + [0.04, -0.05, 0])
        loop = VGroup(right, left, tip).set_stroke(TOOL_COLOR, 1.5).set_fill(opacity=0)
        return VGroup(words, arrows, loop, cont)
