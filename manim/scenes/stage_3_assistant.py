from manim_imports_ext import *
from scenes.agentic_common import *


class Stage3Assistant(AgenticScene):
    """
    Post-training (example conversations, feedback, special words) turns the
    base model into an assistant. The software formats the chat as one text
    with STOP after each turn and now loops until the model writes STOP.
    The answer is fluent and helpful-looking, but one claim is invented:
    it comes from patterns in the weights, not from any source.
    """
    stage_number = 3
    stage_title = "AI assistant"
    stage_subtitle = "Helpful answers, but may hallucinate"
    code_lines = [
        "text = format(chat)",
        "repeat until word is STOP:  # e.g. <|im_end|>",
        "    probabilities = model(text)",
        "    word = pick(probabilities)",
        "    text = text + word",
    ]
    model_line, pick_line, append_line = 2, 3, 4
    # The generated answer; probabilities in the detailed steps are illustrative
    answer_steps = [
        ("detail", "Studies", ["Studies", "Recent", "Microplastics", "Research", "There", "The"], [0.31, 0.22, 0.18, 0.09, 0.04, 0.03]),
        ("quick", "suggest microplastics may be linked to inflammation. A landmark study"),
        ("detail", "proved", ["proved", "showed", "found", "suggested", "linked", "demonstrated"], [0.38, 0.27, 0.14, 0.09, 0.04, 0.03]),
        ("quick", "direct harm in humans."),
        ("detail", "STOP", ["STOP", "The", "However,", "This", "More", "In"], [0.93, 0.02, 0.01, 0.01, 0.01, 0.01]),
    ]
    claim = "A landmark study proved direct harm in humans."
    random_seed = 4

    def construct(self):
        self.setup_stage(show=False)
        machine, code = self.machine, self.code
        old_code = CodePanel(AgenticScene.code_lines, width=self.code_width, font_size=23, line_buff=0.24)
        old_code.move_to(code, UL)

        weights_label = text("Learned language patterns", font_size=22, color=MUTED)
        weights_label.next_to(machine[0], DOWN, buff=0.2)
        self.add(self.title_group, self.software_window, machine[:2], weights_label, old_code)
        self.wait()

        # Post-training: example conversations and feedback
        header = VGroup(
            text("Post-training", font_size=34, color=ACCENT, weight=BOLD),
            text("Answer helpfully, then stop", font_size=24, color=MUTED),
        ).arrange(DOWN, buff=0.15)
        center_x = (self.chat_left + self.chat_right) / 2
        header.move_to([center_x, 2.2, 0])
        example = self.get_example_card()
        example.move_to([center_x, 0.4, 0])
        feedback = self.get_feedback_card()
        feedback.next_to(example, DOWN, buff=0.35)

        self.play(FadeIn(header, 0.2 * DOWN))
        self.play(FadeIn(example, 0.2 * UP))
        self.wait()
        self.play(FadeIn(feedback, 0.2 * UP))
        self.wait()
        self.stills_every(1.0)
        self.play(
            LaggedStart(
                (card.animate.scale(0.1).move_to(machine[0]).set_opacity(0)
                for card in [example, feedback]),
                lag_ratio=0.3,
            ),
            self.randomize_dials(run_time=3, lag_factor=1),
            self.block_flash(run_time=3),
            run_time=3,
        )
        self.stills_every(None)
        self.remove(example, feedback)
        new_weights_label = text("+ Assistant behavior", font_size=22, color=MUTED)
        new_weights_label.move_to(weights_label)
        self.play(
            FadeOut(header, 0.2 * UP),
            FadeTransform(weights_label, new_weights_label),
        )

        # New loop: stop when the model says STOP
        self.play(FadeTransform(old_code, code), run_time=1.5)
        stop_rect = SurroundingRectangle(code.lines[1], buff=0.06).set_stroke(WARN, 2)
        self.play(ShowCreation(stop_rect))
        self.play(FadeOut(stop_rect))

        # Chat; underneath, the model reads one plain text
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.wait()
        doc, doc_title = self.get_model_view()
        self.play(
            code.highlight_line(0),
            FadeOut(self.user_bubble),
            FadeTransform(self.chat_window.title, doc_title),
        )
        self.play(FadeIn(doc, lag_ratio=0.05))
        self.wait(2)
        self.play(
            FadeOut(doc),
            FadeTransform(doc_title, self.chat_window.title),
            FadeIn(self.user_bubble),
            code.unhighlight(),
        )

        # Generate the answer
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.3)
        self.play(FadeIn(answer_group[0]), GrowArrow(self.out_arrow))
        source = VGroup(self.user_bubble, bubble)
        for step in self.answer_steps:
            if step[0] == "detail":
                _, word, words, probs = step
                self.feed_model(source, run_time=1.2)
                chart = self.show_distribution(words, probs)
                self.pick(chart, words.index(word), run_time=0.8)
                self.append_word(chart, words.index(word), flow, bubble, word, run_time=0.7)
                if word == "STOP":
                    end_rect = SurroundingRectangle(code.lines[1], buff=0.06).set_stroke(WARN, 2)
                    self.play(code.highlight_line(1), ShowCreation(end_rect))
                    self.play(FadeOut(end_rect), code.unhighlight())
            else:
                self.play(code.unhighlight(), run_time=0.2)
                for word in step[1].split(" "):
                    self.quick_word(flow, bubble, word, run_time=0.3)
        self.wait()

        # The hallucinated claim
        claim_words = self.find_words(flow, self.claim.split(" "))
        highlights = VGroup(
            SurroundingRectangle(word, buff=0.04).set_fill(WARN_FILL, 1).set_stroke(width=0)
            for word in claim_words
        )
        underlines = VGroup(
            DashedLine(word.get_corner(DL), word.get_corner(DR), dash_length=0.05).shift(0.05 * DOWN)
            for word in claim_words
        ).set_stroke(WARN, 2)
        self.add(highlights, flow)
        self.play(FadeIn(highlights), ShowCreation(underlines))
        self.wait()

        # Where it comes from: the weights, not a source
        memory_arrow = CurvedArrow(
            bubble.bg.get_left() + 0.1 * LEFT + (claim_words.get_y() - bubble.bg.get_y()) * UP,
            machine[0].get_right() + 0.15 * RIGHT + 0.45 * DOWN,
            angle=40 * DEGREES,
        )
        memory_arrow.set_color(WARN)
        memory_label = text("From memory: learned patterns", font_size=24, color=WARN)
        memory_label.next_to(memory_arrow.pfp(0.5), DOWN, buff=0.25)
        self.play(ShowCreation(memory_arrow), FadeIn(memory_label))
        self.wait()

        notes = VGroup(
            text("Every word was a likely next word", font_size=20, color=MUTED),
            text("No source was looked up or checked", font_size=20, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        notes.next_to(bubble.bg, DOWN, buff=0.3).align_to(bubble.bg, LEFT)
        warning = warning_label(["Plausible, but from memory", "and potentially hallucinated"], font_size=24)
        warning.next_to(notes, DOWN, buff=0.35).align_to(notes, LEFT)
        self.play(FadeIn(notes, lag_ratio=0.5, run_time=2))
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait()

        takeaway = text("Post-training teaches the format and when to STOP, not what is true", font_size=24)
        takeaway.move_to(3.72 * DOWN)
        self.play(
            FadeIn(takeaway, 0.2 * UP),
            FadeOut(memory_arrow),
            FadeOut(memory_label),
        )
        self.wait(3)

    def get_example_card(self):
        lines = VGroup()
        for speaker, string in [("User:", "How far away is the Moon?"), ("Assistant:", "About 384,000 km.")]:
            flow = FlowText(ORIGIN, 4.4, font_size=22)
            flow.add_word(speaker, color=MUTED)
            flow.add_words(string.split(" "))
            flow.add_word("STOP")
            lines.add(flow)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        title = text("Example conversation", font_size=20, color=MUTED, weight=BOLD)
        title.next_to(lines, UP, buff=0.2, aligned_edge=LEFT)
        content = VGroup(title, lines)
        bg = SurroundingRectangle(content, buff=0.2).round_corners(0.1)
        bg.set_stroke(FRAME_GREY, 1).set_fill(TRUE_WHITE, 1)
        return VGroup(bg, content)

    def get_feedback_card(self):
        rows = VGroup()
        for mark, color, string in [
            (R"\checkmark", TOOL_COLOR, "Clear, helpful answer"),
            (R"\times", RED_E, "Rambling, keeps going"),
        ]:
            symbol = Tex(mark, font_size=32).set_color(color)
            label = text(string, font_size=22)
            rows.add(VGroup(symbol, label).arrange(RIGHT, buff=0.2))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        title = text("Human feedback", font_size=20, color=MUTED, weight=BOLD)
        title.next_to(rows, UP, buff=0.2, aligned_edge=LEFT)
        content = VGroup(title, rows)
        bg = SurroundingRectangle(content, buff=0.2).round_corners(0.1)
        bg.set_stroke(FRAME_GREY, 1).set_fill(TRUE_WHITE, 1)
        return VGroup(bg, content)

    def get_model_view(self):
        """The chat as the model reads it: one text, special words included."""
        top = window_content_top(self.chat_window, 0.3)
        user = FlowText([self.chat_left + 0.3, top, 0], self.chat_right - self.chat_left - 0.6, font_size=24)
        user.add_word("User:", color=MUTED)
        user.add_words(self.question.split(" "))
        user.add_word("STOP")
        assistant = FlowText([self.chat_left + 0.3, user.get_bottom_y() - 0.2, 0], 4.6, font_size=24)
        assistant.add_word("Assistant:", color=MUTED)
        doc_title = text("What the model reads", font_size=18, color=MUTED)
        doc_title.move_to(self.chat_window.title)
        return VGroup(user, assistant), doc_title

    def find_words(self, flow, words):
        """The last run of mobs in flow matching the given words."""
        n = len(words)
        return VGroup(*flow[len(flow) - n - 1:len(flow) - 1])
