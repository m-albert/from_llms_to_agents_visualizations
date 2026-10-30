from manim_imports_ext import *
from scenes.agentic_common import *


class Stage4Agent(AgenticScene):
    """
    The same chat model, in software that offers tools. The system prompt
    says which tools exist and how to call them. The model writes TOOL, the
    tool and its input; the software recognizes that shape at the end of
    the text, runs the tool, and joins its output to the input, which then
    goes through the model again. TOOL and STOP are always among the
    options. Bars, tool call and answer are the real outputs of a small
    chat model (Qwen2.5-1.5B-Instruct). The search returns two real papers;
    the answer cites both, but overstates one: the study found a link, not
    a cause.
    """
    stage_number = 4
    stage_title = "Tool-using agent"
    stage_subtitle = "Can retrieve and act; needs oversight"
    roles = True
    # Displayed system prompt; the bars were computed with a prompt that also
    # asks for short answers with a citation (see tools/compute_distributions.py)
    system_prompt = [
        ("What follows is a conversation between a human and a helpful and kind assistant. Tools:", INK),
        ("Search, Read, Code.", TOOL_COLOR),
        ("To use one, write TOOL + tool + “input”.", INK),
    ]
    stop_rule = "stop"
    special_rows = ("STOP", "TOOL")
    input_font_size = 14
    chat_font_size = 18
    input_bottom = -2.2
    tool_names = ["Search", "Read", "Code"]
    papers = DISTRIBUTIONS["stage4_text"]["papers"]
    random_seed = 5

    def construct(self):
        self.setup_stage()
        machine = self.machine
        weights_label = self.get_weights_label("+ Assistant behavior")
        tools = self.get_tools()
        self.add(self.title_group, self.software_window, machine[:2], weights_label)
        self.play(self.build_software())
        self.play(LaggedStartMap(FadeIn, tools, shift=0.2 * UP, lag_ratio=0.2))
        # The system prompt names the tools the software offers
        self.play(LaggedStart(
            (TransformFromCopy(tile.label, word) for tile, word in zip(tools.tiles, self.system_block.segments[1])),
            lag_ratio=0.2,
        ), run_time=1.2)
        self.wait()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))

        # The model decides to call a tool, one word at a time
        call_group, call_flow, call_bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.2)
        call_bubble.fill = "#DDF1EE"
        call_bubble.bg.set_fill("#DDF1EE")
        self.play(FadeIn(call_group[0]))
        self.open_turn()
        records = DISTRIBUTIONS["stage4_call"]
        for n, record in enumerate(records):
            self.run_pass(n, self.distribution_from_record(record), (call_flow, call_bubble), color=TOOL_COLOR)

        # The software sees TOOL + tool + "input" at the end and runs the tool
        sources = self.run_tool(tools, n_call_words=len(records), call_bubble=call_bubble)

        # Back through the model, now with the result in the input
        answer_group, flow, bubble = self.get_answer(sources.get_bottom()[1] - 0.12, with_icon=False)
        n0 = len(records)
        for n, record in enumerate(DISTRIBUTIONS["stage4_answer"]):
            self.run_pass(n0 + n, self.distribution_from_record(record), (flow, bubble), fast_time=0.35)
        self.flash_rule()

        # The citations point to what the tool returned
        citations = [VGroup(*flow[-8:-4]), VGroup(*flow[-4:])]
        for citation, source in zip(citations, sources):
            highlights, underlines = self.highlight_words(citation, color=TOOL_COLOR, fill="#DDF1EE")
            link = DashedLine(citation.get_top(), source.get_bottom(), dash_length=0.05).set_stroke(TOOL_COLOR, 1.5)
            self.add(highlights, flow)
            self.play(FadeIn(highlights), ShowCreation(underlines), ShowCreation(link), run_time=0.8)
            self.play(FadeOut(link), run_time=0.3)

        # But the second study found a link, not a cause
        claim = VGroup(*flow[-14:-8])
        highlights, underlines = self.highlight_words(claim)
        self.add(highlights, flow)
        self.play(FadeIn(highlights), ShowCreation(underlines))
        warning = warning_label(["Check the sources: the study", "shows a link, not a cause"], font_size=17)
        warning.next_to(bubble.bg, DOWN, buff=0.2).align_to(bubble.bg, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait(3)

    # Tools

    def get_tools(self):
        tiles = VGroup(self.get_tool_tile(name) for name in self.tool_names)
        tiles.arrange(RIGHT, buff=0.35)
        card = self.input_card.bg
        tiles.move_to([card.get_x(), (card.get_bottom()[1] + self.window_bottom) / 2, 0])
        tools = VGroup(*tiles)
        tools.tiles = tiles
        return tools

    def get_tool_tile(self, name, size=0.62):
        """A small program: a dark app window with a glyph, and its name."""
        body = RoundedRectangle(size, size, corner_radius=0.08)
        body.set_fill(CHIP_FILL, 1).set_stroke(width=0)
        dots = VGroup(Dot(radius=0.025) for _ in range(3)).arrange(RIGHT, buff=0.03)
        dots.set_fill(FRAME_GREY, 1).move_to(body.get_corner(UL) + [0.12, -0.08, 0])
        if name == "Search":
            glyph = VGroup(
                Circle(radius=0.11).set_stroke(TRUE_WHITE, 3),
                Line(ORIGIN, 0.12 * (RIGHT + DOWN)).set_stroke(TRUE_WHITE, 4).shift(0.08 * (RIGHT + DOWN)),
            )
        elif name == "Read":
            glyph = doc_icon(0.3, color=CHIP_FILL)
        else:
            glyph = Text(">_", font=MONO, font_size=18, weight=BOLD).set_color(TRUE_WHITE)
        glyph.move_to(body).shift(0.04 * DOWN)
        label = mono(name, font_size=14)
        label.next_to(body, DOWN, buff=0.06)
        tile = VGroup(body, dots, glyph, label)
        tile.body = body
        tile.label = label
        return tile

    def get_result_card(self):
        title = text("2 papers", font_size=14, weight=BOLD)
        lines = VGroup(Line(ORIGIN, w * RIGHT) for w in [0.6, 0.5, 0.6]).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        lines.set_stroke(FRAME_GREY, 2)
        content = VGroup(title, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        bg = SurroundingRectangle(content, buff=0.08).round_corners(0.05)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(TOOL_COLOR, 1.5)
        return VGroup(bg, content)

    def run_tool(self, tools, n_call_words, call_bubble):
        """
        Recognize TOOL + tool + "input" at the end of the text, run the tool,
        join its output to the input (and show it in the chat).
        """
        # The newest word joins the input first
        word, color, source = self.pending
        self.play(self.append_to_input(word, color, source), run_time=0.4)
        self.pending = None
        call_words = VGroup(*self.input_convo[-n_call_words:])
        highlights, underlines = self.highlight_words(call_words, color=TOOL_COLOR, fill="#DDF1EE")
        self.add(highlights, call_words)
        self.play(FadeIn(highlights), ShowCreation(underlines), self.pulse(self.rule_badge[0], color="#DDF1EE"))

        # Run it
        tile = tools.tiles[0]
        link = Arrow(call_words.get_bottom(), tile.body.get_top(), buff=0.08, thickness=3).set_fill(TOOL_COLOR)
        glow = SurroundingRectangle(tile.body, buff=0.05).round_corners(0.1).set_stroke(TOOL_COLOR, 4)
        spinner = Arc(start_angle=0, angle=1.5 * PI, radius=0.48).set_stroke(TOOL_COLOR, 3).move_to(tile.body)
        self.play(GrowArrow(link), ShowCreation(glow))
        self.play(Rotate(spinner, -2 * TAU, about_point=tile.body.get_center(), run_time=1.2, rate_func=linear), FadeIn(spinner, run_time=0.2))
        self.remove(spinner)

        # Its output is joined to the input (and recorded in the chat)
        card = self.get_result_card().move_to(tile.body)
        self.play(FadeIn(card, scale=0.5), FadeOut(link))
        self.turns[-1]["closed"] = True
        flow = self.input_flow
        flow.line_break()
        label = flow.add_word("Result:", color=MUTED)
        # Titles and findings are in the input in full; shortened here with "…"
        result_words = VGroup()
        for n, paper in enumerate(self.papers):
            if n > 0:
                flow.line_break()
            string = f"[{n + 1}] {paper['ref']}: " + " ".join(paper["title"].split()[:2]) + " …"
            result_words.add(*flow.add_words(string.split(" "), color=TOOL_COLOR))
        stop = flow.add_word("STOP")
        flow.line_break()
        assistant = flow.add_word("Assistant:", color=MUTED)
        sources = VGroup(self.get_source_card(paper) for paper in self.papers)
        sources.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        sources.next_to(call_bubble.bg, DOWN, buff=0.1).align_to(call_bubble.bg, LEFT)
        self.play(
            FadeTransform(card.copy(), result_words),
            FadeIn(label), FadeIn(stop),
            TransformFromCopy(card, sources),
            FadeOut(card),
            run_time=1.5,
        )
        self.play(FadeIn(assistant), FadeOut(highlights), FadeOut(underlines), FadeOut(glow))
        self.input_convo.add(label, *result_words, stop, assistant)
        self.turns.append(dict(role="Result:", items=[(w, TOOL_COLOR, None) for w in result_words], closed=True))
        self.open_turn()
        self.wait()
        return sources

    def get_source_card(self, paper):
        """A search result as the chat shows it: a small paper card with its reference."""
        icon = doc_icon(0.22, color=TOOL_COLOR)
        label = text(paper["ref"], font_size=self.chat_font_size - 3, color=TOOL_COLOR)
        content = VGroup(icon, label).arrange(RIGHT, buff=0.1)
        bg = SurroundingRectangle(content, buff=0.07).round_corners(0.06)
        bg.set_fill("#DDF1EE", 1).set_stroke(TOOL_COLOR, 1)
        return VGroup(bg, content)
