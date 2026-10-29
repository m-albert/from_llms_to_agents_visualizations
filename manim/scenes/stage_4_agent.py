from manim_imports_ext import *
from scenes.agentic_common import *


class Stage4Agent(AgenticScene):
    """
    The same model, now in software that offers tools. The model can write
    the special word TOOL followed by a call; the software, not the model,
    runs the tool and pastes the result into the text, then calls the model
    again: decide, use tool, observe, repeat. The final answer draws on
    retrieved sources, so hallucination is less likely, but still possible.
    """
    stage_number = 4
    stage_title = "Tool-using agent"
    stage_subtitle = "Can retrieve and act; needs oversight"
    code_lines = [
        "repeat until word is STOP:",
        "    probabilities = model(text)",
        "    word = pick(probabilities)",
        "    text = text + word",
        "    if text ends in a TOOL call:",
        "        text = text + run(call)",
    ]
    code_width = 4.4
    code_font_size = 20
    answer_font_size = 22
    model_line, pick_line, append_line = 1, 2, 3
    tool_names = ["Search papers", "Read files", "Run code"]
    # Probabilities in the detailed step are illustrative
    first_words = ["TOOL", "Studies", "Recent", "Microplastics", "Research", "There"]
    first_probs = [0.64, 0.14, 0.08, 0.06, 0.03, 0.02]
    tool_font_size = 20
    random_seed = 5

    def construct(self):
        self.setup_stage(show=False)
        machine, code = self.machine, self.code
        weights_label = text("+ Assistant behavior", font_size=22, color=MUTED)
        weights_label.next_to(machine[0], DOWN, buff=0.2)
        old_code = CodePanel([
            "text = format(chat)",
            "repeat until word is STOP:",
            "    probabilities = model(text)",
            "    word = pick(probabilities)",
            "    text = text + word",
        ], width=7.8, font_size=23, line_buff=0.24)
        old_code.move_to([self.window_left + 0.15, -0.55, 0], UL)
        self.add(self.title_group, self.software_window, machine[:2], weights_label, old_code)
        self.wait()

        # Same model, new software: tools, and a tool step in the loop
        tools = self.get_tools_panel()
        self.play(FadeTransform(old_code, code), run_time=1.5)
        self.play(FadeIn(tools[0]), FadeIn(tools[1]))
        self.play(LaggedStartMap(FadeIn, tools.rows, shift=0.2 * LEFT, lag_ratio=0.3))
        tool_rect = SurroundingRectangle(code.lines[4:], buff=0.06).set_stroke(TOOL_COLOR, 2)
        self.play(ShowCreation(tool_rect))
        self.wait()
        self.play(FadeOut(tool_rect))

        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.play(GrowArrow(self.out_arrow))
        loop_diagram = self.get_loop_diagram()

        # Pass 1: the model decides to use a tool
        chat_content = VGroup(self.user_bubble)
        call1, flow1, bubble1 = self.get_tool_call_line(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(call1[0]))
        self.feed_model(chat_content, run_time=1.2)
        chart = self.show_distribution(self.first_words, self.first_probs)
        self.pick(chart, 0, run_time=0.8)
        self.append_word(chart, 0, flow1, bubble1, "TOOL", run_time=0.7)
        self.play(FadeIn(loop_diagram[0]), code.unhighlight())
        for word in "Search: microplastics health".split(" "):
            self.quick_word(flow1, bubble1, word, run_time=0.3, color=TOOL_COLOR)
        chat_content.add(call1)

        # The software runs the search
        papers = self.get_paper_cards()
        papers.next_to(call1, DOWN, buff=0.15).align_to(bubble1.bg, LEFT)
        self.run_tool(flow1, tools.rows[0], papers, loop_diagram)
        chat_content.add(papers)

        # Pass 2: read the papers found
        call2, flow2, bubble2 = self.get_tool_call_line(papers.get_bottom()[1] - 0.15, with_icon=False)
        self.feed_model(chat_content, run_time=1.0)
        self.play(FadeIn(loop_diagram[3]), code.unhighlight())
        for word in ["TOOL", *"Read: Paper A, B, C".split(" ")]:
            self.quick_word(flow2, bubble2, word, run_time=0.3, color=TOOL_COLOR)
        chat_content.add(call2)
        read_result = self.get_read_result()
        read_result.next_to(call2, DOWN, buff=0.12).align_to(bubble2.bg, LEFT)
        self.run_tool(flow2, tools.rows[1], read_result, loop_diagram, show_labels=False)
        chat_content.add(read_result)

        # Pass 3: answer from what was retrieved, then STOP
        answer_group, flow3, bubble3 = self.get_answer(read_result.get_bottom()[1] - 0.15)
        answer_group[0].set_opacity(0)
        self.feed_model(chat_content, run_time=1.0)
        self.play(code.unhighlight(), run_time=0.2)
        for word in "Retrieved papers: evidence is still emerging.".split(" "):
            self.quick_word(flow3, bubble3, word, run_time=0.3)
        self.quick_word(flow3, bubble3, "STOP", run_time=0.4)
        end_rect = SurroundingRectangle(code.lines[0], buff=0.06).set_stroke(WARN, 2)
        self.play(code.highlight_line(0), ShowCreation(end_rect))
        self.play(FadeOut(end_rect), code.unhighlight())

        # Sources, linked to what was retrieved
        sources = VGroup(
            self.get_source_chip(letter) for letter in "ABC"
        ).arrange(RIGHT, buff=0.12)
        sources.next_to(bubble3.bg, DOWN, buff=0.12).align_to(bubble3.bg, LEFT)
        links = VGroup(
            DashedLine(source.get_top(), paper.get_bottom(), dash_length=0.06).set_stroke(TOOL_COLOR, 1.5)
            for source, paper in zip(sources, papers)
        )
        self.play(LaggedStartMap(FadeIn, sources, shift=0.1 * UP, lag_ratio=0.2))
        self.play(ShowCreation(links, lag_ratio=0.2), run_time=1.5)
        self.wait()
        self.play(FadeOut(links))

        # Still fallible
        warning = warning_label(["Less likely to hallucinate,", "but still possible"], font_size=21)
        warning.next_to(sources, DOWN, buff=0.22).align_to(sources, LEFT)
        oversight = VGroup(
            text("Check the sources.", font_size=21, color=INK),
            text("Tools act in the real world:", font_size=21, color=INK),
            text("agents need oversight.", font_size=21, color=INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        oversight.next_to(loop_diagram, DOWN, buff=0.3).align_to(loop_diagram, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.play(FadeIn(oversight, lag_ratio=0.3))
        self.wait(3)

    # Pieces

    def get_tools_panel(self):
        left = self.window_left + 0.15 + self.code_width + 0.2
        right = self.window_right - 0.15
        top = self.code.get_top()[1]
        bg = RoundedRectangle(right - left, top - (self.window_bottom + 0.15), corner_radius=0.1)
        bg.set_fill(PANEL_FILL, 1).set_stroke(width=0)
        bg.move_to([left, top, 0], UL)
        header = text("Tools", font_size=22, color=MUTED, weight=BOLD)
        header.move_to(bg.get_corner(UL) + [0.2, -0.3, 0], LEFT)
        rows = VGroup()
        for name in self.tool_names:
            row = VGroup(chip("TOOL", font_size=16), text(name, font_size=22, color=TOOL_COLOR))
            row.arrange(RIGHT, buff=0.15)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.next_to(header, DOWN, buff=0.25, aligned_edge=LEFT)
        panel = VGroup(bg, header, rows)
        panel.rows = rows
        return panel

    def get_tool_call_line(self, top_y, with_icon=True):
        icon = robot_icon(0.4)
        icon.move_to([self.chat_left + 0.35, top_y - 0.2, 0])
        if not with_icon:
            icon.set_opacity(0)
        flow = FlowText([self.chat_left + 0.85, top_y - 0.08, 0], 4.1, font_size=self.tool_font_size)
        bubble = ChatBubble(flow, "#DDF1EE", buff=0.12)
        bubble.bg.set_opacity(0)
        return VGroup(icon, bubble), flow, bubble

    def get_paper_cards(self):
        cards = VGroup()
        for letter in "ABC":
            title = text(f"Paper {letter}", font_size=18)
            lines = VGroup(
                Line(ORIGIN, width * RIGHT).set_stroke(FRAME_GREY, 2)
                for width in [0.8, 0.6]
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
            content = VGroup(title, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            bg = SurroundingRectangle(content, buff=0.1).round_corners(0.06)
            bg.set_fill(TRUE_WHITE, 1).set_stroke(FRAME_GREY, 1)
            cards.add(VGroup(bg, content))
        cards.arrange(RIGHT, buff=0.15)
        return cards

    def get_read_result(self):
        return text("Full text of Papers A, B, C", font_size=19, color=MUTED, slant=ITALIC)

    def get_source_chip(self, letter):
        label = text(f"Paper {letter}", font_size=18)
        bg = SurroundingRectangle(label, buff=0.07).round_corners(0.05)
        bg.set_stroke(INK, 1).set_fill(TRUE_WHITE, 1)
        return VGroup(bg, label)

    def get_loop_diagram(self):
        """Decide -> Use tool -> Observe, with a 'continue' arrow back."""
        words = VGroup(
            text("Decide", font_size=22, color=TOOL_COLOR, weight=BOLD),
            text("Use tool", font_size=22, color=TOOL_COLOR, weight=BOLD),
            text("Observe", font_size=22, color=TOOL_COLOR, weight=BOLD),
        ).arrange(RIGHT, buff=0.5)
        arrows = VGroup(
            Arrow(w1, w2, buff=0.12, thickness=3).set_fill(TOOL_COLOR)
            for w1, w2 in zip(words[:-1], words[1:])
        )
        loop_back = CurvedArrow(
            words[2].get_bottom() + 0.05 * DOWN,
            words[0].get_bottom() + 0.05 * DOWN,
            angle=-50 * DEGREES,
        ).set_color(TOOL_COLOR)
        cont = text("continue", font_size=20, color=TOOL_COLOR, slant=ITALIC)
        cont.next_to(loop_back.pfp(0.5), DOWN, buff=0.05)
        diagram = VGroup(
            words[0],
            VGroup(arrows[0], words[1]),
            VGroup(arrows[1], words[2]),
            VGroup(loop_back, cont),
        )
        # Top right of the software window, free once the bars are gone
        diagram.move_to([
            (self.out_arrow.get_end()[0] + self.window_right) / 2,
            self.machine[0].get_y() + 0.35, 0
        ])
        return diagram

    def run_tool(self, call_flow, tool_row, result, loop_diagram, show_labels=True):
        """The software sees a TOOL call, runs the tool, appends the result."""
        code = self.code
        call_copy = call_flow.copy()
        self.play(code.highlight_line(4), run_time=0.5)
        self.play(
            Transform(call_copy, VGroup(VectorizedPoint(tool_row.get_left())), lag_ratio=0.02, remover=True, path_arc=20 * DEGREES),
            tool_row[1].animate.scale(1.1, about_edge=LEFT).set_anim_args(rate_func=there_and_back),
            *([FadeIn(loop_diagram[1])] if show_labels else []),
            run_time=1.2,
        )
        self.play(
            code.highlight_line(5),
            FadeInFromPoint(result, tool_row.get_right()),
            *([FadeIn(loop_diagram[2])] if show_labels else []),
            run_time=1.2,
        )
        self.wait(0.5)
