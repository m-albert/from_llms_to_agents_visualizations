from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.example_common import ExampleAgentScene, TOOL_FILL
from scenes.example_outputs import (
    TUTOR_ANSWER, TUTOR_CALL_CODE, TUTOR_CALL_SOLUTION, TUTOR_CELL, TUTOR_CODE, TUTOR_FILES,
    TUTOR_NOTEBOOK, TUTOR_OUTPUT, TUTOR_SOLUTION, TUTOR_SOLUTION_FILE,
)
from scenes.stage_outputs import words


class CourseTutorBot(ExampleAgentScene):
    """
    A course tutor that lives in JupyterLab, next to the student's notebook.
    Two tools: read_code reads a cell of the student's notebook,
    read_solution reads the exercise's solution, from a folder students
    can't see. The system prompt says not to give solutions but to hint at
    the next step. The model reads the code and the solution while
    thinking; the solution stays in the private thoughts, the student gets
    a hint. Words, bars, code and solution are scripted
    (scenes/example_outputs.py).
    """
    example_title = "Course tutor bot"
    example_subtitle = "Lives in JupyterLab; gives hints, not solutions"
    software_title = "Tutor software"
    chat_title = "JupyterLab"
    question = f"My segmentation in cell {TUTOR_CELL} finds only one object. What's wrong?"
    system_prompt = [
        ("You're the virtual course tutor of the SCF lab course for master students. Your goal is "
         "to help students with understanding image analysis concepts, as well as Python coding and debugging.", INK),
        ("Don't provide solutions to exercises, but instead hint students towards the next steps "
         "towards the solution.", INK),
        ("You can use the available tools by running", INK),
        ("TOOL read_code <cell>", TOOL_COLOR),
        ("or", INK),
        ("TOOL read_solution <exercise>.", TOOL_COLOR),
    ]
    tool_names = ["read_code", "read_solution"]
    tool_glyphs = {"read_code": "code", "read_solution": "papers"}
    input_font_size = 11
    # A wider input (the system prompt is long), so shorter bars
    input_right = -3.35
    bar_max_len = 0.75
    chat_font_size = 16
    code_font_size = 10
    random_seed = 8

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label(self.weights_text)
        tools = self.get_tools()
        folder = self.get_folder("solutions/", "students can't see these", TUTOR_FILES)
        self.folder = folder
        notebook = self.notebook
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)
        self.play(self.build_software())
        self.highlight_system_prompt()
        self.play(FadeIn(tools, shift=0.2 * UP), FadeIn(folder))
        segments = self.system_block.segments
        self.name_tools(tools, [segments[3][1], segments[5][1]])
        self.wait()

        # JupyterLab: the student's notebook, and the tutor next to it
        self.play(FadeIn(self.chat_window), FadeIn(notebook.tab), FadeIn(notebook.cell))
        self.play(FadeIn(notebook.output, 0.1 * DOWN))
        self.play(FadeIn(notebook.divider), FadeIn(notebook.header), FadeIn(self.user_bubble, 0.25 * LEFT))

        # The model thinks and reads the student's code...
        icon, flow, bubble = self.get_thought(self.user_bubble.get_bottom()[1] - 0.2)
        self.play(FadeIn(icon), FadeIn(bubble))
        self.open_turn()
        self.in_call = False
        n = self.run_records(TUTOR_CALL_CODE, colors=self.call_color)
        tiles = tools.tiles
        code_card = self.get_result_card(f"Read cell [{TUTOR_CELL}]", [], icon=self.code_icon())
        code_result = [f"cell [{TUTOR_CELL}]:", *self.code_lines(TUTOR_CODE[:-1]), self.code_line(f"{TUTOR_CODE[-1]}  → {TUTOR_OUTPUT}")]
        self.call_tool(self.n_call_words(TUTOR_CALL_CODE), tiles[0], lambda: self.run_read_code(tiles[0]), code_result, code_card, keep=True)

        # ...then the solution, which the student can't see...
        n = self.run_records(TUTOR_CALL_SOLUTION, n0=n, colors=self.call_color)
        solution_card = self.get_result_card(f"Read solution: {TUTOR_SOLUTION_FILE}", [], icon=doc_icon(0.24, color=TOOL_COLOR))
        solution_result = [f"{TUTOR_SOLUTION_FILE}:", *self.code_lines(TUTOR_SOLUTION)]
        solution_words = self.call_tool(self.n_call_words(TUTOR_CALL_SOLUTION), tiles[1], self.run_read_solution, solution_result, solution_card)

        # ...and gives a hint: the solution stays in the private thoughts
        self.run_records(TUTOR_ANSWER, n0=n, colors=self.thought_color)
        self.flash_rule()

        # What the system prompt asked for: the model saw the solution, the student gets a hint
        rule = segments[1]
        rule_highlights, _ = self.highlight_words(rule, fill="#CADDF2")
        sol_highlights, _ = self.highlight_words(solution_words, fill=WARN_FILL)
        answer_rect = SurroundingRectangle(self.chat[1].bg, buff=0.04).round_corners(0.15).set_stroke(ACCENT, 2)
        notes = VGroup(
            self.end_note(["System prompt: hint,", "don't give the solution"], color=ACCENT, font_size=14),
            verdict_label("ok", ["The model reads the solution,", "the student only gets a hint"], font_size=14),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        notes.move_to([self.window_right - 0.2, self.machine[0].get_y() + 0.5, 0], RIGHT)
        self.add(rule_highlights, self.system_block.flow)
        self.play(FadeIn(rule_highlights), FadeIn(notes[0], 0.1 * DOWN))
        self.add(sol_highlights, self.input_convo)
        self.play(FadeIn(sol_highlights), FadeIn(notes[1], 0.1 * DOWN), ShowCreation(answer_rect))
        self.wait(3)

    def n_call_words(self, records):
        return len(records) - words(records).index("TOOL")

    # JupyterLab, in the chat window: the notebook above the tutor's chat

    def code_line(self, line, color=INK):
        return mono(line, font_size=self.code_font_size, color=color)

    def code_lines(self, lines, color=INK):
        return [self.code_line(line, color) for line in lines]

    def code_icon(self):
        return text("</>", font_size=self.chat_font_size - 4, color=TOOL_COLOR, weight=BOLD)

    def get_notebook(self):
        left = self.chat_left + 0.15
        right = self.chat_right - 0.15
        top = window_content_top(self.chat_window, 0.1)
        tab_label = mono(TUTOR_NOTEBOOK, font_size=12, color=INK)
        tab_bg = SurroundingRectangle(tab_label, buff=0.07).round_corners(0.04)
        tab_bg.set_fill(PANEL_FILL, 1).set_stroke(FRAME_GREY, 1)
        tab = VGroup(tab_bg, tab_label)
        tab.move_to([left, top, 0], UL)
        prompt = mono(f"[{TUTOR_CELL}]:", font_size=11, color=MUTED)
        code = VGroup(self.code_line(line, color=INK) for line in TUTOR_CODE)
        code.scale(1.15)
        code.arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        code_bg = Rectangle(right - left - 0.55, code.get_height() + 0.2)
        code_bg.set_fill(PANEL_FILL, 1).set_stroke(FRAME_GREY, 1)
        code_bg.next_to(tab, DOWN, buff=0.15).align_to(right * RIGHT, RIGHT)
        code.move_to(code_bg.get_left() + 0.12 * RIGHT, LEFT)
        prompt.next_to(code_bg, LEFT, buff=0.08).align_to(code_bg, UP).shift(0.06 * DOWN)
        cell = VGroup(prompt, code_bg, code)
        output = mono(TUTOR_OUTPUT, font_size=12, color=INK)
        output.next_to(code_bg, DOWN, buff=0.12, aligned_edge=LEFT).shift(0.12 * RIGHT)
        divider = DashedLine([left, 0, 0], [right, 0, 0], dash_length=0.06).set_stroke(FRAME_GREY, 1.5)
        divider.set_y(output.get_bottom()[1] - 0.18)
        header = VGroup(robot_icon(0.22), text("Course tutor", font_size=16, color=MUTED, weight=BOLD))
        header.arrange(RIGHT, buff=0.1)
        header.next_to(divider, DOWN, buff=0.12).align_to(divider, LEFT)
        notebook = VGroup(tab, cell, output, divider, header)
        notebook.tab = tab
        notebook.cell = cell
        notebook.code = code
        notebook.code_bg = code_bg
        notebook.output = output
        notebook.divider = divider
        notebook.header = header
        return notebook

    def get_user_bubble(self):
        # The tutor's chat starts below the notebook
        self.notebook = self.get_notebook()
        group = super().get_user_bubble()
        group.shift((self.notebook.header.get_bottom()[1] - 0.15 - group.get_top()[1]) * UP)
        return group

    # The tools

    def run_read_code(self, tile):
        """read_code: the software reads the cell from the student's notebook."""
        cell = self.notebook.code_bg
        glow = SurroundingRectangle(cell, buff=0.05).set_stroke(TOOL_COLOR, 3)
        link = Arrow(tile.body.get_right(), cell.get_left(), buff=0.1, thickness=3, path_arc=-30 * DEGREES)
        link.set_fill(TOOL_COLOR)
        self.play(GrowArrow(link), ShowCreation(glow))
        self.play(self.pulse(self.notebook.code, color=TOOL_COLOR), run_time=0.6)
        return VGroup(self.notebook.code, self.notebook.output), [glow, link]

    def run_read_solution(self):
        """read_solution: the software opens the exercise's solution file."""
        folder = self.folder
        item = folder.items[TUTOR_FILES.index(TUTOR_SOLUTION_FILE)]
        glow = SurroundingRectangle(item, buff=0.04).set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 2)
        self.add(glow, item)
        self.play(FadeIn(glow))
        code = VGroup(self.code_lines(TUTOR_SOLUTION)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        title = mono(TUTOR_SOLUTION_FILE, font_size=11, color=TOOL_COLOR)
        content = VGroup(title, code).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        bg = SurroundingRectangle(content, buff=0.1).round_corners(0.06)
        bg.set_fill(TRUE_WHITE, 1).set_stroke(TOOL_COLOR, 1.5)
        popup = VGroup(bg, content)
        popup.next_to(folder, UP, buff=0.15).align_to(folder, RIGHT)
        self.play(TransformFromCopy(item, popup))
        self.wait(0.5)
        return code, [glow, popup]
