from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.example_course_tutor import CourseTutorBot
from scenes.example_outputs import (
    TUTOR_CELL, TUTOR_CODE, TUTOR_FILES, TUTOR_NOTEBOOK, TUTOR_OUTPUT, WIKI_FILES,
)
from scenes.example_wiki_bot import WikiSearchBot
from scenes.overview import (
    AgenticOverview, CHAT_STROKE, STEP_FILL, STEP_STROKE, TOOL_FILL, dashed_round_rect,
    export_svg, get_icon, on_baseline, open_arrow,
)


CYAN = "#00B2D6"
MAGENTA = "#E0119D"


class OverviewFigure(AgenticOverview):
    """
    A still for a slide, from the pieces of the overview schematic. It's
    written to an SVG cropped to the middle of the frame (16:9, view_width
    wide), so the pieces come out larger than in the schematic.
    """
    view_width = FRAME_WIDTH / 2
    export_name = ""

    def construct(self):
        self.add(self.get_figure())
        self.wait()
        if self.file_writer.write_to_movie:
            self.export_cropped(Path(self.file_writer.output_directory, self.export_name))

    def export_cropped(self, path):
        export_svg(self.mobjects, path)
        w, h = self.view_width, self.view_width * 9 / 16
        lines = path.read_text().split("\n")
        lines[1] = f'     viewBox="{-w / 2} {-h / 2} {w} {h}" width="1920" height="1080">'
        lines[2] = f'  <rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" fill="{TRUE_WHITE}"/>'
        path.write_text("\n".join(lines))

    def get_header(self, title, subtitle, left, y):
        title_mob = on_baseline(title, left, y, font_size=17, weight=BOLD)
        subtitle_mob = on_baseline(
            subtitle, title_mob.get_right()[0] + 0.15, y, font_size=13, color=MUTED,
        )
        return VGroup(title_mob, subtitle_mob)

    # Windows

    def get_window(self, left, top, width, height, title, stroke=INK, code_mark=True):
        """App window as in the overview, with a title in its bar."""
        self.window_height = height
        window = self.get_software_window(width)
        body, tint, bar_line, outline, dots, mark = window
        for part in [body, bar_line, outline]:
            part.set_stroke(stroke)
        if not code_mark:
            window.remove(mark)
        window.add(text(title, font_size=9, color=MUTED).move_to(tint))
        window.move_to([left + width / 2, top - height / 2, 0])
        return window

    def get_model_column(self, x, top, tools):
        """The model, its stop rule and the programs it can use, from top to bottom."""
        llm = self.get_llm(True)
        software = self.get_software_label(["Generate until", "STOP"])
        programs = self.get_named_programs(tools)
        column = VGroup(llm, software, programs).arrange(DOWN, buff=0.1)
        column.move_to([x, top, 0], UP)
        column.llm = llm
        column.tiles = programs.tiles
        return column

    def get_named_programs(self, tools):
        """get_programs, with each program's name next to it."""
        rows = VGroup()
        tiles = VGroup()
        for icon, name in tools:
            tile = RoundedRectangle(0.2, 0.2, corner_radius=0.04)
            tile.set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 1)
            glyph = get_icon(icon, color=TOOL_COLOR, height=0.12, width=1.0).move_to(tile)
            label = text(name, font_size=self.panel_font_size, color=TOOL_COLOR)
            tiles.add(tile)
            rows.add(VGroup(VGroup(tile, glyph), label).arrange(RIGHT, buff=0.05))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        result = VGroup(self.get_panel_title("PROGRAMS", TOOL_COLOR), rows)
        result.arrange(DOWN, buff=0.05)
        result.tiles = tiles
        return result

    def get_system_prompt(self, segments, left, width):
        flow = self.get_panel_flow(width)
        for string, color in segments:
            self.add_flow_words(flow, string.split(" "), color=color)
        content = VGroup(self.get_panel_title("SYSTEM PROMPT", ACCENT), flow)
        content.arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        return self.get_panel(content, left, width, STEP_FILL, STEP_STROKE, dashed=True)

    def get_data_folder(self, name, note, files, left, top, width, height):
        """A folder the tools can reach: its name, a note, and its files."""
        bg = RoundedRectangle(width, height, corner_radius=0.09)
        bg.set_fill(PANEL_FILL, 1).set_stroke(CHAT_STROKE, 1.5)
        bg.move_to([left, top, 0], UL)
        header = VGroup(
            get_icon("folder", color=MUTED, height=0.13, width=1.0),
            mono(name, font_size=10),
            text(note, font_size=10, color=MUTED, slant=ITALIC),
        ).arrange(RIGHT, buff=0.06)
        items = VGroup(
            VGroup(doc_icon(0.13), mono(file, font_size=8)).arrange(RIGHT, buff=0.04)
            for file in files
        )
        items.arrange_in_grid(n_cols=2, h_buff=0.2, v_buff=0.07, aligned_edge=LEFT, fill_rows_first=True)
        content = VGroup(header, items).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        content.move_to(bg)
        return VGroup(bg, content)

    def get_tool_link(self, points, color=TOOL_COLOR):
        """Thin line with corners, ending in an open arrowhead."""
        points = [np.array(p, dtype=float) for p in points]
        link = VGroup(open_arrow(points[-2], points[-1], color, width=1.5))
        if len(points) > 2:
            link.add(Polyline(*points[:-1]).set_stroke(color, 1.5).set_fill(opacity=0))
        return link

    # Chat

    def get_chat_question(self, string, left, width, top):
        right = left + width
        flow = FlowText(ORIGIN, width - 0.65, font_size=self.chat_font_size, line_height=self.chat_line_height)
        flow.add_words(string.split(" "))
        bubble = self.get_bubble(flow, USER_FILL, flow.get_width() + 0.2)
        icon = get_icon("person", color=MUTED)
        bubble.move_to([right - 0.33, top, 0], UR)
        icon.move_to([right - 0.17, bubble.get_y(), 0])
        return VGroup(bubble, icon)

    def get_thoughts(self, items, left, top, width):
        """
        Dashed box with the private thoughts: running text (a string), tool
        calls (name, icon, input) and what they return (a list of lines).
        """
        buff = 0.08
        inner_width = width - 2 * buff
        content = VGroup()
        y = top - 0.04
        for n, item in enumerate(items):
            if isinstance(item, str):
                flow = FlowText(
                    [left + buff, y, 0], inner_width, font_size=self.chat_font_size - 1,
                    line_height=self.chat_line_height, slant=ITALIC,
                )
                if n == 0:
                    self.add_flow_words(flow, ["THINK"])
                self.add_flow_words(flow, item.split(" "), color=MUTED)
                content.add(flow)
                y = flow.get_bottom_y()
            elif isinstance(item, tuple):
                name, icon, tool_input = item
                call = VGroup(
                    chip("TOOL", font_size=8),
                    get_icon(icon, color=TOOL_COLOR, height=0.11, width=1.0),
                    text(name, font_size=11, color=TOOL_COLOR),
                    text(tool_input, font_size=10, color=TOOL_COLOR, slant=ITALIC),
                ).arrange(RIGHT, buff=0.05)
                pill = RoundedRectangle(inner_width, call.get_height() + 0.07, corner_radius=0.05)
                pill.set_stroke(TOOL_COLOR, 1).set_fill(TOOL_FILL, 1)
                pill.move_to([left + buff, y - 0.02, 0], UL)
                call.move_to(pill.get_left() + 0.05 * RIGHT, LEFT)
                content.add(pill, call)
                y = pill.get_bottom()[1]
            else:
                results = VGroup(text("↳ " + line, font_size=10, color=MUTED) for line in item)
                results.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
                results.move_to([left + buff + 0.04, y - 0.04, 0], UL)
                content.add(results)
                y = results.get_bottom()[1] - 0.01
        height = top - y + buff - 0.02
        rect = RoundedRectangle(width, height, corner_radius=0.09)
        rect.set_fill(TRUE_WHITE, 1).set_stroke(width=0)
        rect.move_to([left, top, 0], UL)
        border = dashed_round_rect(width, height, 0.09, FRAME_GREY).move_to(rect)
        return VGroup(rect, border, content)

    def get_chat_answer(self, string, left, width, top, cited=()):
        """The bot's bubble; the cited words are in the tools' color."""
        flow = FlowText(
            [left + 0.1, top - 0.05, 0], width - 0.18,
            font_size=self.chat_font_size, line_height=self.chat_line_height,
        )
        for word in string.split(" "):
            self.add_flow_words(flow, [word], color=TOOL_COLOR if word in cited else INK)
        return self.get_bubble(flow, PANEL_FILL, width)


