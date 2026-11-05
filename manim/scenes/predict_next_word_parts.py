from manim_imports_ext import *
from _2024.transformers.chm import PredictTheNextWord
from scenes.stills import BuildStills


class PredictNextWordBase(BuildStills, PredictTheNextWord):
    """
    3b1b's PredictTheNextWord cut into parts for separate slides (1a, 1b, 2, 3).
    Each part starts on the exact frame the previous one ends on.
    """

    def setup_stage(self):
        # Same objects, in the same order, as PredictTheNextWord.construct, so
        # that the random dials come out identical in all parts
        text_mob, next_word_line, machine = self.init_text_and_machine()
        machine.move_to(ORIGIN)
        machine[1].set_backstroke(BLACK, 3)

        text_group = VGroup(text_mob, next_word_line)
        text_group.scale(1.5)
        text_group.match_x(machine[0]).to_edge(UP)

        in_arrow = Arrow(text_group, machine[0].get_top(), thickness=5)
        self.set_floor_plane("xz")
        flat_dials, last_dials = self.get_machine_dials(machine[0])

        out_arrow = Vector(1.5 * RIGHT, thickness=5)
        out_arrow.next_to(machine[0][-1], RIGHT)

        self.clear()
        return text_mob, next_word_line, machine, in_arrow, out_arrow, flat_dials, last_dials

    def add_stage(self, text_mob, next_word_line, machine, in_arrow, out_arrow, last_dials):
        # The state at the end of the machine's introduction in part 1
        machine[0][-1].add(last_dials)
        self.add(machine[0], machine[1])
        self.add(text_mob, next_word_line, in_arrow, out_arrow)
        machine.replace_submobject(2, out_arrow)

    def get_prediction(self, out_arrow):
        prediction = Text("France", font_size=72)
        prediction.next_to(out_arrow, RIGHT)
        return prediction


class PredictNextWordPart1a(PredictNextWordBase):
    """The machine flies in, and the camera settles on its final position."""

    def construct(self):
        text_mob, next_word_line, machine, in_arrow, out_arrow, flat_dials, last_dials = self.setup_stage()

        frame = self.frame
        blocks = machine[0]
        llm_text = machine[1]
        block_outlines = blocks.copy()
        block_outlines.set_fill(opacity=0)
        block_outlines.set_stroke(GREY_B, 2)
        block_outlines.insert_n_curves(20)

        frame.reorient(-31, -4, -5, (-0.24, -0.26, -0.06), 3)
        self.play(
            FadeIn(blocks, shift=0.0, lag_ratio=0.01),
            LaggedStartMap(VShowPassingFlash, VGroup(*block_outlines.family_members_with_points()), time_width=2.0, lag_ratio=0.01, remover=True),
            LaggedStartMap(VFadeInThenOut, flat_dials, lag_ratio=0.001, remover=True),
            Write(llm_text, time_span=(2, 4), stroke_color=WHITE),
            FadeIn(last_dials, time_span=(4, 5)),
            frame.animate.reorient(0, 0, 0, (-0.17, -0.12, 0.0), 4.50),
            run_time=6,
        )
        self.add(llm_text)  # Above the dials, as in the following parts
        self.play(frame.animate.to_default_state(), run_time=3)
        self.wait()


class PredictNextWordPart1b(PredictNextWordBase):
    """The sentence appears, and the machine predicts one word: France."""

    def construct(self):
        text_mob, next_word_line, machine, in_arrow, out_arrow, flat_dials, last_dials = self.setup_stage()
        text_group = VGroup(text_mob, next_word_line)

        # The machine as part 1a leaves it
        machine[0][-1].add(last_dials)
        self.add(machine[0], machine[1])
        self.wait(0.5)

        self.play(
            FadeIn(text_group, UP),
            GrowFromCenter(in_arrow),
            run_time=2
        )

        # Single word prediction
        prediction = self.get_prediction(out_arrow)
        self.animate_text_input(
            text_mob, machine,
            position_text_over_machine=False,
        )
        self.play(
            LaggedStart(
                (TransformFromCopy(VectorizedPoint(machine.get_right()), letter)
                for letter in prediction),
                lag_ratio=0.05,
            ),
            GrowArrow(out_arrow)
        )
        self.wait(2)


class PredictNextWordPart2(PredictNextWordBase):
    """The word France gets replaced by the full probability distribution."""

    def construct(self):
        text_mob, next_word_line, machine, in_arrow, out_arrow, flat_dials, last_dials = self.setup_stage()
        self.add_stage(text_mob, next_word_line, machine, in_arrow, out_arrow, last_dials)
        prediction = self.get_prediction(out_arrow)
        self.add(prediction)
        self.wait()

        self.play(FadeOut(prediction, DOWN))
        self.animate_prediction_ouptut(machine, self.cur_str)
        self.wait(2)


