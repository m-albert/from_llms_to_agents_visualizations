from manim_imports_ext import *
from _2024.transformers.chm import PredictTheNextWord
from scenes.stills import BuildStills


class NextWordPrediction(BuildStills, PredictTheNextWord):
    """
    Opening of 3b1b's PredictTheNextWord: text goes into the model, it gives
    one word, then the full probability distribution over next words.
    """
    seed_text = "The Single Cell Unit at D-BSSE is a"
    show_machine_intro = False  # True: start with the 3D build-up of the model

    def construct(self):
        # Setup machine
        text_mob, next_word_line, machine = self.init_text_and_machine()
        machine.move_to(ORIGIN)
        machine[1].set_backstroke(BLACK, 3)

        text_group = VGroup(text_mob, next_word_line)
        text_group.scale(1.5)
        text_group.match_x(machine[0]).to_edge(UP)

        in_arrow = Arrow(text_group, machine[0].get_top(), thickness=5)
        frame = self.frame
        self.set_floor_plane("xz")
        blocks = machine[0]
        llm_text = machine[1]
        flat_dials, last_dials = self.get_machine_dials(blocks)

        self.clear()
        if self.show_machine_intro:
            self.introduce_machine(blocks, llm_text, flat_dials, last_dials)
        else:
            self.add(blocks, llm_text, last_dials)
            self.save_still()
            self.wait()
        blocks[-1].add(last_dials)

        # Text into the machine
        self.play(
            FadeIn(text_group, UP),
            GrowFromCenter(in_arrow),
            run_time=2
        )

        # Single word prediction
        out_arrow = Vector(1.5 * RIGHT, thickness=5)
        out_arrow.next_to(machine[0][-1], RIGHT)
        words, probs = self.predict_next_token(self.cur_str)
        prediction = Text(words[0].strip(), font_size=72)
        prediction.next_to(out_arrow, RIGHT)

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
        self.wait()
        machine.replace_submobject(2, out_arrow)

        # Probability distribution
        self.play(FadeOut(prediction, DOWN))
        self.animate_prediction_ouptut(machine, self.cur_str)
        self.wait(2)

    def get_distribution(self, words, probs, machine, **kwargs):
        # The predictions here are spread thin (top word ~5%), so stretch the
        # bars until the longest is readable; the % labels stay true
        kwargs.setdefault("width_100p", max(1.8, 1.5 / max(probs)))
        return super().get_distribution(words, probs, machine, **kwargs)

    def introduce_machine(self, blocks, llm_text, flat_dials, last_dials):
        frame = self.frame
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
        self.play(frame.animate.to_default_state(), run_time=2)