class SecurityOverview(OverviewFigure):
    """
    The tool-using agent of the overview, without the system prompt: the two
    parts to secure are the LLM (cyan border) and the software around it,
    the harness (magenta border).
    """
    view_width = 4.27
    export_name = "SecurityOverview.svg"
    tools = [("web", "Search web"), ("folder", "Read files"), ("code", "Execute code")]

    def get_figure(self):
        width, height = 2.5, 1.5
        left, top = -width / 2, 0.58
        window = self.get_window(left, top, width, height, "Agent software")
        content_y = top - height / 2 - self.bar_height / 2

        llm = self.get_llm(True).move_to([left + 0.68, content_y - 0.09, 0])
        programs = self.get_named_programs(self.tools)
        programs.move_to([left + width - 0.62, content_y, 0])

        llm_border = self.get_border(llm, CYAN, buff=0.05)
        llm_tab = self.get_tab("LLM", CYAN).next_to(llm_border, UP, buff=0)
        harness_border = self.get_border(window[0], MAGENTA, buff=0.05)
        harness_tab = self.get_tab("Software / harness", MAGENTA)
        harness_tab.next_to(harness_border, UP, buff=0).align_to(harness_border, LEFT).shift(0.1 * RIGHT)

        header = self.get_header("Security overview", "Two parts to secure", left - 0.05, 1.0)
        return VGroup(header, window, llm, programs, llm_border, llm_tab, harness_border, harness_tab)

    def get_border(self, mob, color, buff):
        border = SurroundingRectangle(mob, buff=buff).round_corners(0.07)
        return border.set_fill(opacity=0).set_stroke(color, 3)

    def get_tab(self, string, color):
        label = text(string, font_size=10, color=TRUE_WHITE, weight=BOLD)
        bg = Rectangle(label.get_width() + 0.14, 0.16).round_corners(0.03)
        bg.set_fill(color, 1).set_stroke(color, 1)
        return VGroup(bg, label.move_to(bg))


