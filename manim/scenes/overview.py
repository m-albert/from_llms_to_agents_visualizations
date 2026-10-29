from manim_imports_ext import *
from manimlib.utils.svg_export import _get_path_data
from scenes.agentic_common import *


STEP_FILL = "#EDF2FA"
STEP_STROKE = "#B9CBE6"


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
            attrs.append('stroke-linejoin="round"')
            if stroke_opacity < 1:
                attrs.append(f'stroke-opacity="{stroke_opacity:.4g}"')
            if getattr(mob, "stroke_behind", False):
                attrs.append('paint-order="stroke"')
        lines.append(f'  <path {" ".join(attrs)}/>')
    lines.append('</svg>')
    Path(filename).write_text("\n".join(lines))


class AgenticOverview(AgenticScene):
    """
    The four stages side by side (the llm_to_agentic_ai schematic), built up
    stage by stage in the style of the manim scenes. The last frame is also
    written out as an SVG next to the video.
    """
    col_xs = [-5.3, -1.77, 1.77, 5.3]
    col_width = 3.3
    steps_y = 3.25
    year_y, title_y, subtitle_y = 2.3, 1.95, 1.63
    model_y = 0.7
    caption_y = -0.27
    chat_top, chat_bottom = -0.5, -3.38
    font_scale = 1.0
    stages = [
        dict(
            year="2017", year_note="Transformer architecture",
            title="Untrained model", subtitle="Random output: nothing learned yet",
            trained=False, software=["Generate", "10 words"], caption="Random weights",
            answer="orbit lamp the seven glass of whenever banana north quietly",
            note="10 random words",
        ),
        dict(
            year="2018-2020", year_note="GPT-1 to GPT-3",
            title="Pre-trained base model", subtitle="Completes text, not yet an assistant",
            trained=True, software=["Generate", "10 words"], caption="Learned language patterns",
            answer="...and in seafood? What do recent papers say about PFAS",
            note="Continues from input prompt",
        ),
        dict(
            year="2022", year_note="ChatGPT",
            title="AI assistant", subtitle="Helpful answers, but may hallucinate",
            trained=True, software=["Generate until", "STOP"], caption="+ Assistant behavior",
            answer="Studies suggest microplastics may be linked to inflammation. A landmark study proved direct harm in humans. STOP",
            claim="A landmark study proved direct harm in humans.",
            warning=["Plausible, but from memory", "and potentially hallucinated"],
        ),
        dict(
            year="2023-today", year_note="tool use & agents",
            title="Tool-using agent", subtitle="Can retrieve and act; needs oversight",
            trained=True, software=["Generate until", "STOP"], caption="+ Tools, called by a special word",
            tools=["Search web", "Read files", "Execute code"],
            tool_steps=["Search papers", "Read PDFs", "Summarize findings"],
            answer="Retrieved papers: evidence is still emerging. STOP",
            sources=["Paper A", "Paper B", "Paper C"],
            warning=["Less likely to hallucinate,", "but still possible"],
        ),
    ]
    steps = [
        dict(title="Pre-training", subtitle="Learn by predicting the next word",
             items=["Books", "Web", "Code", "Papers"]),
        dict(title="Post-training", subtitle="Answer helpfully, then stop",
             items=["Examples", "Feedback", "e.g. STOP"]),
        dict(title="Tools + agent loop", subtitle="Run the model in a loop with tools",
             items=None),
    ]
    export_name = "AgenticOverview.svg"

    def construct(self):
        columns = [self.get_column(n, stage) for n, stage in enumerate(self.stages)]
        step_cards = [self.get_step_card(n, step) for n, step in enumerate(self.steps)]

        # Stage 1
        self.play(LaggedStartMap(FadeIn, columns[0].header, shift=0.1 * DOWN, lag_ratio=0.2))
        self.play(FadeIn(columns[0].model))
        self.play(FadeIn(columns[0].chat_window), FadeIn(columns[0].question))
        self.play(FadeIn(columns[0].answer, lag_ratio=0.05))
        self.wait()

        # Each step leads to the next stage
        for n in range(1, 4):
            card = step_cards[n - 1]
            self.play(FadeIn(card.card, 0.2 * DOWN))
            self.play(ShowCreation(card.connector), FadeIn(card.chevron, scale=0.5))
            self.play(
                LaggedStartMap(FadeIn, columns[n].header, shift=0.1 * DOWN, lag_ratio=0.2),
                TransformFromCopy(columns[n - 1].model, columns[n].model),
            )
            self.play(FadeIn(columns[n].chat_window), FadeIn(columns[n].question))
            self.play(FadeIn(columns[n].answer, lag_ratio=0.05))
            if columns[n].warning is not None:
                self.play(FadeIn(columns[n].warning, 0.1 * UP))
            self.wait()
        self.wait(2)

        if self.file_writer.write_to_movie:
            export_svg(self.mobjects, Path(self.file_writer.output_directory, self.export_name))

    # Columns

    def get_column(self, n, stage):
        x = self.col_xs[n]
        left = x - self.col_width / 2
        column = VGroup()

        # Header: year, number + title, subtitle
        year = VGroup(
            text(f"≈ {stage['year']}", font_size=16, color=ACCENT, weight=BOLD),
            text(f"· {stage['year_note']}", font_size=16, color=MUTED),
        ).arrange(RIGHT, buff=0.08)
        number = VGroup(
            Circle(radius=0.15).set_fill(ACCENT, 1).set_stroke(width=0),
            text(str(n + 1), font_size=18, color=TRUE_WHITE, weight=BOLD),
        )
        number[1].move_to(number[0])
        title = text(stage["title"], font_size=24, weight=BOLD)
        title_row = VGroup(number, title).arrange(RIGHT, buff=0.12)
        subtitle = text(stage["subtitle"], font_size=17, color=MUTED)
        for mob, y in [(year, self.year_y), (title_row, self.title_y), (subtitle, self.subtitle_y)]:
            mob.move_to([left, y, 0], LEFT)
        column.header = VGroup(year, title_row, subtitle)

        # Model in its software window, plus caption
        column.model = self.get_model_window(stage, x)

        # Chat
        chat_window = RoundedRectangle(self.col_width, self.chat_top - self.chat_bottom, corner_radius=0.12)
        chat_window.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1.5)
        chat_window.move_to([x, (self.chat_top + self.chat_bottom) / 2, 0])
        column.chat_window = chat_window
        column.question = self.get_question(x)
        column.answer, column.warning = self.get_answer_parts(stage, x, column.question)
        return column

    def get_model_window(self, stage, x):
        has_tools = "tools" in stage
        width = self.col_width if has_tools else 2.1
        window = app_window(width, 1.5, title="", title_font_size=12, bar_height=0.2)
        window.move_to([x, self.model_y, 0])
        machine = self.get_transformer_drawing()
        blocks = machine[0]
        blocks.set_fill(TRAINED_FILL if stage["trained"] else UNTRAINED_FILL, 1)
        flat_dials, last_dials = self.get_machine_dials(blocks)
        last_dials.set_stroke(opacity=0.15)
        blocks.add(last_dials)
        blocks.set_height(0.5)
        model_x = x - width / 2 + 0.85 if has_tools else x
        blocks.move_to([model_x, self.model_y + 0.22, 0])
        software = self.get_software_label(stage["software"])
        software.next_to(blocks, DOWN, buff=0.1)
        group = VGroup(window, blocks, software)
        if has_tools:
            divider = DashedLine(
                window.get_top() + (0.3 + 2.1 - width / 2) * RIGHT + 0.3 * DOWN,
                window.get_bottom() + (0.3 + 2.1 - width / 2) * RIGHT + 0.1 * UP,
                dash_length=0.05,
            ).set_stroke(FRAME_GREY, 1)
            divider.match_x(window).shift(0.12 * RIGHT)
            tools = VGroup(
                VGroup(chip("TOOL", font_size=11), text(name, font_size=14, color=TOOL_COLOR)).arrange(RIGHT, buff=0.08)
                for name in stage["tools"]
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            dots = text("...", font_size=14, color=TOOL_COLOR)
            dots.next_to(tools, DOWN, buff=0.02).align_to(tools[0][1], LEFT)
            tools.add(dots)
            tools.next_to(divider, RIGHT, buff=0.12).match_y(window).shift(0.08 * DOWN)
            group.add(divider, tools)
        caption = text(stage["caption"], font_size=17, color=MUTED)
        caption.move_to([x, self.caption_y, 0])
        group.add(caption)
        return group

    def get_software_label(self, lines):
        top = text(lines[0], font_size=14, color=MUTED)
        if lines[1] in SPECIAL_WORDS:
            bottom = chip(lines[1], font_size=11)
        else:
            bottom = text(lines[1], font_size=14, color=MUTED)
        return VGroup(top, bottom).arrange(DOWN, buff=0.06)

    def get_question(self, x):
        flow = FlowText(ORIGIN, 2.3, font_size=15)
        flow.add_words(self.question.replace(" and ", " & ").split(" "))
        bubble = ChatBubble(flow, USER_FILL, buff=0.1)
        icon = person_icon(0.24)
        group = VGroup(bubble, icon)
        bubble.move_to([x + 1.32, self.chat_top - 0.15, 0], UR)
        icon.next_to(bubble, RIGHT, buff=0.08)
        return group

    def get_answer_parts(self, stage, x, question):
        left = x - self.col_width / 2
        top = question.get_bottom()[1] - 0.1
        icon = robot_icon(0.24)
        icon.move_to([left + 0.22, top - 0.14, 0])
        parts = VGroup(icon)
        content_left = left + 0.45

        if "tool_steps" in stage:
            steps = VGroup()
            for name in stage["tool_steps"]:
                label = text(name, font_size=14, color=TOOL_COLOR)
                tag = chip("TOOL", font_size=10)
                row = VGroup(tag, label).arrange(RIGHT, buff=0.08)
                pill = SurroundingRectangle(row, buff=0.04).round_corners(0.08)
                pill.set_stroke(TOOL_COLOR, 1).set_fill("#DDF1EE", 1)
                steps.add(VGroup(pill, row))
            steps.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
            steps.move_to([content_left, top, 0], UL)
            parts.add(steps)
            top = steps.get_bottom()[1] - 0.06

        flow = FlowText([content_left + 0.1, top - 0.08, 0], 2.55, font_size=15)
        flow.add_words(stage["answer"].split(" "))
        bubble = ChatBubble(flow, PANEL_FILL, buff=0.1)
        parts.add(bubble)

        if "claim" in stage:
            claim_words = VGroup(*flow[-len(stage["claim"].split(" ")) - 1:-1])
            highlights = VGroup(
                SurroundingRectangle(word, buff=0.02).set_fill(WARN_FILL, 1).set_stroke(width=0)
                for word in claim_words
            )
            underlines = VGroup(
                DashedLine(word.get_corner(DL), word.get_corner(DR), dash_length=0.04).shift(0.03 * DOWN)
                for word in claim_words
            ).set_stroke(WARN, 1.5)
            bubble.remove(flow)
            bubble.add(highlights, underlines, flow)

        if "sources" in stage:
            sources = VGroup()
            for name in stage["sources"]:
                label = text(name, font_size=14)
                bg = SurroundingRectangle(label, buff=0.05).round_corners(0.04)
                bg.set_stroke(INK, 1).set_fill(TRUE_WHITE, 1)
                sources.add(VGroup(bg, label))
            sources.arrange(RIGHT, buff=0.08)
            sources.next_to(bubble.bg, DOWN, buff=0.07).align_to(bubble.bg, LEFT)
            parts.add(sources)

        if "note" in stage:
            note = text(stage["note"], font_size=14, color=MUTED, slant=ITALIC)
            note.next_to(bubble.bg, DOWN, buff=0.15).align_to(bubble.bg, LEFT).shift(0.1 * RIGHT)
            parts.add(note)

        warning = None
        if "warning" in stage:
            warning = warning_label(stage["warning"], font_size=16)
            warning.move_to([x, (self.chat_bottom - 4.0) / 2, 0])
        return parts, warning

    # Steps

    def get_step_card(self, n, step):
        x = (self.col_xs[n] + self.col_xs[n + 1]) / 2
        title = text(step["title"], font_size=22, color=ACCENT, weight=BOLD)
        subtitle = text(step["subtitle"], font_size=15, color=MUTED)
        if step["items"]:
            items = VGroup(
                VGroup(
                    text("e.g.", font_size=13, color=MUTED),
                    word_mob(item.split(" ")[-1], font_size=15),
                ).arrange(RIGHT, buff=0.06)
                if item.startswith("e.g.") else text(item, font_size=15)
                for item in step["items"]
            )
            items.arrange(RIGHT, buff=0.25)
        else:
            items = self.get_mini_loop()
        content = VGroup(title, subtitle, items).arrange(DOWN, buff=0.1)
        card_bg = RoundedRectangle(3.0, 1.32, corner_radius=0.12)
        card_bg.set_fill(STEP_FILL, 1).set_stroke(STEP_STROKE, 1.5)
        card_bg.move_to([x, self.steps_y, 0])
        content.move_to(card_bg)
        connector = Line(card_bg.get_bottom(), [x, self.model_y, 0]).set_stroke(ACCENT, 2)
        chevron = VGroup(
            Circle(radius=0.14).set_fill(ACCENT, 1).set_stroke(width=0),
            Tex(R"\rightarrow", font_size=20).set_color(TRUE_WHITE),
        )
        chevron.move_to([x, self.model_y, 0])
        result = VGroup(card_bg, content, connector, chevron)
        result.card = VGroup(card_bg, content)
        result.connector = connector
        result.chevron = chevron
        return result

    def get_mini_loop(self):
        words = VGroup(
            text(word, font_size=16, color=TOOL_COLOR, weight=BOLD)
            for word in ["Decide", "Use tool", "Observe"]
        ).arrange(RIGHT, buff=0.35)
        arrows = VGroup(
            Arrow(w1, w2, buff=0.06, thickness=2).set_fill(TOOL_COLOR)
            for w1, w2 in zip(words[:-1], words[1:])
        )
        loop_back = Arrow(
            words[2].get_bottom(), words[0].get_bottom(),
            path_arc=-70 * DEGREES, buff=0.04, thickness=2,
        ).set_fill(TOOL_COLOR)
        cont = text("continue", font_size=12, color=TOOL_COLOR, slant=ITALIC)
        cont.next_to(loop_back, DOWN, buff=0.02)
        return VGroup(words, arrows, loop_back, cont)
