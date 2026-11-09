from manim_imports_ext import *
from _2024.transformers.helpers import softmax
from _2024.transformers.chm import ShowMachineWithDials
from scenes.stills import BuildStills


class TrainingLevel1(BuildStills, ShowMachineWithDials):
    """
    3b1b's ShowMachineWithDials, up to (not including) the zoom-out to many
    more parameters: the model's behavior is set by its weights (the dials;
    also called parameters), turning them changes the predicted
    distribution, and they start out random.
    """
    def construct(self):
        # Show machine (same position as in PredictTheNextWord)
        frame = self.frame
        self.set_floor_plane("xz")
        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()

        self.clear()
        self.add(frame)
        frame.reorient(0, 0, 0, (-0.17, -0.12, 0.0), 4.50)
        self.add(blocks, llm_text, last_dials)

        # Prepare dial highlight
        last_dials.target = last_dials.generate_target()
        self.fix_dials(last_dials.target)

        small_rect = SurroundingRectangle(last_dials[0], buff=0.025)
        small_rect.set_stroke(BLUE, 2)
        big_rect = small_rect.copy().scale(4)
        big_rect.next_to(blocks, UP, buff=SMALL_BUFF, aligned_edge=LEFT + OUT)
        big_rect.shift(1.5 * RIGHT)
        big_dial = last_dials[0].copy().scale(4).set_stroke(opacity=1)
        big_dial.move_to(big_rect)
        rect_lines = VGroup(
            Line(small_rect.get_corner(UL), big_rect.get_corner(DL)),
            Line(small_rect.get_corner(UR), big_rect.get_corner(DR)),
        )
        rect_lines.set_stroke(WHITE, width=(1, 3))
        weight_label = Text("one weight", font_size=36).set_color(BLUE)
        weight_label.next_to(big_rect, RIGHT, buff=0.2)
        highlighed_parameter_group = VGroup(small_rect, rect_lines, big_rect, big_dial)

        # The label goes first, so that it never sits on top of the dials
        self.play(FadeOut(llm_text), run_time=0.6)
        last_dials.set_stroke(width=1, opacity=1)
        self.play(
            MoveToTarget(last_dials),
            FadeIn(small_rect),
        )

        # Show an example input and output
        example = self.get_example(blocks)
        in_text, in_arrow, out_arrow, bar_groups = example
        logprobs = example.logprobs
        true_probs = 100 * softmax(logprobs)
        bar_groups = self.get_output_distribution(self.words, 0.1 * logprobs, out_arrow)

        self.play(
            LaggedStart(
                ShowCreation(rect_lines, lag_ratio=0),
                TransformFromCopy(small_rect, big_rect),
                TransformFromCopy(last_dials[0], big_dial),
                FadeIn(weight_label, 0.2 * LEFT),
                FadeIn(in_text),
                GrowArrow(in_arrow),
                FadeIn(bar_groups),
                GrowArrow(out_arrow),
            ),
            frame.animate.reorient(0, 0, 0, (-0.43, 0.38, 0.0), 7.05),
            run_time=2
        )
        self.play(
            last_dials[0].animate_set_value(0.8),
            big_dial.animate_set_value(0.8),
            LaggedStart(
                (dial.animate_set_value(dial.get_random_value())
                for dial in last_dials[1:]),
                lag_ratio=1.0 / len(last_dials),
            ),
            *(
                self.bar_group_change_animation(bg, value)
                for bg, value in zip(bar_groups[:-1], true_probs)
            ),
            run_time=3
        )
        self.wait()

        # Play around tweaking the parameters, and seeing the output change
        self.play(
            LaggedStart(
                (dial.animate_set_value(0)
                for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(0),
            self.bar_group_change_animation(bar_groups[0], 50),
            self.bar_group_change_animation(bar_groups[1], 34),
            self.bar_group_change_animation(bar_groups[2], 5),
            run_time=4,
        )
        self.play(
            LaggedStart(
                (dial.animate_set_value(1)
                for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(1),
            self.bar_group_change_animation(bar_groups[0], 80),
            self.bar_group_change_animation(bar_groups[1], 5),
            self.bar_group_change_animation(bar_groups[2], 15),
            run_time=4,
        )
        self.wait()

        # Mention randomness
        random_words = Text("Weights start random")
        random_words.next_to(blocks, UP)
        random_words.set_color(RED)
        out_dots = Tex(R"...", font_size=120)
        out_dots.next_to(out_arrow, RIGHT)

        self.play(
            FadeOut(big_rect),
            FadeOut(weight_label),
            Uncreate(rect_lines, lag_ratio=0),
            FadeOut(small_rect),
            Transform(big_dial, last_dials[0])
        )
        self.play(
            Write(random_words),
            LaggedStart(
                (dial.animate_set_value(dial.get_random_value())
                for dial in last_dials),
                lag_ratio=0.5 / len(last_dials),
                run_time=2
            ),
            FadeOut(bar_groups),
        )
        self.play(Write(out_dots))
        self.wait()
        self.play(
            FadeOut(out_dots),
            FadeOut(random_words),
            FadeIn(bar_groups),
        )

        self.wait()
