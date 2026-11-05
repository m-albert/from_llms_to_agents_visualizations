from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.example_common import ExampleAgentScene, TOOL_FILL
from scenes.example_outputs import (
    PRIVACY_ANSWER, PRIVACY_CALL, PRIVACY_CONTENT, PRIVACY_FILE, PRIVACY_FILES,
    PRIVACY_REACHABLE, PRIVACY_SENSITIVE,
)
from scenes.stage_outputs import words


def lock_icon(height=0.24, color=INK):
    body = RoundedRectangle(1.0, 0.8, corner_radius=0.12).set_fill(color, 1).set_stroke(width=0)
    shackle = Arc(start_angle=0, angle=PI, radius=0.32).set_stroke(color, 10)
    shackle.next_to(body, UP, buff=0)
    shackle.add(Line(shackle.get_start(), shackle.get_start() + 0.12 * DOWN).set_stroke(color, 10))
    shackle.add(Line(shackle.get_end(), shackle.get_end() + 0.12 * DOWN).set_stroke(color, 10))
    hole = Dot(radius=0.09).set_fill(TRUE_WHITE, 1).move_to(body)
    return VGroup(shackle, body, hole).set_height(height)


def cloud_icon(height=0.22, color=MUTED):
    puffs = VGroup(
        Circle(radius=0.3).shift(0.35 * LEFT),
        Circle(radius=0.42).shift(0.05 * UP),
        Circle(radius=0.3).shift(0.4 * RIGHT),
        Rectangle(1.1, 0.4).shift(0.1 * DOWN),
    ).set_fill(color, 1).set_stroke(width=0)
    return puffs.set_height(height)


def server_icon(height=0.22, color=TOOL_COLOR):
    units = VGroup(RoundedRectangle(1.0, 0.28, corner_radius=0.06) for _ in range(3))
    units.arrange(DOWN, buff=0.06).set_fill(color, 1).set_stroke(width=0)
    leds = VGroup(Dot(radius=0.04).move_to(unit.get_right() + 0.15 * LEFT) for unit in units)
    leds.set_fill(TRUE_WHITE, 1)
    return VGroup(units, leds).set_height(height)