class WikiChatbotFigure(OverviewFigure):
    """
    WikiSearchBot at a glance: the chat with its search and cited answer, and
    the software with the system prompt, the tool and the downloaded pages.
    """
    export_name = "WikiChatbotFigure.svg"
    left, right = -3.42, 3.42
    top, bottom = 1.5, -1.24
    chat_width = 3.3
    software_left = 0.14
    software_height = 1.6
    folder_gap = 0.42

    def get_figure(self):
        header = self.get_header(
            WikiSearchBot.example_title, WikiSearchBot.example_subtitle, self.left, 1.72,
        )
        return VGroup(header, self.get_chat(), self.get_software()).set_y(0)

    def get_chat(self):
        window = self.get_window(
            self.left, self.top, self.chat_width, self.top - self.bottom, "Wiki chat",
            stroke=CHAT_STROKE, code_mark=False,
        )
        question = self.get_chat_question(
            WikiSearchBot.question, self.left, self.chat_width, self.top - self.bar_height - 0.1,
        )
        content_left = self.left + self.bubble_left
        content_width = self.chat_width - self.bubble_left - 0.1
        thought_top = question.get_bottom()[1] - 0.1
        thoughts = self.get_thoughts(
            [
                "Check the wiki.",
                ("search_wiki_files", "folder", "<raw images>"),
                [
                    "storage.md: …save raw images on the group share…",
                    "microscopes.md: …export raw images as .czi, not .png…",
                ],
            ],
            content_left, thought_top, content_width,
        )
        answer = self.get_chat_answer(
            "ANSWER Save them on the group share, folder raw/, and never delete them "
            "(storage.md). Export them as .czi, not .png (microscopes.md). STOP",
            content_left, content_width, thoughts.get_bottom()[1] - 0.07,
            cited=("(storage.md).", "(microscopes.md)."),
        )
        icon = get_icon("robot").move_to([self.left + 0.17, thought_top - 0.09, 0])
        return VGroup(window, question, icon, thoughts, answer)

    def get_software(self):
        left, top = self.software_left, self.top
        width = self.right - left
        height = self.software_height
        window = self.get_window(left, top, width, height, "Wiki bot software")
        column_x = left + 0.56
        column = self.get_model_column(
            column_x, top - self.bar_height - 0.11, [("folder", "search_wiki_files")],
        )
        panel_left = left + 1.14
        panel_width = width - 1.14 - 0.1
        prompt = self.get_system_prompt(
            [
                ("You're a wiki search bot. You can search wiki files by saying", INK),
                ("TOOL search_wiki_files <search>.", TOOL_COLOR),
            ],
            panel_left, panel_width,
        )
        prompt.move_to([panel_left + panel_width / 2, top - height / 2 - self.bar_height / 2, 0])

        folder_top = top - height - self.folder_gap
        folder = self.get_data_folder(
            "wiki/", "pages, downloaded beforehand as markdown",
            [f["file"] for f in WIKI_FILES], left, folder_top, width, folder_top - self.bottom,
        )
        tile = column.tiles[0]
        link = self.get_tool_link([tile.get_bottom(), [tile.get_x(), folder_top, 0]])
        note = VGroup(
            text("Searches within the files; returns the file", font_size=10, color=TOOL_COLOR, slant=ITALIC),
            text("name and the text around the match", font_size=10, color=TOOL_COLOR, slant=ITALIC),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        note.move_to([tile.get_x() + 0.08, top - height - self.folder_gap / 2, 0], LEFT)
        return VGroup(link, window, column, prompt, folder, note)


class TeachingAssistantFigure(OverviewFigure):
    """
    CourseTutorBot at a glance: the tutor in JupyterLab, below the student's
    notebook, and the software with the system prompt, the two tools and the
    solutions, which students can't see.
    """
    export_name = "TeachingAssistantFigure.svg"
    left, right = -3.42, 3.42
    top, bottom = 1.5, -1.86
    lab_width = 3.3
    software_left = 0.14
    software_height = 2.15
    folder_gap = 0.4

    def get_figure(self):
        header = self.get_header(
            CourseTutorBot.example_title, CourseTutorBot.example_subtitle, self.left, 1.72,
        )
        lab, cell = self.get_lab()
        return VGroup(header, lab, self.get_software(cell))

    def get_lab(self):
        window = self.get_window(
            self.left, self.top, self.lab_width, self.top - self.bottom, f"JupyterLab · {TUTOR_NOTEBOOK}",
            stroke=CHAT_STROKE, code_mark=False,
        )
        inner_left = self.left + 0.1
        inner_right = self.left + self.lab_width - 0.1
        y = self.top - self.bar_height - 0.05

        # The student's notebook
        prompt = mono(f"[{TUTOR_CELL}]:", font_size=8, color=MUTED)
        code = VGroup(mono(line, font_size=8) for line in TUTOR_CODE)
        code.arrange(DOWN, aligned_edge=LEFT, buff=0.035)
        cell = Rectangle(inner_right - inner_left - 0.25, code.get_height() + 0.08)
        cell.set_fill(PANEL_FILL, 1).set_stroke(CHAT_STROKE, 1)
        cell.move_to([inner_right, y, 0], UR)
        code.move_to(cell.get_left() + 0.06 * RIGHT, LEFT)
        prompt.next_to(cell, LEFT, buff=0.04).align_to(cell, UP).shift(0.04 * DOWN)
        output = mono(TUTOR_OUTPUT, font_size=8).next_to(cell, DOWN, buff=0.04, aligned_edge=LEFT).shift(0.06 * RIGHT)
        divider_y = output.get_bottom()[1] - 0.05
        divider = Line([self.left, divider_y, 0], [self.left + self.lab_width, divider_y, 0])
        divider.set_stroke(CHAT_STROKE, 1)

        # The tutor below it
        content_left = self.left + self.bubble_left
        content_width = self.lab_width - self.bubble_left - 0.1
        question = self.get_chat_question(
            CourseTutorBot.question, self.left, self.lab_width, divider_y - 0.05,
        )
        thought_top = question.get_bottom()[1] - 0.06
        thoughts = self.get_thoughts(
            [
                "Look at their code.",
                ("read_code", "code", f"<{TUTOR_CELL}>"),
                "Threshold 0 is too low. Compare with the solution.",
                ("read_solution", "papers", "<3>"),
                "It uses Otsu. Hint, not the code.",
            ],
            content_left, thought_top, content_width,
        )
        answer = self.get_chat_answer(
            "ANSWER Look at your threshold: with img > 0, almost every pixel counts as "
            "foreground. Which value separates nuclei from background? STOP",
            content_left, content_width, thoughts.get_bottom()[1] - 0.05,
        )
        icon = get_icon("robot").move_to([self.left + 0.17, thought_top - 0.09, 0])
        return VGroup(window, prompt, cell, code, output, divider, question, icon, thoughts, answer), cell

    def get_software(self, cell):
        left, top = self.software_left, self.top
        width = self.right - left
        height = self.software_height
        window = self.get_window(left, top, width, height, "Tutor software")
        column = self.get_model_column(
            left + 0.53, top - self.bar_height - 0.11,
            [("code", "read_code"), ("papers", "read_solution")],
        )
        panel_left = left + 1.08
        panel_width = width - 1.08 - 0.07
        prompt = self.get_system_prompt(
            [
                ("You're the virtual course tutor of the SCF lab course for master students. Your goal "
                 "is to help students with understanding image analysis concepts, as well as Python "
                 "coding and debugging. Don't provide solutions to exercises, but instead hint students "
                 "towards the next steps towards the solution. You can use the available tools by running", INK),
                ("TOOL read_code <cell>", TOOL_COLOR),
                ("or", INK),
                ("TOOL read_solution <exercise>.", TOOL_COLOR),
            ],
            panel_left, panel_width,
        )
        prompt.move_to([panel_left + panel_width / 2, top - height / 2 - self.bar_height / 2, 0])

        folder_top = top - height - self.folder_gap
        folder = self.get_data_folder(
            "solutions/", "students can't see these", TUTOR_FILES,
            left, folder_top, width, folder_top - self.bottom,
        )
        read_code, read_solution = column.tiles
        gutter_x = (self.left + self.lab_width + left) / 2
        code_link = self.get_tool_link([
            read_code.get_left(), [gutter_x, read_code.get_y(), 0],
            [gutter_x, cell.get_y(), 0], cell.get_right(),
        ])
        solution_link = self.get_tool_link([read_solution.get_bottom(), [read_solution.get_x(), folder_top, 0]])
        note = text("Reads the exercise's solution", font_size=10, color=TOOL_COLOR, slant=ITALIC)
        note.move_to([read_solution.get_x() + 0.08, top - height - self.folder_gap / 2, 0], LEFT)
        return VGroup(code_link, solution_link, window, column, prompt, folder, note)
