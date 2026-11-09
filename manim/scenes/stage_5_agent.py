from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.icons import get_icon
from scenes.stage_outputs import STAGE5_ANSWER, STAGE5_CALL, STAGE5_PAPERS, words


class Stage5Agent(AgenticScene):
    """
    The same reasoning model, in software that offers tools: programs it
    can run. The system prompt says which tools exist and how to call them.
    While thinking, the model writes TOOL, the tool and its input; the
    software recognizes that shape at the end of the text, runs the tool,
    and joins its output to the input, which then goes through the model
    again. Tool call and result stay inside the private thoughts; then the
    model answers from the result and cites it. THINK, ANSWER, TOOL and
    STOP are always among the options. Words, bars and the two papers
    are scripted (scenes/stage_outputs.py).
    """
    stage_number = 5
    stage_title = "Tool-using agent"
    stage_subtitle = "Can retrieve and act; needs oversight"
    roles = True
    system_prompt = [
        (SYSTEM_PROMPT + " Tools:", INK),
        ("Search web, Read files, Execute code.", TOOL_COLOR),
        ("To use one, write TOOL + tool + “input”.", INK),
    ]
    stop_rule = "stop"
    special_rows = ("THINK", "ANSWER", "TOOL", "STOP")
    input_font_size = 14
    chat_font_size = 18
    tool_names = ["Search web", "Read files", "Execute code"]
    # tool name -> icon (scenes/icons.py); by default from the name
    tool_glyphs = {}
    papers = STAGE5_PAPERS
    random_seed = 5

    def construct(self):
        self.setup_stage()
        machine = self.machine
        weights_label = self.get_weights_label("+ Thinking")
        tools = self.get_tools()
        self.add(self.title_group, self.software_window, machine[:2], weights_label)
        # The same model, trained to also call tools
        self.play(FadeTransform(weights_label, self.get_weights_label("+ Tool use")))
        self.play(self.build_software())
        self.highlight_system_prompt()
        self.play(LaggedStartMap(FadeIn, tools, shift=0.2 * UP, lag_ratio=0.2))
        # The system prompt names the tools the software offers
        tool_words = self.system_block.segments[1]
        self.play(LaggedStart(
            (
                TransformFromCopy(tile.label, VGroup(*tool_words[2 * n:2 * n + 2]))
                for n, tile in enumerate(tools.tiles)
            ),
            lag_ratio=0.2,
        ), run_time=1.2)
        self.wait()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))

        # The model thinks, then decides to call a tool, one word at a time
        icon, flow, bubble = self.get_thought(self.user_bubble.get_bottom()[1] - 0.2)
        self.play(FadeIn(icon), FadeIn(bubble))
        self.open_turn()
        self.in_call = False
        n = self.run_records(STAGE5_CALL, colors=self.call_color)

        # The software sees TOOL + tool + "input" at the end and runs the tool
        n_call_words = len(STAGE5_CALL) - words(STAGE5_CALL).index("TOOL")
        sources = self.run_tool(tools, n_call_words=n_call_words)

        # Back through the model, now with the result in the input: it answers
        self.run_records(STAGE5_ANSWER, n0=n, colors=self.thought_color)
        self.flash_rule()

        # The citations point to what the tool returned
        flow = self.chat[0]
        answer = words(STAGE5_ANSWER)[:-1]  # ANSWER ... (as in the chat; STOP isn't)
        starts = [n for n, word in enumerate(answer) if word == "(Paper"]
        for start, source in zip(starts, sources):
            citation = VGroup(*flow[start:start + 2])
            highlights, underlines = self.highlight_words(citation, color=TOOL_COLOR, fill="#DDF1EE")
            link = DashedLine(citation.get_top(), source.get_bottom(), dash_length=0.05).set_stroke(TOOL_COLOR, 1.5)
            self.add(highlights, flow)
            self.play(FadeIn(highlights), ShowCreation(underlines), ShowCreation(link), run_time=0.8)
            self.play(FadeOut(link), run_time=0.3)

        verdict = verdict_label("warn", ["Can answer from sources,", "might still hallucinate"], font_size=18)
        verdict.next_to(self.chat[1].bg, DOWN, buff=0.2).align_to(self.chat[1].bg, LEFT)
        self.play(FadeIn(verdict, 0.2 * UP))
        self.wait(3)

    def call_color(self, record):
        """Thoughts in grey, the tool call (from TOOL on) in teal."""
        if record["word"] == "TOOL":
            self.in_call = True
        return TOOL_COLOR if self.in_call else MUTED

    # Tools: programs at the bottom of the software window, right of the input

    def tools_y(self):
        return (self.rule_badge.get_bottom()[1] + self.window_bottom) / 2 - 0.05

    def get_tools(self):
        tiles = VGroup(self.get_tool_tile(name, glyph=self.tool_glyphs.get(name)) for name in self.tool_names)
        tiles.arrange(RIGHT, buff=0.2, aligned_edge=UP)
        tiles.move_to([self.input_right + 0.25, self.tools_y() - 0.12, 0], LEFT)
        title = text("PROGRAMS", font_size=15, color=TOOL_COLOR, weight=BOLD)
        title.next_to(tiles, UP, buff=0.12).align_to(tiles, LEFT)
        tools = VGroup(title, *tiles)
        tools.tiles = tiles
        return tools

    def get_tool_tile(self, name, size=0.56, glyph=None):
        """
        A program, as in the schematics: a teal tile with a line icon
        ("web", "folder", "code" or "papers"; by default from the name), and its name.
        """
        if glyph is None:
            glyph = "web" if name.startswith("Search") else "folder" if name.startswith("Read") else "code"
        body = RoundedRectangle(size, size, corner_radius=0.1)
        body.set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 2)
        icon = get_icon(glyph, color=TOOL_COLOR, height=0.62 * size, width=2.5).move_to(body)
        label = text(name, font_size=15, color=TOOL_COLOR)
        label.next_to(body, DOWN, buff=0.08)
        tile = VGroup(body, icon, label)
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

    def run_tool(self, tools, n_call_words):
        """
        Recognize TOOL + tool + "input" at the end of the text, run the tool,
        join its output to the input (and show it in the thoughts in the chat).
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
        link = Arrow(call_words.get_right(), tile.body.get_top(), buff=0.08, thickness=3).set_fill(TOOL_COLOR)
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
        result_words = VGroup()
        for n, paper in enumerate(self.papers):
            if n > 0:
                flow.line_break()
            string = f"Paper {n + 1}: {paper['title']}: {paper['finding']}."
            result_words.add(*flow.add_words(string.split(" "), color=TOOL_COLOR))
        stop = flow.add_word("STOP")
        flow.line_break()
        assistant = flow.add_word("Assistant:", color=MUTED)
        bubble = self.thought_bubble
        sources = VGroup(self.get_source_card(n, paper) for n, paper in enumerate(self.papers))
        sources.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        sources.move_to([bubble.top_left[0] + bubble.buff, self.chat[0].get_bottom_y() - 0.06, 0], UL)
        bubble.add_part(sources)
        bubble.keep = sources
        self.play(
            FadeTransform(card.copy(), result_words),
            FadeIn(label), FadeIn(stop),
            TransformFromCopy(card, sources),
            Transform(bubble.bg, bubble.get_bg()),
            FadeOut(card),
            run_time=1.5,
        )
        self.play(FadeIn(assistant), FadeOut(highlights), FadeOut(underlines), FadeOut(glow))
        self.input_convo.add(label, *result_words, stop, assistant)
        self.turns.append(dict(role="Result:", items=[(w, TOOL_COLOR, None) for w in result_words], closed=True))
        self.open_turn()
        self.mark_input_synced()
        self.wait()
        return sources

    def get_source_card(self, n, paper):
        """A search result as the chat shows it: a small paper card with its title."""
        icon = doc_icon(0.3, color=TOOL_COLOR)
        label = VGroup(
            text(f"Paper {n + 1}", font_size=self.chat_font_size - 4, color=TOOL_COLOR, weight=BOLD),
            text(paper["title"], font_size=self.chat_font_size - 6, color=TOOL_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        content = VGroup(icon, label).arrange(RIGHT, buff=0.1)
        bg = SurroundingRectangle(content, buff=0.07).round_corners(0.06)
        bg.set_fill("#DDF1EE", 1).set_stroke(TOOL_COLOR, 1)
        return VGroup(bg, content)
