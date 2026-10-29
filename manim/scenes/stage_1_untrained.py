from manim_imports_ext import *
from scenes.agentic_common import *


class Stage1Untrained(AgenticScene):
    """
    An untrained model inside the software loop: the loop asks it for
    next-word probabilities ten times, but with random weights every word is
    about equally likely, so the output is ten random words.
    """
    stage_number = 1
    stage_title = "Untrained model"
    stage_subtitle = "Random output: nothing learned yet"
    trained = False
    show_bars = True
    answer_words = "orbit lamp the seven glass of whenever banana north quietly".split()
    vocab_size_note = "All ~150,000 words about equally likely"
    random_seed = 1

    def construct(self):
        self.setup_stage()
        machine = self.machine

        # The pieces: software with a model inside, and a chat
        self.play(FadeIn(self.title_group, lag_ratio=0.1))
        self.play(FadeIn(self.software_window), FadeIn(machine[:2]))
        weights_label = self.get_weights_label("Random weights")
        self.play(
            self.randomize_dials(run_time=2),
            FadeIn(weights_label, 0.2 * DOWN),
        )
        self.play(self.build_loop())
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.send_question()
        self.wait()

        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.3)
        self.play(FadeIn(answer_group[0]))

        # First two passes, slowly
        for n, (word, run_time) in enumerate([(self.answer_words[0], 1.0), (self.answer_words[1], 0.6)]):
            self.update_counter(n + 1)
            self.feed_model(run_time=1.4 * run_time)
            words = self.random_vocab(word)
            probs = 1 + 0.08 * np.random.uniform(-1, 1, len(words))
            chart = self.show_distribution(
                words, probs,
                pct_labels=["0.0007%"] * len(words),
                run_time=run_time,
            )
            if n == 0:
                note = VGroup(
                    text("All ~150,000 words", font_size=17, color=MUTED),
                    text("about equally likely", font_size=17, color=MUTED),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
                note.move_to([self.return_arrow[0].get_x() + 0.25, -0.5, 0], LEFT)
                self.play(FadeIn(note, 0.1 * DOWN))
                self.wait()
                self.play(FadeOut(note))
            self.pick(chart, words.index(word), run_time=run_time)
            self.append_word(chart, words.index(word), flow, bubble, word, run_time=run_time)

        # The rest, quickly
        for n, word in enumerate(self.answer_words[2:]):
            self.update_counter(n + 3, animate=False)
            self.emit_word(word, flow, bubble, run_time=0.4)
        self.wait(0.5)

        # The software stops after 10 words
        note = text("10 random words", font_size=20, color=MUTED, slant=ITALIC)
        note.next_to(bubble.bg, DOWN, buff=0.2).align_to(bubble.bg, LEFT)
        rect = self.flash_rule()
        self.play(FadeIn(note, 0.1 * DOWN))
        self.wait()

        # Takeaway
        takeaway = text("The software runs the loop; the model only gives probabilities", font_size=24)
        takeaway.move_to(3.72 * DOWN)
        self.play(FadeOut(rect), FadeIn(takeaway, 0.2 * UP))
        self.wait(3)

    def random_vocab(self, chosen, n=6):
        pool = (
            "orbit lamp the seven glass of whenever banana north quietly "
            "piano sudden river elbow nine ticket purple asleep under cable "
            "mango thus vertical honey quantum seldom brick"
        ).split()
        others = [w for w in pool if w != chosen]
        words = random.sample(others, n - 1)
        words.insert(random.randint(0, n - 1), chosen)
        return words
