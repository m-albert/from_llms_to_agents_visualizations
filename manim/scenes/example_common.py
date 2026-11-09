"""
Shared pieces of the example bots (scenes/example_*.py): agents built
like Stage5Agent, but for one concrete use, so that what their software
does is visible. The model is an off-the-shelf reasoning model (no
training of its own); the bot is its system prompt, its tools and the
data the tools can reach. Tools sit at the bottom of the software window,
next to the folder their data is in.
"""
from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.stage_5_agent import Stage5Agent


def folder_icon(height=0.2, color=MUTED):
    body = RoundedRectangle(1.4, 1.0, corner_radius=0.12)
    tab = RoundedRectangle(0.6, 0.35, corner_radius=0.1)
    tab.move_to(body.get_corner(UL), DL).shift(0.15 * DOWN)
    icon = VGroup(tab, body).set_fill(color, 1).set_stroke(width=0)
    return icon.set_height(height)


class ExampleAgentScene(Stage5Agent):
    example_title = ""
    example_subtitle = ""
    weights_text = "Off-the-shelf reasoning model"
    input_bottom = -3.25
    input_font_size = 12
    chat_font_size = 16

    def get_title(self):
        icon = robot_icon(0.48)
        title = text(self.example_title, font_size=40, weight=BOLD)
        subtitle = text(self.example_subtitle, font_size=26, color=MUTED)
        icon.move_to([self.window_left + 0.26, 3.5, 0])
        title.next_to(icon, RIGHT, buff=0.2)
        subtitle.next_to(title, RIGHT, buff=0.4, aligned_edge=DOWN)
        return VGroup(icon, title, subtitle)

    def get_chart(self, *args, **kwargs):
        # Long words (tool names, file names) are shrunk to fit left of the bars
        chart = super().get_chart(*args, **kwargs)
        for label, bar, pct in chart.rows:
            if label.get_width() > 1.0:
                label.set_width(1.0, about_edge=RIGHT)
        return chart

    # The data the tools can reach, at the bottom right of the software window

    def get_folder(self, name, note, files, n_cols=2):
        """A folder the tools can read: its name, a note, and its files."""
        header = VGroup(
            folder_icon(0.2),
            mono(name, font_size=13, color=INK),
            text(note, font_size=14, color=MUTED, slant=ITALIC),
        ).arrange(RIGHT, buff=0.1)
        items = VGroup(
            VGroup(doc_icon(0.24), mono(file, font_size=11)).arrange(RIGHT, buff=0.07)
            for file in files
        )
        items.arrange_in_grid(n_cols=n_cols, h_buff=0.25, v_buff=0.1, aligned_edge=LEFT, fill_rows_first=True)
        content = VGroup(header, items).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        bg = SurroundingRectangle(content, buff=0.12).round_corners(0.08)
        bg.set_fill(PANEL_FILL, 1).set_stroke(FRAME_GREY, 1)
        folder = VGroup(bg, content)
        folder.move_to([self.window_right - 0.15, self.tools_y(), 0], RIGHT)
        folder.bg = bg
        folder.header = header
        folder.items = items
        return folder

    def name_tools(self, tools, words):
        """The system prompt names the tools: each tile's name goes to its word in the prompt."""
        self.play(LaggedStart(
            (TransformFromCopy(tile.label, word) for tile, word in zip(tools.tiles, words)),
            lag_ratio=0.3,
        ), run_time=1.2)

    # A tool call

    def call_tool(self, n_call_words, tile, run, result, chat_part, keep=False):
        """
        The software sees TOOL + tool + <input> at the end of the text. It
        runs the tool: run() plays the tool's own animation and returns
        (mobject the output comes from, mobjects to remove afterwards). The
        output is joined to the input as a Result turn (result: one entry per
        line, a string or a mobject such as a line of code), and chat_part
        shows it in the private thoughts (kept when they fold away if keep).
        The thoughts then continue below it.
        """
        # The newest word joins the input first
        word, color, source = self.pending
        self.play(self.append_to_input(word, color, source), run_time=0.4)
        self.pending = None
        call_words = VGroup(*self.input_convo[-n_call_words:])
        highlights, underlines = self.highlight_words(call_words, color=TOOL_COLOR, fill=TOOL_FILL)
        self.add(highlights, call_words)
        self.play(FadeIn(highlights), ShowCreation(underlines), self.pulse(self.rule_badge[0], color=TOOL_FILL))

        # Run it
        link = Arrow(call_words.get_right(), tile.body.get_top(), buff=0.08, thickness=3).set_fill(TOOL_COLOR)
        glow = SurroundingRectangle(tile.body, buff=0.05).round_corners(0.1).set_stroke(TOOL_COLOR, 4)
        spinner = Arc(start_angle=0, angle=1.5 * PI, radius=0.48).set_stroke(TOOL_COLOR, 3).move_to(tile.body)
        self.play(GrowArrow(link), ShowCreation(glow))
        self.play(
            Rotate(spinner, -TAU, about_point=tile.body.get_center(), run_time=0.8, rate_func=linear),
            FadeIn(spinner, run_time=0.2),
        )
        self.remove(spinner)
        output, cleanup = run()

        # Its output is joined to the input (and shown in the thoughts)
        self.turns[-1]["closed"] = True
        flow = self.input_flow
        flow.line_break()
        label = flow.add_word("Result:", color=MUTED)
        result_mobs = VGroup()
        for n, line in enumerate(result):
            if n > 0:
                flow.line_break()
            if isinstance(line, Mobject):
                result_mobs.add(flow.add_word(line))
            else:
                result_mobs.add(*flow.add_words(line.split(" "), color=TOOL_COLOR))
        stop = flow.add_word("STOP")
        flow.line_break()
        assistant = flow.add_word("Assistant:", color=MUTED)
        bubble = self.thought_bubble
        chat_part.move_to([bubble.top_left[0] + bubble.buff, bubble.get_bottom_y() - 0.06, 0], UL)
        bubble.add_part(chat_part)
        if keep:
            bubble.keep = chat_part
        self.play(
            FadeTransform(output.copy(), result_mobs),
            FadeIn(label), FadeIn(stop),
            TransformFromCopy(output, chat_part),
            Transform(bubble.bg, bubble.get_bg()),
            run_time=1.5,
        )
        self.play(
            FadeIn(assistant),
            *map(FadeOut, [highlights, underlines, glow, link, *cleanup]),
        )
        self.input_convo.add(label, *result_mobs, stop, assistant)
        self.turns.append(dict(role="Result:", items=[], closed=True))
        self.open_turn()
        self.mark_input_synced()
        self.in_call = False
        flow = bubble.add_flow(bubble.get_bottom_y() - 0.06, self.chat_font_size - 2)
        self.chat = (flow, bubble)
        self.wait(0.5)
        return result_mobs

    def get_result_card(self, title, lines, icon=None, font_size=None):
        """A tool's output as the chat shows it: a small teal card."""
        font_size = font_size or self.chat_font_size - 5
        icon = icon or doc_icon(0.28, color=TOOL_COLOR)
        label = VGroup(
            text(title, font_size=font_size + 1, color=TOOL_COLOR, weight=BOLD),
            *lines,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        content = VGroup(icon, label).arrange(RIGHT, buff=0.1, aligned_edge=UP)
        bg = SurroundingRectangle(content, buff=0.07).round_corners(0.06)
        bg.set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 1)
        return VGroup(bg, content)

    def end_note(self, lines, color=INK, font_size=16):
        """A note in the empty part of the software window (right of the model)."""
        note = VGroup(text(line, font_size=font_size, color=color) for line in lines)
        note.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        note.move_to([1.15, self.machine[0].get_y() + 0.6, 0])
        return note
