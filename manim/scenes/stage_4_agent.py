from manim_imports_ext import *
from scenes.agentic_common import *


class Stage4Agent(AgenticScene):
    """
    The same model, now in software that offers tools. The tool descriptions
    are part of the system prompt, which is put in front of the user's
    message in the input. The model can write the special word TOOL followed
    by a call; the software, not the model, runs the tool and attaches the
    result to the input, then runs the model again: decide, use tool,
    observe, repeat. The final answer draws on retrieved sources, so
    hallucination is less likely, but still possible.
    """
    stage_number = 4
    stage_title = "Tool-using agent"
    stage_subtitle = "Can retrieve and act; needs oversight"
    loop_rule = "stop"
    input_font_size = 17
    tool_names = ["Search papers", "Read files", "Run code"]
    system_prompt = [
        ("You are a helpful assistant.", INK),
        ("Tools: Search papers, Read files, Run code.", TOOL_COLOR),
        ("To use one, write TOOL and the call.", INK),
    ]
    system_pill_label = "System prompt + tools"
    answer_font_size = 22
    tool_font_size = 20
    random_seed = 5

    def construct(self):
        self.setup_stage()
        machine = self.machine
        weights_label = self.get_weights_label("+ Assistant behavior")
        self.add(
            self.title_group, self.software_window, machine[:2], weights_label,
            self.input_panel, self.loop_parts,
        )
        self.wait()

        # Same model, new software: tools, a way to call them, a way back
        tools = self.get_tools_box()
        tool_paths = self.get_tool_paths(tools)
        self.play(FadeIn(tools[:2]), LaggedStartMap(FadeIn, tools.rows, shift=0.2 * LEFT, lag_ratio=0.3))
        self.play(LaggedStartMap(FadeIn, tool_paths, lag_ratio=0.4), run_time=2)
        self.wait()

        # The system prompt describes the tools; it goes in front of the chat message
        card = self.get_system_prompt_card(font_size=18)
        intro, tool_words, usage = card.segments
        self.play(FadeIn(card.frame), FadeIn(intro), FadeIn(usage))
        self.play(
            FadeIn(tool_words[0]),
            LaggedStart(
                (TransformFromCopy(row, tool_words[2 * n + 1:2 * n + 3], path_arc=20 * DEGREES)
                for n, row in enumerate(tools.rows)),
                lag_ratio=0.3,
            ),
            run_time=1.8,
        )
        self.wait()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.join_system_prompt(card)

        # Pass 1: the model decides to use a tool
        call1, flow1, bubble1 = self.get_tool_call_line(self.user_bubble.get_bottom()[1] - 0.15)
        self.play(FadeIn(call1[0]))
        n0 = len(self.input_flow)
        self.emit_word("TOOL", flow1, bubble1, slow=True)
        decide = self.get_stage_tag("Decide", self.get_out_point() + 0.55 * UP)
        self.play(FadeIn(decide, 0.1 * DOWN))
        for word in "Search: microplastics health".split(" "):
            self.emit_word(word, flow1, bubble1, run_time=0.3, color=TOOL_COLOR)

        # The software runs the search and attaches the result to the input
        papers = self.get_paper_cards()
        papers.next_to(call1, DOWN, buff=0.1).align_to(bubble1.bg, LEFT)
        use_tool = self.get_stage_tag("Use tool", tools.get_top() + 0.25 * UP)
        observe = self.get_stage_tag("Observe", ORIGIN)
        observe.next_to(tool_paths.result_label, DOWN, buff=0.08)
        self.run_tool(
            tools, tool_paths, VGroup(*self.input_flow[n0:]), 0, papers, "Papers A, B, C",
            tags=(use_tool, observe),
        )

        # Pass 2: read the papers found
        call2, flow2, bubble2 = self.get_tool_call_line(papers.get_bottom()[1] - 0.1, with_icon=False)
        n0 = len(self.input_flow)
        for word in ["TOOL", *"Read: Paper A, B, C".split(" ")]:
            self.emit_word(word, flow2, bubble2, run_time=0.3, color=TOOL_COLOR)
        read_result = self.get_read_result()
        read_result.next_to(call2, DOWN, buff=0.08).align_to(bubble2.bg, LEFT)
        self.run_tool(tools, tool_paths, VGroup(*self.input_flow[n0:]), 1, read_result, "Full texts A, B, C")

        # Pass 3: answer from what was retrieved, then STOP
        answer_group, flow3, bubble3 = self.get_answer(read_result.get_bottom()[1] - 0.1)
        for word in "Retrieved papers: evidence is still emerging.".split(" "):
            self.emit_word(word, flow3, bubble3, run_time=0.3)
        self.emit_word("STOP", flow3, bubble3, run_time=0.5)
        rect = self.flash_rule()
        self.wait(0.5)
        self.play(FadeOut(rect))

        # Sources, linked to what was retrieved
        sources = VGroup(
            self.get_source_chip(letter) for letter in "ABC"
        ).arrange(RIGHT, buff=0.12)
        sources.next_to(bubble3.bg, DOWN, buff=0.1).align_to(bubble3.bg, LEFT)
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
        warning.next_to(sources, DOWN, buff=0.15).align_to(sources, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        takeaway = text("Check the sources. Tools act in the real world: agents need oversight.", font_size=24)
        takeaway.move_to(3.72 * DOWN)
        self.play(FadeIn(takeaway, 0.2 * UP))
        self.wait(3)

    # Pieces

    def get_tools_box(self, left=-0.6, top=1.75, bottom=0.1):
        right = self.window_right - 0.15
        bg = RoundedRectangle(right - left, top - bottom, corner_radius=0.1)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(TOOL_COLOR, 1.5)
        bg.move_to([left, top, 0], UL)
        header = text("Tools", font_size=20, color=TOOL_COLOR, weight=BOLD)
        header.move_to(bg.get_corner(UL) + [0.2, -0.15, 0], UL)
        rows = VGroup(text(name, font_size=19, color=TOOL_COLOR) for name in self.tool_names)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rows.next_to(header, DOWN, buff=0.18, aligned_edge=LEFT)
        box = VGroup(bg, header, rows)
        box.rows = rows
        return box

    def get_tool_paths(self, tools):
        """Input -> tools (a TOOL call), tools -> input (the result)."""
        bottom = tools[0].get_bottom()[1]
        call_x, result_x = tools[0].get_left()[0] + 0.3, tools[0].get_right()[0] - 0.35
        call = flow_arrow([call_x, self.input_top, 0], [call_x, bottom, 0], color=TOOL_COLOR)
        result = flow_arrow([result_x, bottom, 0], [result_x, self.input_top, 0], color=TOOL_COLOR)
        call_label = VGroup(chip("TOOL", font_size=13), text("call", font_size=16, color=TOOL_COLOR))
        call_label.arrange(RIGHT, buff=0.06)
        call_label.next_to(call, LEFT, buff=0.1).set_y(-0.4)
        result_label = text("+ result", font_size=16, color=TOOL_COLOR)
        result_label.move_to([(call_x + result_x) / 2, -0.4, 0])
        paths = VGroup(call, call_label, result, result_label)
        paths.call = call
        paths.result = result
        paths.result_label = result_label
        return paths

    def get_stage_tag(self, string, point):
        tag = text(string, font_size=20, color=TOOL_COLOR, weight=BOLD, slant=ITALIC)
        tag.move_to(point)
        return tag

    def get_result_pill(self, string):
        label = text("Result: " + string, font_size=self.input_font_size - 2, color=TOOL_COLOR)
        bg = SurroundingRectangle(label, buff=0.05).round_corners(0.05)
        bg.set_fill("#DDF1EE", 1).set_stroke(TOOL_COLOR, 1)
        return VGroup(bg, label)

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

    def run_tool(self, tools, paths, call_words, row_index, chat_result, result_string, tags=()):
        """
        The software sees a complete TOOL call in the input, runs the tool,
        and attaches the result to the input (and shows it in the chat).
        """
        row = tools.rows[row_index]
        call_rect = SurroundingRectangle(call_words, buff=0.04).set_stroke(TOOL_COLOR, 2)
        self.play(ShowCreation(call_rect), run_time=0.5)
        use_tool = tags[0] if tags else None
        self.play(
            TransformFromCopy(call_words, VGroup(VectorizedPoint(row.get_left())), path_arc=-20 * DEGREES, lag_ratio=0.01, remover=True),
            self.pulse(paths.call, color=BAR_COLOR),
            row.animate.scale(1.15, about_edge=LEFT).set_anim_args(rate_func=there_and_back, time_span=(0.6, 1.2)),
            FadeOut(call_rect),
            *([FadeIn(use_tool, 0.1 * DOWN)] if use_tool else []),
            run_time=1.2,
        )
        pill = self.get_result_pill(result_string)
        target = self.input_flow.next_word(pill)
        source = pill.copy().move_to(row)
        self.play(
            FadeTransform(source, target, path_arc=-10 * DEGREES),
            self.pulse(paths.result, color=BAR_COLOR),
            FadeInFromPoint(chat_result, row.get_center()),
            *([FadeIn(tags[1], 0.1 * DOWN)] if len(tags) > 1 else []),
            run_time=1.4,
        )
        self.input_flow.add(target)
        self.wait(0.5)