class PrivacyDataFlow(ExampleAgentScene):
    """
    Privacy and data security, with the agent layout: the model runs at a
    provider (dashed boundary), the software, files and chat on your side.
    Every pass sends the whole input across the boundary, including what
    the tools read (here a file with a donor's name and unpublished
    results), and the provider may keep it (logs). The answer leaves the
    donor out, but the data was sent many times. The tool can reach every
    file in its folder. Options at the end: check the terms, limit what the
    tools can read, or run the model locally. Numbered captions below the
    windows say what to look at. Words and data are scripted
    (scenes/example_outputs.py).
    """
    example_title = "Where does the data go?"
    example_subtitle = "Privacy and data security with agents"
    software_title = "Lab assistant software"
    chat_title = "Chat"
    question = f"Summarize {PRIVACY_FILE} for my report."
    system_prompt = [
        ("You're a lab assistant. You can read files in lab_data/ by saying", INK),
        ("TOOL read_files <file>.", TOOL_COLOR),
    ]
    tool_names = ["read_files"]
    tool_glyphs = {"read_files": "files"}
    input_font_size = 14
    chat_font_size = 18
    # Room for the captions below the windows
    window_bottom = -3.25
    input_bottom = -3.1
    random_seed = 9

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label(self.weights_text)
        tools = self.get_tools()
        folder = self.get_folder("lab_data/", "your files", PRIVACY_FILES)
        folder.set_max_width(self.window_right - 0.15 - (self.rule_badge.get_right()[0] + 0.2))
        folder.move_to([self.window_right - 0.15, self.tools_y(), 0], RIGHT)
        self.folder = folder
        boundary = self.get_boundary()
        logs = self.get_logs()
        self.n_logged = 0
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)

        # The model runs at a provider; everything else is on your side
        self.play(ShowCreation(boundary.box), FadeIn(boundary.label))
        self.caption(1, "The model runs at a provider (cloud API); the software, files and chat are on your side")
        self.play(self.build_software(), FadeIn(boundary.lock))
        self.play(FadeIn(tools, shift=0.2 * UP), FadeIn(folder), FadeIn(logs))
        self.name_tools(tools, [self.system_block.segments[1][1]])
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))

        # Every pass sends the whole input across
        self.caption(2, "Every pass sends the whole input: system prompt, chat and tool results. The provider may keep it")
        icon, flow, bubble = self.get_thought(self.user_bubble.get_bottom()[1] - 0.2)
        self.play(FadeIn(icon), FadeIn(bubble))
        self.open_turn()
        self.in_call = False
        n = self.run_records(PRIVACY_CALL, colors=self.call_color)

        # The tool reads a file with personal and unpublished data...
        card = self.get_result_card(f"Read {PRIVACY_FILE}", [], icon=doc_icon(0.24, color=TOOL_COLOR))
        result = [f"{PRIVACY_FILE}: {PRIVACY_CONTENT}"]
        n_call_words = len(PRIVACY_CALL) - words(PRIVACY_CALL).index("TOOL")
        result_mobs = self.call_tool(n_call_words, tools.tiles[0], self.run_read_file, result, card, keep=True)
        result_words = PRIVACY_FILE.split(" ") + PRIVACY_CONTENT.split(" ")
        sensitive = VGroup(mob for mob, word in zip(result_mobs[1:], result_words[1:]) if word in PRIVACY_SENSITIVE)
        highlights, underlines = self.highlight_words(sensitive)
        self.add(highlights, self.input_convo)
        self.caption(3, "The file's content is now part of the input, so it is sent with every following pass")
        self.play(FadeIn(highlights), ShowCreation(underlines))
        self.wait()

        # ...and leaves the donor out of the answer
        self.run_records(PRIVACY_ANSWER, n0=n, colors=self.thought_color)
        self.flash_rule()
        answer_rect = SurroundingRectangle(self.chat[1].bg, buff=0.04).round_corners(0.15).set_stroke(ACCENT, 2)
        self.caption(4, f"The answer leaves out the donor, but the provider received the name {self.n_logged - self.first_sensitive} times")
        self.play(ShowCreation(answer_rect), self.pulse(logs.counter, color=WARN), self.pulse(logs.title, color=WARN))
        self.wait(2)

        # The tool can read everything in its folder
        reach = VGroup(item for item, file in zip(folder.items, PRIVACY_FILES) if file in PRIVACY_REACHABLE)
        reach_rects = VGroup(SurroundingRectangle(item, buff=0.04).set_fill(WARN_FILL, 1).set_stroke(WARN, 2) for item in reach)
        self.add(reach_rects, reach)
        self.caption(5, "The tool can read every file in lab_data/, also donors.csv and api_keys.txt: limit what tools can reach")
        self.play(FadeIn(reach_rects), FadeOut(answer_rect))
        self.wait(2)

        # Options: check the provider's terms, or keep the model on your side
        self.caption(6, "Check the provider's terms (storage, training on your data, location) and what is allowed to leave")
        self.play(*(self.pulse(part, color=WARN) for part in [boundary.label[1]]), run_time=1.2)
        self.wait(1.5)
        local = self.get_boundary(local=True)
        self.caption(7, "For sensitive data: a local model, on your institution's server. The input never leaves your side")
        self.play(
            Transform(boundary.box, local.box),
            FadeTransform(boundary.label, local.label),
            FadeTransform(logs.title, logs.local_title),
            FadeOut(highlights), FadeOut(underlines), FadeOut(reach_rects),
            run_time=1.5,
        )
        self.feed_model()
        self.wait(3)

    # The provider's side

    def tools_y(self):
        return (-1.7 + self.window_bottom) / 2

    def get_rule_badge(self):
        # Under the boundary, between the tool and its folder: the stop rule is the software's
        badge = super().get_rule_badge()
        badge.move_to([self.input_right + 1.35, self.tools_y(), 0], LEFT)
        return badge

    def get_boundary(self, local=False):
        left = self.input_right + 0.28
        right = self.window_right - 0.12
        top = window_content_top(self.software_window, 0.08)
        bottom = -1.6
        rect = RoundedRectangle(right - left, top - bottom, corner_radius=0.12)
        rect.move_to([left, top, 0], UL)
        color = TOOL_COLOR if local else WARN
        rect.set_fill(opacity=0).set_stroke(color, 2.5)
        box = DashedVMobject(rect, num_dashes=90)
        if local:
            label = VGroup(server_icon(0.24), text("Local model: your institution's server", font_size=17, color=TOOL_COLOR, weight=BOLD))
        else:
            label = VGroup(cloud_icon(0.22, color=WARN), text("Model provider (cloud API)", font_size=17, color=WARN, weight=BOLD))
        label.arrange(RIGHT, buff=0.1)
        label.move_to(rect.get_corner(UL) + [0.15, -0.12, 0], UL)
        # The input crosses the boundary on its way to the model (encrypted in transit)
        lock = lock_icon(0.26)
        lock.move_to([left, self.arrows[0].get_y() + 0.3, 0])
        boundary = VGroup(box, label, lock)
        boundary.box = box
        boundary.label = label
        boundary.lock = lock
        return boundary

    def get_logs(self):
        title = text("Provider logs", font_size=16, color=WARN, weight=BOLD)
        local_title = text("Your logs", font_size=16, color=TOOL_COLOR, weight=BOLD)
        self.log_counter = Integer(0, font_size=16).set_color(MUTED)
        unit = text("inputs stored", font_size=16, color=MUTED)
        counter = VGroup(self.log_counter, unit).arrange(RIGHT, buff=0.08)
        unit.add_updater(lambda m: m.next_to(self.log_counter, RIGHT, buff=0.08))
        header = VGroup(title, counter).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        header.move_to([self.machine[0].get_left()[0] - 0.1, -0.95, 0], LEFT)
        local_title.move_to(title, LEFT)
        self.log_stack_corner = header.get_corner(UR) + [0.3, 0.05, 0]
        self.log_stack = VGroup()
        logs = VGroup(header, self.log_stack)
        logs.title = title
        logs.local_title = local_title
        logs.counter = counter
        return logs

    def log_tile(self, k):
        tile = self.get_mini_card("text")
        k = min(k, 8)
        tile.move_to(self.log_stack_corner + [0.06 * k, -0.04 * k, 0], UL)
        return tile

    def log_input(self, animate):
        """The provider stores what it received."""
        self.n_logged += 1
        tile = self.log_tile(self.n_logged - 1)
        update = ChangeDecimalToValue(self.log_counter, self.n_logged)
        if animate:
            self.play(TransformFromCopy(self.input_card.bg, tile), update, run_time=0.6)
        else:
            self.add(tile)
            self.log_counter.set_value(self.n_logged)
        self.log_stack.add(tile)

    def feed_model(self, run_time=1.2):
        super().feed_model(run_time)
        if hasattr(self, "log_stack"):
            self.log_input(animate=True)

    def run_pass(self, n, distribution, *args, **kwargs):
        if n >= self.n_detailed:
            self.log_input(animate=False)
        return super().run_pass(n, distribution, *args, **kwargs)

    def call_tool(self, *args, **kwargs):
        result = super().call_tool(*args, **kwargs)
        # From the next pass on, the file is in what the provider receives
        self.first_sensitive = self.n_logged
        return result

    def run_read_file(self):
        folder = self.folder
        item = folder.items[PRIVACY_FILES.index(PRIVACY_FILE)]
        glow = SurroundingRectangle(item, buff=0.04).set_fill(TOOL_FILL, 1).set_stroke(TOOL_COLOR, 2)
        self.add(glow, item)
        self.play(FadeIn(glow), self.pulse(item[1], color=TOOL_COLOR))
        return item, [glow]

    # Captions

    def caption(self, number, string):
        badge = VGroup(
            Circle(radius=0.17).set_fill(ACCENT, 1).set_stroke(width=0),
            text(str(number), font_size=18, color=TRUE_WHITE, weight=BOLD),
        )
        badge[1].move_to(badge[0])
        line = text(string, font_size=21)
        group = VGroup(badge, line).arrange(RIGHT, buff=0.15)
        group.set_max_width(13.6)
        group.move_to([0, -3.68, 0])
        old = getattr(self, "caption_mob", None)
        anims = [FadeIn(group, 0.1 * UP)]
        if old is not None:
            anims.append(FadeOut(old, 0.1 * UP))
        self.play(*anims, run_time=0.6)
        self.caption_mob = group
