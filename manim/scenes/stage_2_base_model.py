from manim_imports_ext import *
from _2024.transformers.helpers import DATA_DIR
from scenes.agentic_common import *


class Stage2BaseModel(AgenticScene):
    """
    Pre-training turns the random model into one that has learned language
    patterns. In the same 10-word loop it now writes fluent text, but it
    continues the question like a web page would instead of answering it.
    It could end the text (STOP, the end-of-text word, is one of its
    options), but that is very unlikely here, so only the software's
    10-word rule stops it.
    """
    stage_number = 2
    stage_title = "Pre-trained base model"
    stage_subtitle = "Completes text, not yet an assistant"
    trained = False  # Starts untrained, pre-training happens in the scene
    show_bars = True
    # Real next-word probabilities of a small base model (Qwen2.5-0.5B).
    # First step, for the bare question:
    first_words = ["Micro", "What", "The", "How", "A", "Are"]
    first_probs = [0.114, 0.101, 0.042, 0.033, 0.024, 0.022]
    # Last step, after "... PFAS and health?"; STOP is its end-of-text
    # token, at rank 38
    last_words = ["What", "How", "And", "Are", "STOP"]
    last_probs = [0.578, 0.069, 0.025, 0.024, 0.0017]
    last_pct_labels = ["58%", "7%", "3%", "2%", "0.17%"]
    answer_words = "What do recent papers say about PFAS and health? What".split()
    n_snippets = 14
    random_seed = 3

    def construct(self):
        self.setup_stage()
        machine, blocks = self.machine, self.blocks

        weights_label = self.get_weights_label("Random weights")
        self.add(self.title_group, self.software_window, machine[:2], weights_label)
        self.wait()

        # Pre-training: lots of text into the model
        step_label = VGroup(
            text("Pre-training", font_size=34, color=ACCENT, weight=BOLD),
            text("Learn by predicting the next word", font_size=24, color=MUTED),
        ).arrange(DOWN, buff=0.15)
        step_label.move_to([(self.chat_left + self.chat_right) / 2, 2.2, 0])
        snippets = self.get_snippets()
        self.play(FadeIn(step_label, 0.2 * DOWN))
        self.stills_every(1.5)
        self.play(
            LaggedStart(
                (Succession(
                    FadeIn(snippet, 0.2 * DOWN),
                    snippet.animate.scale(0.2).move_to(machine[0]).set_opacity(0),
                )
                for snippet in snippets),
                lag_ratio=0.15,
            ),
            self.randomize_dials(run_time=5, lag_factor=3),
            blocks.animate.set_fill(TRAINED_FILL),
            run_time=6,
        )
        self.stills_every(None)
        self.remove(snippets)
        self.play(
            FadeOut(step_label, 0.2 * UP),
            FadeTransform(weights_label, self.get_weights_label("Learned language patterns")),
        )

        # Same software, same question
        self.play(
            self.build_loop(),
            FadeIn(self.chat_window),
            FadeIn(self.user_bubble, 0.25 * LEFT),
        )
        self.send_question()
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.3)
        self.play(FadeIn(answer_group[0]))

        # First pass, with the model's real probabilities
        self.update_counter(1)
        self.feed_model(run_time=1.4)
        chart = self.show_distribution(self.first_words, self.first_probs)
        self.wait()
        index = self.first_words.index(self.answer_words[0])
        self.pick(chart, index)
        self.append_word(chart, index, flow, bubble, self.answer_words[0])

        # The middle, quickly
        for n, word in enumerate(self.answer_words[1:-1]):
            self.update_counter(n + 2, animate=False)
            self.emit_word(word, flow, bubble, run_time=0.4)

        # Last pass: ending the text is an option, just a very unlikely one
        self.update_counter(10)
        self.feed_model(run_time=1.0)
        chart = self.show_distribution(
            self.last_words, self.last_probs,
            pct_labels=self.last_pct_labels, n_main=len(self.last_words) - 1,
        )
        stop_row = chart.rows[-1]
        stop_rect = SurroundingRectangle(stop_row, buff=0.05).set_stroke(WARN, 2)
        stop_note = VGroup(
            text("STOP (end of text) is just", font_size=17, color=WARN),
            text("another word it can pick", font_size=17, color=WARN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        stop_note.next_to(stop_rect, RIGHT, buff=0.15)
        self.play(ShowCreation(stop_rect), FadeIn(stop_note))
        self.wait(2)
        self.play(FadeOut(stop_rect), FadeOut(stop_note))
        index = self.last_words.index(self.answer_words[-1])
        self.pick(chart, index)
        self.append_word(chart, index, flow, bubble, self.answer_words[-1])
        self.wait(0.5)

        # Cut off by the software, not by the model
        cut_mark = text("...", font_size=self.answer_font_size, color=MUTED)
        cut_mark.next_to(flow[-1], RIGHT, buff=0.08, aligned_edge=DOWN)
        note = text("Continues from input prompt", font_size=20, color=MUTED, slant=ITALIC)
        note.next_to(bubble.bg, DOWN, buff=0.2).align_to(bubble.bg, LEFT)
        rule_rect = self.flash_rule()
        self.play(FadeIn(cut_mark))
        self.play(FadeIn(note, 0.1 * DOWN))
        self.wait()

        # Why: it learned what text looks like, e.g. a page of questions
        page = self.get_faq_page()
        page.next_to(note, DOWN, buff=0.35).match_x(self.chat_window)
        self.play(FadeIn(page, 0.2 * UP), FadeOut(rule_rect))
        self.wait(2)

        takeaway = text("Fluent text, but it continues the prompt instead of answering", font_size=24)
        takeaway.move_to(3.72 * DOWN)
        self.play(FadeIn(takeaway, 0.2 * UP))
        self.wait(3)

    def get_snippets(self):
        lines = Path(DATA_DIR, "pile_of_text.txt").read_text().splitlines()
        random.shuffle(lines)
        snippets = VGroup()
        for line in lines[:self.n_snippets]:
            flow = FlowText(ORIGIN, 3.6, font_size=20)
            flow.add_words(line.split(" "), color=MUTED)
            snippets.add(flow)
        for snippet in snippets:
            snippet.move_to([
                random.uniform(self.chat_left + 2.0, self.chat_right - 2.0),
                random.uniform(-3.0, 1.2),
                0
            ])
        return snippets

    def get_faq_page(self):
        lines = VGroup(
            text("Typical web text:", font_size=20, color=MUTED, weight=BOLD),
            text("FAQ: plastics and health", font_size=20, color=MUTED),
            text("- What do recent papers say about microplastics...", font_size=18, color=MUTED),
            text("- What do recent papers say about PFAS...", font_size=18, color=MUTED),
            text("- What about...", font_size=18, color=MUTED),
        )
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        bg = SurroundingRectangle(lines, buff=0.15)
        bg.set_stroke(FRAME_GREY, 1).set_fill(TRUE_WHITE, 1)
        bg.round_corners(0.08)
        return VGroup(bg, lines)
