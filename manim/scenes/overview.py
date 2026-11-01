from manim_imports_ext import *
from manimlib.utils.svg_export import _get_path_data
from scenes.agentic_common import *
from scenes.stage_5_agent import Stage5Agent


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
    The five stages side by side (the llm_to_agentic_ai schematic), built up
    stage by stage in the style of the manim scenes. The last frame is also
    written out as an SVG next to the video.
    """
    col_xs = [-5.64, -2.82, 0.0, 2.82, 5.64]
    col_width = 2.62
    steps_y = 3.3
    year_y, title_y, subtitle_y = 2.38, 2.06, 1.78
    model_y = 0.78
    window_height = 1.62
    caption_y = -0.2
    chat_top, chat_bottom = -0.42, -3.5
    warning_y = -3.78
    chat_font_size = 12
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
            year="2024", year_note="o1, DeepSeek-R1",
            title="Reasoning model", subtitle="Thinks first, but still no sources",
            trained=True, software=["Generate until", "STOP"], caption="+ Thinking, marked by special words",
            panel="split",
            thought="Harm in humans proven? Not yet → don't overclaim.",
            answer="ANSWER Microplastics are found in human tissue, but harm is still unclear. STOP",
            warning=["More careful, but still", "answers from memory"],
        ),
        dict(
            year="2024-today", year_note="tool use & agents",
            title="Tool-using agent", subtitle="Can retrieve and act; needs oversight",
            trained=True, software=["Generate until", "STOP"], caption="+ Tools, called by a special word",
            panel="tools",
            tools=["Search web", "Read files", "Execute code"],
            thought="Need sources first.",
            tool_call=("Search web", "“microplastics health publication”"),
            results=["Paper 1: The effects of micro…", "Paper 2: Microplastics in hu…"],
            answer=(
                "ANSWER Microplastics are found in human blood and tissue (Paper 1). "
                "Whether they harm health is not yet proven (Paper 2). STOP"
            ),
            warning=["Less likely to hallucinate,", "but still possible"],
        ),
    ]
    steps = [
        dict(title="Pre-training", subtitle="Learn by predicting the next word",
             items=["Books", "Web", "Code", "Papers"]),
        dict(title="Post-training", subtitle="Answer helpfully, then stop",
             items=["Examples", "Feedback", "e.g. STOP"]),
        dict(title="Reasoning training", subtitle="Think privately, then answer",
             items=["Problems", "Rewards", "THINK ANSWER"]),
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
        for n in range(1, len(self.stages)):
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
            text(f"≈ {stage['year']}", font_size=13, color=ACCENT, weight=BOLD),
            text(f"· {stage['year_note']}", font_size=13, color=MUTED),
        ).arrange(RIGHT, buff=0.06)
        number = VGroup(
            Circle(radius=0.12).set_fill(ACCENT, 1).set_stroke(width=0),
            text(str(n + 1), font_size=15, color=TRUE_WHITE, weight=BOLD),
        )
        number[1].move_to(number[0])
        title = text(stage["title"], font_size=19, weight=BOLD)
        title_row = VGroup(number, title).arrange(RIGHT, buff=0.1)
        subtitle = text(stage["subtitle"], font_size=13, color=MUTED)
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
        panel = stage.get("panel")
        width = self.col_width if panel else 1.6
        window = app_window(width, self.window_height, title="", title_font_size=10, bar_height=0.18)
        window.move_to([x, self.model_y, 0])
        machine = self.get_transformer_drawing()
        blocks = machine[0]
        blocks.set_fill(TRAINED_FILL if stage["trained"] else UNTRAINED_FILL, 1)
        flat_dials, last_dials = self.get_machine_dials(blocks)
        last_dials.set_stroke(opacity=0.15)
        blocks.add(last_dials)
        blocks.set_height(0.42)
        software = self.get_software_label(stage["software"])
        left_part = VGroup(blocks, software)
        if panel == "tools":
            left_part.add(self.get_programs(stage["tools"]))
        left_part.arrange(DOWN, buff=0.08)
        content_y = self.model_y - window.bar_height / 2
        model_x = x - width / 2 + 0.52 if panel else x
        left_part.move_to([model_x, content_y, 0])
        group = VGroup(window, left_part)
        if panel:
            divider_x = x - width / 2 + 1.02
            divider = DashedLine(
                [divider_x, window.get_top()[1] - window.bar_height - 0.08, 0],
                [divider_x, window.get_bottom()[1] + 0.08, 0],
                dash_length=0.05,
            ).set_stroke(FRAME_GREY, 1)
            content = self.get_split_panel() if panel == "split" else self.get_prompt_panel(stage["tools"])
            content.move_to([divider_x + 0.08, content_y, 0], LEFT)
            group.add(divider, content)
        caption = text(stage["caption"], font_size=13, color=MUTED)
        caption.move_to([x, self.caption_y, 0])
        group.add(caption)
        return group

    def get_panel_title(self, string, color):
        return text(string, font_size=9, color=color, weight=BOLD)

    def get_split_panel(self):
        """How the software splits the output (not part of the system prompt)."""
        rows = VGroup(
            VGroup(chip(word, font_size=8), text(label, font_size=10, color=color, slant=slant)).arrange(RIGHT, buff=0.05)
            for word, label, color, slant in [
                ("THINK", "→ Private thoughts", MUTED, ITALIC),
                ("ANSWER", "→ Answer", INK, NORMAL),
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        return VGroup(self.get_panel_title("SPLIT OUTPUT", MUTED), rows).arrange(DOWN, aligned_edge=LEFT, buff=0.1)

    def get_prompt_panel(self, tools):
        """The system prompt lists the tools and how to call them."""
        intro = VGroup(
            text("“…can use these tools", font_size=10, slant=ITALIC),
            text("by writing", font_size=10, slant=ITALIC),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        syntax = VGroup(chip("TOOL", font_size=8), text("+ tool + <input>:", font_size=10, slant=ITALIC)).arrange(RIGHT, buff=0.05)
        names = VGroup(text(name, font_size=10, color=TOOL_COLOR) for name in tools)
        names.add(text("…”", font_size=10, color=TOOL_COLOR))
        names.arrange(DOWN, aligned_edge=LEFT, buff=0.03)
        return VGroup(self.get_panel_title("SYSTEM PROMPT", ACCENT), intro, syntax, names).arrange(DOWN, aligned_edge=LEFT, buff=0.05)

    def get_programs(self, tools):
        """The same tools, as programs the software can run."""
        tiles = VGroup()
        for name in tools:
            tile = Stage5Agent.get_tool_tile(self, name)
            tile.remove(tile.label)
            tiles.add(tile.set_height(0.2))
        tiles.arrange(RIGHT, buff=0.05)
        label = self.get_panel_title("PROGRAMS", TOOL_COLOR)
        return VGroup(label, tiles).arrange(DOWN, buff=0.04)

    def get_software_label(self, lines):
        top = text(lines[0], font_size=11, color=MUTED)
        if lines[1] in SPECIAL_WORDS:
            bottom = chip(lines[1], font_size=9)
        else:
            bottom = text(lines[1], font_size=11, color=MUTED)
        return VGroup(top, bottom).arrange(DOWN, buff=0.05)

    def get_question(self, x):
        flow = FlowText(ORIGIN, 1.9, font_size=self.chat_font_size)
        flow.add_words(self.question.replace(" and ", " & ").split(" "))
        bubble = ChatBubble(flow, USER_FILL, buff=0.08)
        icon = person_icon(0.2)
        group = VGroup(bubble, icon)
        bubble.move_to([x + self.col_width / 2 - 0.32, self.chat_top - 0.12, 0], UR)
        icon.next_to(bubble, RIGHT, buff=0.06)
        return group

    def get_thought_box(self, stage, left, top, width):
        """Dashed box with the private thoughts (and, for the agent, the tool call and its results)."""
        flow = FlowText(ORIGIN, width - 0.16, font_size=self.chat_font_size - 1, slant=ITALIC)
        flow.add_word("THINK")
        flow.add_words(stage["thought"].split(" "), color=MUTED)
        content = VGroup(flow)
        if "tool_call" in stage:
            name, query = stage["tool_call"]
            row = VGroup(chip("TOOL", font_size=8), text(name, font_size=11, color=TOOL_COLOR)).arrange(RIGHT, buff=0.06)
            query_mob = text(query, font_size=10, color=TOOL_COLOR, slant=ITALIC)
            call = VGroup(row, query_mob).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
            pill = SurroundingRectangle(call, buff=0.05).round_corners(0.06)
            pill.set_stroke(TOOL_COLOR, 1).set_fill("#DDF1EE", 1)
            results = VGroup(text("↳ " + result, font_size=10, color=MUTED) for result in stage["results"])
            results.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
            content.add(VGroup(pill, call), results)
        content.arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        content.move_to([left + 0.08, top - 0.08, 0], UL)
        rect = RoundedRectangle(width, content.get_height() + 0.16, corner_radius=0.08)
        rect.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1)
        rect.move_to([left, top, 0], UL)
        return VGroup(DashedVMobject(rect, num_dashes=110), content)

    def get_answer_parts(self, stage, x, question):
        left = x - self.col_width / 2
        top = question.get_bottom()[1] - 0.08
        icon = robot_icon(0.2)
        icon.move_to([left + 0.17, top - 0.12, 0])
        parts = VGroup(icon)
        content_left = left + 0.36
        content_width = self.col_width - 0.36 - 0.1

        if "thought" in stage:
            thought = self.get_thought_box(stage, content_left, top, content_width)
            parts.add(thought)
            top = thought.get_bottom()[1] - 0.07

        flow = FlowText([content_left + 0.08, top - 0.06, 0], content_width - 0.16, font_size=self.chat_font_size)
        flow.add_words(stage["answer"].split(" "))
        bubble = ChatBubble(flow, PANEL_FILL, buff=0.08)
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

        if "note" in stage:
            note = text(stage["note"], font_size=12, color=MUTED, slant=ITALIC)
            note.next_to(bubble.bg, DOWN, buff=0.12).align_to(bubble.bg, LEFT).shift(0.08 * RIGHT)
            parts.add(note)

        warning = None
        if "warning" in stage:
            warning = warning_label(stage["warning"], font_size=13)
            warning.move_to([x, self.warning_y, 0])
        return parts, warning

    # Steps

    def get_step_card(self, n, step):
        x = (self.col_xs[n] + self.col_xs[n + 1]) / 2
        title = text(step["title"], font_size=18, color=ACCENT, weight=BOLD)
        subtitle = text(step["subtitle"], font_size=12, color=MUTED)
        if step["items"]:
            items = VGroup(self.get_step_item(item) for item in step["items"])
            items.arrange(RIGHT, buff=0.18)
        else:
            items = self.get_mini_loop()
        content = VGroup(title, subtitle, items).arrange(DOWN, buff=0.09)
        card_bg = RoundedRectangle(2.6, 1.22, corner_radius=0.12)
        card_bg.set_fill(STEP_FILL, 1).set_stroke(STEP_STROKE, 1.5)
        card_bg.move_to([x, self.steps_y, 0])
        content.move_to(card_bg)
        connector = Line(card_bg.get_bottom(), [x, self.model_y, 0]).set_stroke(ACCENT, 2)
        chevron = VGroup(
            Circle(radius=0.12).set_fill(ACCENT, 1).set_stroke(width=0),
            Tex(R"\rightarrow", font_size=17).set_color(TRUE_WHITE),
        )
        chevron.move_to([x, self.model_y, 0])
        result = VGroup(card_bg, content, connector, chevron)
        result.card = VGroup(card_bg, content)
        result.connector = connector
        result.chevron = chevron
        return result

    def get_step_item(self, item):
        """A word; "e.g. STOP": an example special word; "THINK ANSWER": special words, stacked."""
        words = item.split(" ")
        if all(word in SPECIAL_WORDS for word in words):
            return VGroup(chip(word, font_size=10) for word in words).arrange(DOWN, buff=0.04)
        if words[0] == "e.g.":
            return VGroup(
                text("e.g.", font_size=11, color=MUTED),
                word_mob(words[-1], font_size=13),
            ).arrange(RIGHT, buff=0.05)
        return text(item, font_size=13)

    def get_mini_loop(self):
        words = VGroup(
            text(word, font_size=13, color=TOOL_COLOR, weight=BOLD)
            for word in ["Decide", "Use tool", "Observe"]
        ).arrange(RIGHT, buff=0.28)
        arrows = VGroup(
            Arrow(w1, w2, buff=0.05, thickness=2).set_fill(TOOL_COLOR)
            for w1, w2 in zip(words[:-1], words[1:])
        )
        loop_back = Arrow(
            words[2].get_bottom(), words[0].get_bottom(),
            path_arc=-70 * DEGREES, buff=0.04, thickness=2,
        ).set_fill(TOOL_COLOR)
        cont = text("continue", font_size=10, color=TOOL_COLOR, slant=ITALIC)
        cont.next_to(loop_back, DOWN, buff=0.02)
        return VGroup(words, arrows, loop_back, cont)
