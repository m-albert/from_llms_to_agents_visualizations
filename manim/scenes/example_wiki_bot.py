import textwrap

from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.example_common import ExampleAgentScene, TOOL_FILL
from scenes.example_outputs import WIKI_ANSWER, WIKI_CALL, WIKI_FILES, WIKI_MATCHES, WIKI_SEARCH
from scenes.stage_outputs import words


class WikiSearchBot(ExampleAgentScene):
    """
    A chatbot for searching a wiki. The wiki pages were downloaded
    beforehand as markdown files. Its one tool, search_wiki_files, searches
    these files and returns, for each match, the file name and the text
    around the match. The system prompt says how to call it; the model
    searches while thinking and answers from the matches, citing the pages
    (file names). Words, bars and the wiki are scripted (scenes/example_outputs.py).
    """
    example_title = "Wiki search bot"
    example_subtitle = "Searches the wiki files, cites the pages"
    software_title = "Wiki bot software"
    chat_title = "Wiki chat"
    question = "Where do I save raw images from the microscope?"
    system_prompt = [
        ("You're a wiki search bot. You can search wiki files by saying", INK),
        ("TOOL search_wiki_files <search>.", TOOL_COLOR),
    ]
    tool_names = ["search_wiki_files"]
    tool_glyphs = {"search_wiki_files": "search"}
    input_font_size = 14
    chat_font_size = 18
    random_seed = 7

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label(self.weights_text)
        tools = self.get_tools()
        folder = self.get_folder("wiki/", "pages as markdown files", [f["file"] for f in WIKI_FILES])
        self.folder = folder
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)
        self.play(self.build_software())
        self.highlight_system_prompt()

        # Downloaded beforehand: the wiki's pages become markdown files
        self.play(FadeIn(tools, shift=0.2 * UP), FadeIn(folder.bg), FadeIn(folder.header))
        self.download_wiki(folder)
        self.name_tools(tools, [self.system_block.segments[1][1]])
        self.wait()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))

        # The model thinks, then searches
        icon, flow, bubble = self.get_thought(self.user_bubble.get_bottom()[1] - 0.2)
        self.play(FadeIn(icon), FadeIn(bubble))
        self.open_turn()
        self.in_call = False
        n = self.run_records(WIKI_CALL, colors=self.call_color)
        n_call_words = len(WIKI_CALL) - words(WIKI_CALL).index("TOOL")
        result = []
        for match in WIKI_MATCHES:
            result.append(f"{match['file']}: {match['snippet']}")
        snippets = VGroup(self.get_snippet_card(match) for match in WIKI_MATCHES)
        snippets.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        self.call_tool(n_call_words, tools.tiles[0], self.run_search, result, snippets, keep=True)

        # It answers from the matches
        self.run_records(WIKI_ANSWER, n0=n, colors=self.thought_color)
        self.flash_rule()

        # The citations point to the files the search returned
        flow = self.chat[0]
        answer = words(WIKI_ANSWER)[:-1]  # ANSWER ... (as in the chat; STOP isn't)
        starts = [n for n, word in enumerate(answer) if word.startswith("(")]
        for start, snippet in zip(starts, snippets):
            citation = flow[start]
            highlights, underlines = self.highlight_words([citation], color=TOOL_COLOR, fill=TOOL_FILL)
            link = DashedLine(citation.get_top(), snippet.get_bottom(), dash_length=0.05).set_stroke(TOOL_COLOR, 1.5)
            self.add(highlights, flow)
            self.play(FadeIn(highlights), ShowCreation(underlines), ShowCreation(link), run_time=0.8)
            self.play(FadeOut(link), run_time=0.3)

        warning = warning_label(["Only as good as the", "downloaded wiki pages"], font_size=17)
        warning.next_to(self.chat[1].bg, DOWN, buff=0.25).align_to(self.chat[1].bg, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait(3)

    def download_wiki(self, folder):
        """The wiki website's pages, downloaded as markdown files (before any chat)."""
        center_x = (self.chat_left + self.chat_right) / 2
        site = app_window(3.5, 2.6, title="Lab wiki (website)", title_font_size=16, bar_height=0.34)
        site.move_to([center_x, 0.9, 0])
        pages = VGroup(
            VGroup(doc_icon(0.3), text(f["page"], font_size=18)).arrange(RIGHT, buff=0.12)
            for f in WIKI_FILES
        )
        pages.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        pages.move_to(site.body).shift(0.17 * DOWN)
        note = text("Downloaded beforehand,\nas markdown files", font_size=18, color=MUTED, slant=ITALIC)
        note.next_to(site, DOWN, buff=0.35)
        arrow = Arrow(note.get_bottom() + 0.05 * DOWN, note.get_bottom() + 0.9 * DOWN, thickness=3).set_fill(MUTED)
        self.play(FadeIn(site), LaggedStartMap(FadeIn, pages, shift=0.1 * DOWN, lag_ratio=0.15))
        self.play(FadeIn(note), GrowArrow(arrow))
        self.play(
            LaggedStart((TransformFromCopy(page, item) for page, item in zip(pages, folder.items)), lag_ratio=0.2),
            run_time=2,
        )
        self.wait()
        self.play(FadeOut(VGroup(site, pages, note, arrow)))

    def run_search(self):
        """
        search_wiki_files goes through every file; where the search text
        appears, it returns the file name and the text around it.
        """
        folder = self.folder
        query = mono(f"“{WIKI_SEARCH}”", font_size=13, color=TOOL_COLOR)
        query.next_to(folder.bg, UP, buff=0.1).align_to(folder.bg, LEFT)
        self.play(FadeIn(query, 0.1 * DOWN))
        matched = [f["file"] for f in WIKI_MATCHES]
        is_match = [f["file"] in matched for f in WIKI_FILES]
        scan = SurroundingRectangle(folder.items[0], buff=0.04).set_stroke(TOOL_COLOR, 2)
        self.play(ShowCreation(scan), run_time=0.3)
        rects = VGroup()
        for item, match in zip(folder.items, is_match):
            self.play(scan.animate.surround(item, buff=0.04), run_time=0.3)
            if match:
                rect = scan.copy().set_fill(TOOL_FILL, 1)
                self.add(rect, item)
                rects.add(rect)
                self.play(self.pulse(item[1], color=TOOL_COLOR), run_time=0.3)
            else:
                self.play(item.animate.set_opacity(0.35), run_time=0.2)
        self.remove(scan)
        hits = VGroup(item for item, match in zip(folder.items, is_match) if match)
        count = text(f"{len(hits)} matches", font_size=14, color=TOOL_COLOR, weight=BOLD)
        count.next_to(query, RIGHT, buff=0.2)
        self.play(FadeIn(count))
        dimmed = [item for item, match in zip(folder.items, is_match) if not match]
        cleanup = [query, count, rects]
        self.play(*(item.animate.set_opacity(1) for item in dimmed), run_time=0.3)
        return hits, cleanup

    def get_snippet_card(self, match):
        """One search match as the chat shows it: the file name and the text around the match."""
        font_size = self.chat_font_size - 4
        # Wrap the text, but keep the search text on one line
        nbsp = WIKI_SEARCH.replace(" ", "\u00a0")
        wrapped = textwrap.wrap(match["snippet"].replace(WIKI_SEARCH, nbsp), 32)
        lines = [
            text(line.replace(nbsp, WIKI_SEARCH), font_size=font_size, t2c={WIKI_SEARCH: TOOL_COLOR})
            for line in wrapped
        ]
        return self.get_result_card(match["file"], lines, font_size=font_size)
