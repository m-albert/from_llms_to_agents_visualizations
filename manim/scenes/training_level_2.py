from manim_imports_ext import *
from _2024.transformers.helpers import DATA_DIR
from _2024.transformers.chm import ShowSingleTrainingExample
from scenes.stills import BuildStills
from scenes.agentic_common import TRAINED_FILL


class TrainingLevel2(BuildStills, ShowSingleTrainingExample):
    """
    3b1b's ShowSingleTrainingExample: take a known sentence, let the model
    predict its last word, flag how the probabilities should change, then
    send that signal backwards through the layers (reverse flash) while every
    dial gets nudged. Ends with a few seconds of fast iterations over many
    more snippets, each nudging the dials, while the model turns from grey
    (untrained) to blue (trained), as in Stage2BaseModel.
    """
    def construct(self):
        # Add state from before
        frame = self.frame
        self.set_floor_plane("xz")

        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()
        self.fix_dials(last_dials)
        example = self.get_example(blocks)
        in_text, in_arrow, out_arrow, bar_groups = example

        self.add(blocks, last_dials)

        # Show example up top
        parts = ("It was the best of times it was the", "worst")
        sentence = Text(" ".join(parts))
        start = sentence[parts[0]][0]
        end = sentence[parts[1]][0]
        sentence.set_width(10)
        sentence.next_to(blocks, UP, buff=1.5)

        start_rect = SurroundingRectangle(start)
        start_rect.set_stroke(BLUE, 2)
        start_rect.set_fill(BLUE, 0.2)
        end_rect = SurroundingRectangle(end)
        end_rect.match_height(start_rect, stretch=True).match_y(start_rect)
        end_rect.set_stroke(YELLOW, 2)
        end_rect.set_fill(YELLOW, 0.2)
        arrow = Arrow(start_rect.get_top(), end_rect.get_top(), path_arc=-90 * DEGREES, thickness=5)
        arrow.set_fill(border_width=1)

        frame.reorient(0, 0, 0, (-0.36, 0.97, 0.0), 7.52)
        self.play(FadeIn(sentence, UP))
        self.play(
            LaggedStartMap(DrawBorderThenFill, VGroup(start_rect, end_rect)),
            FadeIn(arrow),
        )
        self.remove(last_dials)
        self.play(LaggedStart(
            AnimationGroup(
                TransformFromCopy(start, in_text[:-1]),
                TransformFromCopy(end_rect, in_text[-1]),
                FadeIn(in_arrow)
            ),
            self.get_block_flash(blocks, TEAL),
            Animation(last_dials),
            GrowArrow(out_arrow),
            LaggedStartMap(GrowFromPoint, bar_groups, point=out_arrow.get_start()),
            lag_ratio=0.3
        ))
        self.wait()

        # Flag bad prediction
        out_rects = VGroup(
            SurroundingRectangle(bg)
            for bg in bar_groups[:2]
        )
        out_rects.set_stroke(RED, 3)
        annotations = VGroup(
            Tex(tex, font_size=60).next_to(rect, LEFT, buff=SMALL_BUFF)
            for rect, tex in zip(out_rects, [R"\uparrow", R"\downarrow"])
        )
        annotations.set_color(RED)

        self.play(
            FadeTransform(end_rect.copy(), out_rects[0]),
            Write(annotations[0]),
        )
        self.wait()
        self.play(
            FadeTransform(*out_rects),
            FadeTransform(*annotations),
        )
        self.wait()
        self.play(
            FadeOut(out_rects[1]),
            FadeOut(annotations[1]),
        )

        # Backpropagation: the error signal runs from the output back
        # through the layers, and every dial gets nudged
        self.play(
            Succession(*(
                self.get_block_flash(blocks, RED, reverse=True)
                for _ in range(3)
            )),
            LaggedStart(
                (dial.animate_set_value(dial.get_random_value())
                for dial in last_dials),
                lag_ratio=1.0 / len(last_dials),
            ),
            LaggedStart(
                (FlashAround(dial, stroke_width=2, color=YELLOW, time_width=1, buff=0.025) for dial in last_dials),
                lag_ratio=1.0 / len(last_dials),
            ),
            self.bar_group_change_animation(bar_groups[0], 70),
            self.bar_group_change_animation(bar_groups[1], 20),
            self.bar_group_change_animation(bar_groups[2], 8),
            run_time=6
        )
        self.wait()

        # Fast iterations: many more snippets, each one nudging the dials
        top_example = VGroup(sentence, start_rect, end_rect, arrow)
        # Each iteration a bit slower, ending at a third of the starting rate
        run_times = np.geomspace(*self.fast_example_time_range, self.n_fast_examples)
        untrained_fill = blocks[0].get_fill_color()
        for n, run_time in enumerate(run_times):
            # The old example is gone before the new one appears: no overlapping text
            out_span = (0, 0.3 * run_time)
            in_span = (0.3 * run_time, 0.6 * run_time)
            blocks.set_fill(interpolate_color(untrained_fill, TRAINED_FILL, (n + 1) / len(run_times)))
            new_top, new_in_text, new_bars = self.get_fast_example(top_example, in_arrow, out_arrow)
            self.play(
                FadeOut(top_example, time_span=out_span),
                FadeOut(in_text, time_span=out_span),
                FadeOut(bar_groups, time_span=out_span),
                FadeIn(new_top, time_span=in_span),
                FadeIn(new_in_text, time_span=in_span),
                FadeIn(new_bars, time_span=in_span),
                self.get_block_flash(blocks, RED, reverse=True, run_time=run_time),
                LaggedStart(
                    (dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials),
                    lag_ratio=0.5 / len(last_dials),
                ),
                run_time=run_time,
            )
            top_example, in_text, bar_groups = new_top, new_in_text, new_bars
        self.wait()

    n_fast_examples = 10
    fast_example_time_range = (0.5, 1.5)  # seconds for the first and last iteration
    fast_window_sizes = (6, 9)

    def get_fast_example(self, prev_top, in_arrow, out_arrow):
        """
        A random window of words from the training text (not necessarily a
        sentence start), laid out like the first example, with the model's
        prediction for its last word.
        """
        if not hasattr(self, "snippets"):
            text = Path(DATA_DIR, "pile_of_text.txt").read_text()
            self.snippets = [line.split() for line in text.splitlines()]
        size = random.randint(*self.fast_window_sizes)
        words = random.choice([words for words in self.snippets if len(words) >= size])
        index = random.randint(0, len(words) - size)
        context, target = words[index:index + size - 1], words[index + size - 1]

        # Sentence up top, context in blue and target in yellow
        context_str = " ".join(context)
        sentence = Text(context_str + " " + target)
        sentence.match_height(prev_top[0])
        sentence.set_max_width(12)
        sentence.move_to(prev_top[0])
        start_rect = SurroundingRectangle(sentence[context_str][0])
        start_rect.set_stroke(BLUE, 2)
        start_rect.set_fill(BLUE, 0.2)
        end_rect = SurroundingRectangle(sentence[target][-1])
        end_rect.match_height(start_rect, stretch=True).match_y(start_rect)
        end_rect.set_stroke(YELLOW, 2)
        end_rect.set_fill(YELLOW, 0.2)
        arrow = Arrow(start_rect.get_top(), end_rect.get_top(), path_arc=-90 * DEGREES, thickness=5)
        arrow.set_fill(border_width=1)
        new_top = VGroup(sentence, start_rect, end_rect, arrow)

        # Model input, wrapped like "It was the best\nof times it was\nthe _"
        # (the blank gets stretched 4x, so it counts as 4 characters)
        lines = [[]]
        for word in [*context, "_"]:
            line_len = len(" ".join(lines[-1] + [word])) + (3 if word == "_" else 0)
            if lines[-1] and line_len > 16:
                lines.append([])
            lines[-1].append(word)
        in_text = Text("\n".join(map(" ".join, lines)), alignment="LEFT")
        in_text[-1].stretch(4, 0, about_edge=LEFT)
        in_text.set_max_width(3.4)
        in_text.next_to(in_arrow, LEFT)

        # Model output, with the true next word marked if it is on the list
        pred_words, probs = self.predict_next_token(context_str)
        pred_words, probs = pred_words[:len(self.words)], np.array(probs[:len(self.words)])
        bar_groups = self.get_distribution(pred_words, probs, self.machine, width_100p=1.0)
        bar_groups.next_to(out_arrow, RIGHT)
        stripped = [w.strip().lower() for w in pred_words]
        if target.lower().strip(".,;:!?\"'") in stripped:
            index = stripped.index(target.lower().strip(".,;:!?\"'"))
            highlight = SurroundingRectangle(bar_groups[index], buff=0.025)
            highlight.set_stroke(YELLOW, 2)
            highlight.set_fill(YELLOW, 0.25)
            bar_groups.add_to_back(highlight)

        return new_top, in_text, bar_groups

    def get_block_flash(self, blocks, color, reverse=False, run_time=None):
        # Upstream's forward-pass flash; reversed, it runs output -> input
        ordered = blocks[::-1] if reverse else blocks
        return LaggedStart(
            (
                block.animate.set_color(
                    block.get_color() if block is blocks[-1] else color
                ).set_anim_args(rate_func=there_and_back)
                for block in ordered
            ),
            group=blocks,
            lag_ratio=0.1,
            run_time=run_time or (2 if reverse else 1),
        )
