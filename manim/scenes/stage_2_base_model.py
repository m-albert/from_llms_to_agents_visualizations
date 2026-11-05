from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.stage_outputs import STAGE2


class Stage2BaseModel(AgenticScene):
    """
    Pre-training turns the random model into one that has learned language
    patterns. Two training texts in detail: the model guesses the hidden
    next word, the real word is shown, and the weights are adjusted so that
    it becomes a bit more likely. Then trillions of words more. In the same
    10-word loop it now writes fluent text, but it continues the input like
    a web page would: it adds another question instead of answering. Words
    and bars are scripted (scenes/stage_outputs.py).
    """
    stage_number = 2
    stage_title = "Pre-trained base model"
    stage_subtitle = "Completes text, not yet an assistant"
    trained = False  # Starts untrained, pre-training happens in the scene
    # (text, real next word, guesses before, after adjusting the weights), in %
    training_texts = [
        (
            "Microplastics have been detected in human", "blood",
            [("cars", 4), ("blood", 3), ("the", 3), ("sing", 2), ("tissue", 2)],
            [("cars", 3), ("blood", 9), ("the", 3), ("sing", 1), ("tissue", 3)],
        ),
        (
            "Plastic bottles slowly break down into tiny", "particles",
            [("piano", 4), ("the", 3), ("particles", 3), ("seven", 2), ("pieces", 2)],
            [("piano", 2), ("the", 3), ("particles", 9), ("seven", 1), ("pieces", 3)],
        ),
    ]
    random_seed = 3

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label("Random weights")
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)
        self.wait()
        self.pre_training()
        self.play(FadeTransform(weights_label, self.get_weights_label("Learned language patterns")))
        self.inference()

    def inference(self):
        # Same software, same question
        self.play(self.build_software(), FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(answer_group[0]))
        self.open_turn()
        for n, record in enumerate(STAGE2):
            self.run_pass(n, self.distribution_from_record(record), (flow, bubble))
        self.wait(0.5)

        # Cut off by the software, not by the model
        cut_mark = text("...", font_size=self.chat_font_size, color=MUTED)
        cut_mark.next_to(flow[-1], RIGHT, buff=0.08, aligned_edge=DOWN)
        self.play(FadeIn(cut_mark))
        self.flash_rule()
        self.wait(2)

    # Pre-training

    def pre_training(self):
        header = self.training_header("Pre-training", "Learn by predicting the next word")
        self.play(FadeIn(header, 0.2 * DOWN))
        label = self.get_part_label("Texts from books, web, code, papers")
        self.play(FadeIn(label, 0.1 * DOWN))
        for n, example in enumerate(self.training_texts):
            self.training_example(*example, speed=1 if n == 0 else 1.4)
        self.many_examples(
            "text", ["Then many, many more", "≈ 10,000,000,000,000 words", "(trillions)"],
            run_time=5, extra_anims=[self.blocks.animate.set_fill(TRAINED_FILL)],
        )
        self.play(FadeOut(header, 0.2 * UP), FadeOut(label, 0.2 * UP))

    def training_example(self, string, target, before, after, speed=1):
        """
        One training step: the model guesses the next word of a text, the
        real word is shown, and the weights are adjusted to make it more likely.
        """
        flow = FlowText(ORIGIN, 3.4, font_size=20)
        context = flow.add_words(string.split(" "))
        slot = flow.next_word(target)
        box = SurroundingRectangle(slot, buff=0.05).round_corners(0.05)
        box.set_stroke(FRAME_GREY, 1.5).set_fill(PANEL_FILL, 1)
        question = text("?", font_size=20, color=MUTED).move_to(box)
        card = self.place_card(VGroup(flow, box, question), "Training text")

        # The model reads the text and guesses the next word
        self.play(FadeIn(card, 0.2 * UP), run_time=1 / speed)
        words = [word for word, p in before]
        chart = self.get_training_chart(words, [p for word, p in before])
        guess_label = text("Model's guess", font_size=17, color=MUTED)
        guess_label.next_to(chart, UP, buff=0.2)
        point = VGroup(VectorizedPoint(self.machine[0].get_left()))
        self.play(
            LaggedStart(
                TransformFromCopy(context, point, lag_ratio=0.01, remover=True),
                self.block_flash(),
                lag_ratio=0.3,
            ),
            run_time=1.2 / speed,
        )
        self.play(
            LaggedStart((FadeIn(row, 0.1 * RIGHT) for row in chart), lag_ratio=0.05),
            FadeIn(guess_label),
            run_time=0.7 / speed,
        )
        self.wait(0.5 / speed)

        # The real next word
        real = text(target, font_size=20, color=TOOL_COLOR, weight=BOLD).move_to(box)
        row = chart.rows[words.index(target)]
        rect = SurroundingRectangle(row, buff=0.04).set_stroke(TOOL_COLOR, 2)
        self.play(FadeOut(question), FadeTransform(box, real), run_time=0.6 / speed)
        self.play(ShowCreation(rect), run_time=0.6 / speed)
        self.wait(0.5 / speed)

        # Adjust the weights: the real word becomes a bit more likely
        note = text(f"Adjust weights: “{target}” a bit more likely", font_size=17, color=ACCENT)
        note.next_to(card, DOWN, buff=0.2)
        new_chart = self.get_training_chart(words, [p for word, p in after])
        self.play(
            FadeIn(note, 0.1 * DOWN),
            self.randomize_dials(run_time=1.5 / speed, lag_factor=1),
            Transform(chart, new_chart),
            rect.animate.surround(new_chart.rows[words.index(target)], buff=0.04),
            run_time=1.5 / speed,
        )
        self.wait(1 / speed)
        card.add(real)
        self.play(
            FadeOut(VGroup(chart, rect, guess_label, note)),
            self.absorb(card),
            run_time=1 / speed,
        )

    def get_training_chart(self, words, percents):
        return self.get_chart(
            words, [p / 100 for p in percents], [f"{p}%" for p in percents],
            n_main=len(words), scale_max=0.1,
        )


class Stage2BaseModelInference(Stage2BaseModel):
    """Only the inference part of Stage2BaseModel: starts with the pre-trained model."""
    trained = True

    def construct(self):
        self.setup_stage()
        self.add(self.title_group, self.software_window, self.machine[:2], self.get_weights_label("Learned language patterns"))
        self.wait(0.5)
        self.inference()
