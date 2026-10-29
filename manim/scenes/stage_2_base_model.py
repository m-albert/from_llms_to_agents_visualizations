from manim_imports_ext import *
from _2024.transformers.helpers import DATA_DIR
from scenes.agentic_common import *


class Stage2BaseModel(AgenticScene):
    """
    Pre-training turns the random model into one that has learned language
    patterns. In the same 10-word loop it now writes fluent text, but it
    continues the question like a web page would instead of answering it,
    and only stops because the software cuts it off.
    """
    stage_number = 2
    stage_title = "Pre-trained base model"
    stage_subtitle = "Completes text, not yet an assistant"
    trained = False  # Starts untrained, pre-training happens in the scene
    # First step: real next-word probabilities of a small base model
    # (Qwen2.5-0.5B) for the bare question; " What" is sampled, the
    # remaining words are illustrative
    first_words = ["Micro", "What", "The", "How", "A", "Are"]
    first_probs = [0.114, 0.101, 0.042, 0.033, 0.024, 0.022]
    answer_words = "What do recent papers say about PFAS and health? What".split()
    n_snippets = 14
    random_seed = 3

    def construct(self):
        self.setup_stage(show=False)
        machine, code = self.machine, self.code
        blocks = self.blocks

        weights_label = text("Random weights", font_size=22, color=MUTED)
        weights_label.next_to(machine[0], DOWN, buff=0.2)
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
        new_weights_label = text("Learned language patterns", font_size=22, color=MUTED)
        new_weights_label.move_to(weights_label)
        self.play(
            FadeOut(step_label, 0.2 * UP),
            FadeTransform(weights_label, new_weights_label),
        )

        # Same software, same question
        self.play(
            FadeIn(code.bg),
            Write(code.lines, lag_ratio=0.05),
            FadeIn(self.chat_window),
            FadeIn(self.user_bubble, 0.25 * LEFT),
            run_time=2,
        )
        self.add(code)
        counter = self.get_counter(0)
        self.add(counter)
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.3)
        self.play(FadeIn(answer_group[0]), GrowArrow(self.out_arrow))

        # First pass, with the model's real probabilities
        counter = self.update_counter(counter, 1)
        self.feed_model(VGroup(self.user_bubble), run_time=1.4)
        chart = self.show_distribution(self.first_words, self.first_probs)
        self.wait()
        index = self.first_words.index(self.answer_words[0])
        self.pick(chart, index)
        self.append_word(chart, index, flow, bubble, self.answer_words[0])

        # The rest, quickly
        self.play(code.unhighlight(), run_time=0.3)
        for n, word in enumerate(self.answer_words[1:]):
            counter = self.update_counter(counter, n + 2, animate=False)
            self.quick_word(flow, bubble, word, run_time=0.4)
        self.wait(0.5)

        # Cut off by the software, not by the model
        stop_rect = SurroundingRectangle(VGroup(code.lines[0], counter), buff=0.08)
        stop_rect.set_stroke(WARN, 2)
        cut_mark = text("...", font_size=self.answer_font_size, color=MUTED)
        cut_mark.next_to(flow[-1], RIGHT, buff=0.08, aligned_edge=DOWN)
        note = text("Continues from input prompt", font_size=20, color=MUTED, slant=ITALIC)
        note.next_to(bubble.bg, DOWN, buff=0.2).align_to(bubble.bg, LEFT)
        self.play(ShowCreation(stop_rect), FadeIn(cut_mark))
        self.play(FadeIn(note, 0.1 * DOWN))
        self.wait()

        # Why: it learned what text looks like, e.g. a page of questions
        page = self.get_faq_page()
        page.next_to(note, DOWN, buff=0.35).match_x(self.chat_window)
        self.play(FadeIn(page, 0.2 * UP), FadeOut(stop_rect))
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

    def get_counter(self, n, total=10):
        counter = mono(f"{n}/{total}", font_size=23, color=MUTED)
        counter.next_to(self.code.lines[0], RIGHT, buff=0.4)
        return counter

    def update_counter(self, counter, n, animate=True):
        new = self.get_counter(n)
        if animate:
            self.play(Transform(counter, new), run_time=0.3)
        else:
            counter.become(new)
        return counter
