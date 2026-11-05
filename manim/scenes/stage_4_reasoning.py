from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.stage_outputs import STAGE4


class Stage4Reasoning(AgenticScene):
    """
    Reasoning training: the model practises problems with checkable answers.
    It writes private thoughts between THINK and ANSWER; only the answer is
    checked, and correct answers are rewarded. Two attempts in detail,
    then many more problems (with their order of magnitude). In the software, the system
    prompt is the same as for the assistant (the special words are learned,
    not prompted); the software shows the thoughts as private and the part
    after ANSWER as the answer, and folds the thoughts away when the answer
    starts. The thoughts catch what the assistant got wrong (harm in humans
    is not proven), so the answer is careful, but it still comes from
    memory. Words and bars are scripted (scenes/stage_outputs.py).
    """
    stage_number = 4
    stage_title = "Reasoning model"
    stage_subtitle = "Thinks first, but still no sources"
    roles = True
    system_prompt = [("What follows is a conversation between a human and a helpful and kind assistant.", INK)]
    stop_rule = "stop"
    special_rows = ("THINK", "ANSWER", "STOP")
    input_font_size = 16
    # (problem, thoughts, answer, correct)
    attempts = [
        ("What is 17 × 24?", "17 × 20 = 340 and 17 × 4 = 68, so 340 + 68 = 408", "408", True),
        ("What is 17 × 24?", "17 × 24 is about 17 × 25 = 425", "425", False),
    ]
    random_seed = 6

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label("+ Assistant behavior")
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)
        self.wait()
        self.reasoning_training()
        self.play(FadeTransform(weights_label, self.get_weights_label("+ Thinking")))
        self.inference()

    def inference(self):
        # The software: same system prompt, plus rules for THINK and ANSWER
        self.play(self.build_software())
        self.highlight_system_prompt()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        icon, flow, bubble = self.get_thought(self.user_bubble.get_bottom()[1] - 0.2)
        self.play(FadeIn(icon), FadeIn(bubble))
        self.open_turn()
        self.run_records(STAGE4, colors=self.thought_color)
        self.flash_rule()
        self.wait()

        # More careful, but still from memory: no sources
        warning = warning_label(["More careful, but still", "answers from memory"], font_size=20)
        warning.next_to(self.chat[1].bg, DOWN, buff=0.3).align_to(self.chat[1].bg, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait(3)

    # Reasoning training

    def reasoning_training(self):
        header = self.training_header("Reasoning training", "Think privately, then answer")
        self.play(FadeIn(header, 0.2 * DOWN))
        label = self.get_part_label("Practice problems")
        self.play(FadeIn(label, 0.1 * DOWN))

        cards = [self.get_attempt_card(*attempt) for attempt in self.attempts]

        # First attempt, step by step: thoughts, answer, check, reward
        first = cards[0]
        mark, reward = first.check
        first.remove(first.check)
        self.play(FadeIn(first, 0.2 * UP))
        # The thoughts are free; only the answer is checked
        _, thought_lines = self.highlight_words(first.thought[1:], color=MUTED)
        thought_note = text("Thoughts: not checked", font_size=15, color=MUTED, slant=ITALIC)
        thought_note.next_to(first.bg, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(ShowCreation(thought_lines), FadeIn(thought_note))
        answer_rect = SurroundingRectangle(first.answer, buff=0.04).set_stroke(TOOL_COLOR, 2)
        self.play(ShowCreation(answer_rect))
        self.play(FadeIn(mark, scale=1.5), FadeIn(reward, 0.1 * RIGHT))
        first.add(first.check)
        self.wait()
        self.play(FadeOut(VGroup(thought_lines, thought_note, answer_rect)))
        self.play(self.absorb(first), run_time=1.3)

        # The same problem, a careless attempt: no reward
        second = cards[1]
        mark, reward = second.check
        second.remove(second.check)
        self.play(FadeIn(second, 0.2 * UP))
        answer_rect = SurroundingRectangle(second.answer, buff=0.04).set_stroke(RED_E, 2)
        self.play(ShowCreation(answer_rect))
        self.play(FadeIn(mark, scale=1.5), FadeIn(reward, 0.1 * RIGHT))
        second.add(second.check)
        self.wait()
        self.play(FadeOut(answer_rect))
        self.play(self.absorb(second), run_time=1.3)

        # Then many more problems, each tried many times
        self.many_examples("problem", ["Then many more", "≈ 100,000 problems,", "many attempts each"])
        self.play(FadeOut(header, 0.2 * UP), FadeOut(label, 0.2 * UP))

    def get_attempt_card(self, problem, thoughts, answer, correct, width=3.4, font_size=17):
        question = FlowText(ORIGIN, width, font_size=font_size)
        question.add_word("User:", color=MUTED)
        question.add_words(problem.split(" "))
        question.add_word("STOP")
        attempt = FlowText(ORIGIN, width, font_size=font_size)
        attempt.add_word("Assistant:", color=MUTED)
        thought = VGroup(attempt.add_word("THINK"), *attempt.add_words(thoughts.split(" "), color=MUTED))
        answer_mobs = VGroup(attempt.add_word("ANSWER"), *attempt.add_words(answer.split(" ")))
        attempt.add_word("STOP")
        lines = VGroup(question, attempt).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        card = self.place_card(lines, "Problem and the model's attempt")
        mark = Tex(R"\checkmark" if correct else R"\times", font_size=30)
        mark.set_color(TOOL_COLOR if correct else RED_E)
        reward = text("reward" if correct else "no reward", font_size=16, color=TOOL_COLOR if correct else RED_E, weight=BOLD)
        check = VGroup(mark, reward).arrange(RIGHT, buff=0.1)
        check.next_to(card[0], DOWN, buff=0.12, aligned_edge=RIGHT)
        card.add(check)
        card.bg = card[0]
        card.thought = thought
        card.answer = answer_mobs
        card.check = check
        return card


class Stage4ReasoningInference(Stage4Reasoning):
    """Only the inference part of Stage4Reasoning: starts with the reasoning-trained model."""
    def construct(self):
        self.setup_stage()
        self.add(self.title_group, self.software_window, self.machine[:2], self.get_weights_label("+ Thinking"))
        self.wait(0.5)
        self.inference()
