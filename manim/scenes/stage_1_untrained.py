from manim_imports_ext import *
from scenes.agentic_common import *


class Stage1Untrained(AgenticScene):
    """
    An untrained model inside the software loop. The input is the
    conversation; with random weights every word is about equally likely,
    so after 10 passes the answer is ten random words.
    """
    stage_number = 1
    stage_title = "Untrained model"
    stage_subtitle = "Random output: nothing learned yet"
    trained = False
    answer_words = "orbit lamp the seven glass of whenever banana north quietly".split()
    random_seed = 1

    def construct(self):
        self.setup_stage()
        machine = self.machine

        self.play(FadeIn(self.title_group, lag_ratio=0.1))
        self.play(FadeIn(self.software_window), FadeIn(machine[:2]))
        weights_label = self.get_weights_label("Random weights")
        self.play(self.randomize_dials(run_time=2), FadeIn(weights_label, 0.2 * DOWN))
        self.play(self.build_software())
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.wait()

        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(answer_group[0]))
        self.open_turn()
        for n, word in enumerate(self.answer_words):
            # After the first three words in detail, the other seven in about 3 seconds
            self.run_pass(n, self.uniform_distribution(word), (flow, bubble), fast_time=0.25)
        self.wait(0.5)
        self.flash_rule()
        verdict = verdict_label("none", ["No answer:", "just random words"], font_size=18)
        verdict.next_to(bubble.bg, DOWN, buff=0.3).align_to(bubble.bg, LEFT)
        self.play(FadeIn(verdict, 0.2 * UP))
        self.wait(2)

    def uniform_distribution(self, chosen, n=6):
        pool = (
            "orbit lamp the seven glass of whenever banana north quietly "
            "piano sudden river elbow nine ticket purple asleep under cable "
            "mango thus vertical honey quantum seldom brick"
        ).split()
        words = random.sample([w for w in pool if w != chosen], n - 1)
        words.insert(random.randint(0, n - 1), chosen)
        probs = list(1 + 0.08 * np.random.uniform(-1, 1, n))
        return words, probs, ["0.0007%"] * n, n, words.index(chosen)
