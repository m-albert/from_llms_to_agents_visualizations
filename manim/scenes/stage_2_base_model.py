from manim_imports_ext import *
from _2024.transformers.helpers import DATA_DIR
from scenes.agentic_common import *


class Stage2BaseModel(AgenticScene):
    """
    Pre-training turns the random model into one that has learned language
    patterns. In the same 10-word loop it now writes fluent text, but it
    continues the input like a web page would: it repeats the question.
    Bars and words are the real outputs of a small base model
    (Qwen2.5-0.5B); in the first pass its second choice, "What", is picked,
    afterwards always its most likely word.
    """
    stage_number = 2
    stage_title = "Pre-trained base model"
    stage_subtitle = "Completes text, not yet an assistant"
    trained = False  # Starts untrained, pre-training happens in the scene
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
            text("Pre-training", font_size=32, color=ACCENT, weight=BOLD),
            text("Learn by predicting the next word", font_size=20, color=MUTED),
        ).arrange(DOWN, buff=0.12)
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
        self.play(self.build_software(), FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(answer_group[0]))
        self.open_turn()
        for n, record in enumerate(DISTRIBUTIONS["stage2"]):
            self.run_pass(n, self.distribution_from_record(record), (flow, bubble))
        self.wait(0.5)

        # Cut off by the software, not by the model
        cut_mark = text("...", font_size=self.chat_font_size, color=MUTED)
        cut_mark.next_to(flow[-1], RIGHT, buff=0.08, aligned_edge=DOWN)
        self.play(FadeIn(cut_mark))
        self.flash_rule()
        self.wait(2)

    def get_snippets(self):
        lines = Path(DATA_DIR, "pile_of_text.txt").read_text().splitlines()
        random.shuffle(lines)
        snippets = VGroup()
        for line in lines[:self.n_snippets]:
            flow = FlowText(ORIGIN, 3.2, font_size=18)
            flow.add_words(line.split(" "), color=MUTED)
            snippets.add(flow)
        for snippet in snippets:
            snippet.move_to([
                random.uniform(self.chat_left + 1.7, self.chat_right - 1.7),
                random.uniform(-3.0, 1.2),
                0
            ])
        return snippets