class PredictNextWordPart3(PredictNextWordBase):
    """
    The sentence is continued one word at a time. For the first words, the
    whole text so far visibly goes back into the model; after that the
    sentence is just completed quickly.

    The bars are the model's real probabilities, but the picked words are
    scripted so that the sentence makes sense, and all of them are among the
    bars shown.
    """
    picked_words = [" France", " that", " is", " known", " for", " its", " beautiful", " architecture", "."]
    n_shown_inputs = 3
    sentence_font_size = 40

    def construct(self):
        text_mob, next_word_line, machine, in_arrow, out_arrow, flat_dials, last_dials = self.setup_stage()
        self.add_stage(text_mob, next_word_line, machine, in_arrow, out_arrow, last_dials)

        words, probs = self.predict_next_token(self.cur_str)
        bar_groups = self.get_distribution(words, probs, machine)
        self.add(bar_groups)
        self.wait(0.5)

        # Make room for the whole sentence (and for bars close to 100%)
        self.font_size = self.sentence_font_size
        self.line_len = 1000
        self.text_top = text_mob.get_top()
        self.text_x = in_arrow.get_x()
        new_text_mob = self.get_sentence(self.cur_str)
        self.play(
            Transform(text_mob, new_text_mob),
            Transform(next_word_line, self.get_next_word_line(new_text_mob)),
            self.frame.animate.reorient(0, 0, 0, (0.7, -0.01, 0.0), 8.52),
        )

        # Words picked with the whole text going back into the model
        for word in self.picked_words[:self.n_shown_inputs]:
            highlight = self.pick_word(bar_groups, word, run_time=0.8)
            text_mob = self.add_word_to_text(bar_groups, highlight, word, text_mob, next_word_line, run_time=0.8)
            rect = self.feed_whole_text(text_mob, machine, in_arrow)
            bar_groups = self.animate_prediction_ouptut(machine, self.cur_str)
            self.play(FadeOut(rect), run_time=0.3)

        # The rest, quickly
        for word in self.picked_words[self.n_shown_inputs:-1]:
            highlight = self.pick_word(bar_groups, word, run_time=0.25, n_flickers=2)
            text_mob = self.add_word_to_text(
                bar_groups, highlight, word, text_mob, next_word_line,
                run_time=0.25,
            )
            words, probs = self.predict_next_token(self.cur_str)
            bar_groups = self.get_distribution(words, probs, machine)
            self.play(FadeIn(bar_groups), run_time=0.15)

        # The finished sentence, next to the probabilities of its last word
        word = self.picked_words[-1]
        highlight = self.pick_word(bar_groups, word, run_time=0.25, n_flickers=2)
        text_mob = self.add_word_to_text(
            bar_groups, highlight, word, text_mob, next_word_line,
            run_time=0.25,
            keep_bars=True,
        )
        self.play(
            FadeOut(next_word_line),
            text_mob[len(self.seed_text.replace(" ", "")):].animate.set_color(WHITE),
        )
        self.wait(3)

    def get_sentence(self, text):
        # Stays centered above the arrow as it grows
        sentence = self.string_to_mob(text)
        sentence.move_to(self.text_top, UP).set_x(self.text_x)
        sentence[:len(self.seed_text.replace(" ", ""))].set_color(self.seed_text_color)
        return sentence

    def pick_word(self, bar_groups, word, run_time=1, n_flickers=8):
        # Flicker over the bars like animate_random_sample, landing on the given word
        bars = bar_groups[:-1]
        index = [group[0].get_text() for group in bars].index(word)
        widths = [group[1].get_width() for group in bars]
        rng = random.Random(self.cur_str)
        flickers = rng.choices(range(len(bars)), widths, k=n_flickers)

        highlight = SurroundingRectangle(bars[0], buff=0.025)
        highlight.set_stroke(YELLOW, 2)
        highlight.set_fill(YELLOW, 0.25)

        def update_highlight(rect, alpha):
            step = int(alpha * (n_flickers + 1))
            rect.surround(bars[flickers[step] if step < n_flickers else index], buff=0.025)
            rect.stretch(1.1, 0)

        self.play(
            UpdateFromAlphaFunc(highlight, update_highlight),
            Animation(bar_groups),
            run_time=run_time,
        )
        self.wait(0.25 * run_time)
        return highlight

    def add_word_to_text(self, bar_groups, highlight, word, text_mob, next_word_line, run_time=1, keep_bars=False):
        new_str = self.cur_str + word
        new_text_mob = self.get_sentence(new_str)
        n_new_chars = len(word.strip())
        target = new_text_mob[-n_new_chars - 1:-1]
        target.set_color(YELLOW)

        # The sentence moves aside for the new word, which is highlighted in
        # place of the previous one
        old_chars = text_mob[:-1]
        bar_group = next(group for group in bar_groups[:-1] if group[0].get_text() == word)
        self.play(
            Transform(old_chars, new_text_mob[:-n_new_chars - 1]),
            FadeTransform(bar_group[0].copy(), target),
            Transform(next_word_line, self.get_next_word_line(new_text_mob)),
            run_time=run_time,
        )
        self.remove(text_mob, old_chars, target)
        self.add(new_text_mob)
        if not keep_bars:
            self.play(FadeOut(VGroup(highlight, bar_groups)), run_time=0.5 * run_time)

        self.cur_str = new_str
        return new_text_mob

    def feed_whole_text(self, text_mob, machine, in_arrow):
        # A boxed copy of everything so far travels down the arrow into the model
        blocks = machine[0]
        whole_text = text_mob[:-1]
        rect = SurroundingRectangle(whole_text, buff=0.15)
        rect.set_stroke(TEAL, 3)
        rect.set_fill(TEAL, 0.1)

        self.add(rect, text_mob)
        self.play(ShowCreation(rect), run_time=0.6)
        self.wait(0.3)

        mover = VGroup(rect, whole_text).copy()
        target = mover.copy()
        target.set_width(1.5)
        target.move_to(blocks.get_top())
        target.set_opacity(0)
        self.play(LaggedStart(
            AnimationGroup(
                Transform(mover, target, remover=True),
                in_arrow.animate.set_color(TEAL).set_anim_args(rate_func=there_and_back),
                run_time=1.5,
            ),
            LaggedStart(
                (
                    block.animate.set_color(
                        block.get_color() if block is blocks[-1] else TEAL
                    ).set_anim_args(rate_func=there_and_back)
                    for block in blocks
                ),
                lag_ratio=0.1,
                run_time=1
            ),
            Animation(machine[1:]),
            lag_ratio=0.6
        ))
        return rect
