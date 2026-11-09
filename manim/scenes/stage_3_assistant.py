from manim_imports_ext import *
from scenes.agentic_common import *
from scenes.stage_outputs import STAGE3, STAGE3_CLAIM


class Stage3Assistant(AgenticScene):
    """
    Post-training (example conversations ending in STOP, then human
    feedback on pairs of answers) turns the base model into an assistant:
    two examples of each in detail, then many more (with their order of
    magnitude).
    The input is now the system prompt plus the conversation in chat format,
    and the software repeats until the model picks STOP, which is always
    among the options. The answer is fluent and helpful, but its second
    sentence overclaims: a "landmark study" that "proved direct harm",
    from learned patterns, not from any source. Words and bars are scripted
    (scenes/stage_outputs.py).
    """
    stage_number = 3
    stage_title = "AI assistant"
    stage_subtitle = "Helpful answers, but may hallucinate"
    roles = True
    system_prompt = [(SYSTEM_PROMPT, INK)]
    stop_rule = "stop"
    special_rows = ("STOP",)
    input_font_size = 20
    example_conversations = [
        ("How far away is the Moon?", "About 384,000 km."),
        ("Translate 'Danke' into English.", "Thank you."),
    ]
    comparisons = [
        ("Is coffee bad for you?",
         "In moderation, it is fine for most adults.",
         "Coffee was first discovered in Ethiopia, where legend says goats ate the berries and",
         True),
        ("What is 15% of 80?", "15% of 80 is 15.", "12.", False),
    ]
    random_seed = 4

    def construct(self):
        self.setup_stage()
        weights_label = self.get_weights_label("Learned language patterns")
        self.add(self.title_group, self.software_window, self.machine[:2], weights_label)
        self.wait()
        self.post_training()
        self.play(FadeTransform(weights_label, self.get_weights_label("+ Assistant behavior")))
        self.inference()

    def inference(self):
        # The software: the system prompt is part of the input from the start
        self.play(self.build_software())
        self.highlight_system_prompt()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(answer_group[0]))
        self.open_turn()
        for n, record in enumerate(STAGE3):
            self.run_pass(n, self.distribution_from_record(record), (flow, bubble), fast_time=0.4)
        self.flash_rule()
        self.wait()

        # Fluent, but the specific claim comes from learned patterns, not sources
        claim_words = VGroup(*flow[-len(STAGE3_CLAIM.split(" ")):])
        highlights, underlines = self.highlight_words(claim_words)
        self.add(highlights, flow)
        self.play(FadeIn(highlights), ShowCreation(underlines))
        warning = warning_label(["Plausible, but from memory", "and potentially hallucinated"], font_size=18)
        warning.next_to(bubble.bg, DOWN, buff=0.3).align_to(bubble.bg, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait(3)

    # Post-training

    def post_training(self):
        header = self.training_header("Post-training", "Answer helpfully, then STOP")
        self.play(FadeIn(header, 0.2 * DOWN))

        # 1. Example conversations, each turn ending in STOP: two in detail, then many
        label = self.get_part_label("1. Example conversations")
        self.play(FadeIn(label, 0.1 * DOWN))
        for card in [self.get_example_card(*pair) for pair in self.example_conversations]:
            self.play(FadeIn(card, 0.2 * UP))
            stop_rects = VGroup(
                SurroundingRectangle(line[-1], buff=0.04).set_stroke(WARN, 2) for line in card.lines
            )
            self.play(ShowCreation(stop_rects, lag_ratio=0.3))
            self.wait()
            self.play(FadeOut(stop_rects))
            self.play(self.absorb(card), run_time=1.3)
        self.many_examples("conversation", ["Then many more", "≈ 10,000 to 1,000,000 example conversations"])

        # 2. People pick the better of two answers: two in detail, then many
        label2 = self.get_part_label("2. Human feedback")
        self.play(FadeOut(label, 0.1 * UP), FadeIn(label2, 0.1 * UP))
        for card in [self.get_comparison_card(*comp) for comp in self.comparisons]:
            marks = card.marks
            card.remove(marks)
            self.play(FadeIn(card, 0.2 * UP))
            self.play(LaggedStart((FadeIn(mark, scale=1.5) for mark in marks), lag_ratio=0.5))
            card.add(marks)
            self.wait()
            self.play(self.absorb(card), run_time=1.3)
        self.many_examples("comparison", ["Then many more", "≈ 100,000 to 1,000,000 comparisons"])
        self.play(FadeOut(header, 0.2 * UP), FadeOut(label2, 0.2 * UP))

    def get_example_card(self, question, answer, width=3.4, font_size=18):
        lines = VGroup()
        for speaker, string in [("User:", question), ("Assistant:", answer)]:
            flow = FlowText(ORIGIN, width, font_size=font_size)
            flow.add_word(speaker, color=MUTED)
            flow.add_words(string.split(" "))
            flow.add_word("STOP")
            lines.add(flow)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        card = self.place_card(lines, "Example conversation")
        card.lines = lines
        return card

    def get_comparison_card(self, question, answer1, answer2, first_better, width=3.0, font_size=19):
        prompt = FlowText(ORIGIN, width + 0.45, font_size=font_size)
        prompt.add_word("User:", color=MUTED)
        prompt.add_words(question.split(" "))
        answers = VGroup()
        marks = VGroup()
        for string, good in [(answer1, first_better), (answer2, not first_better)]:
            flow = FlowText(ORIGIN, width, font_size=font_size)
            flow.add_words(string.split(" "))
            if not string.endswith("."):
                flow.add_word("...", color=MUTED)
            bubble = ChatBubble(flow, PANEL_FILL, buff=0.08)
            if good:
                # The preferred answer: teal, like the reward of reasoning training
                bubble.bg.set_fill(TOOL_FILL).set_stroke(TOOL_COLOR, 2)
            answers.add(bubble)
            mark = Tex(R"\checkmark" if good else R"\times", font_size=44)
            marks.add(mark.set_color(TOOL_COLOR if good else RED_E))
        answers.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        content = VGroup(prompt, answers).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        answers.shift(0.4 * RIGHT)
        for mark, answer in zip(marks, answers):
            mark.next_to(answer, LEFT, buff=0.12)
        content.add(marks)
        card = self.place_card(content, "Which answer is better?")
        content.remove(marks)
        card.marks = marks
        card.add(marks)
        return card


class Stage3AssistantInference(Stage3Assistant):
    """Only the inference part of Stage3Assistant: starts with the post-trained model."""
    def construct(self):
        self.setup_stage()
        self.add(self.title_group, self.software_window, self.machine[:2], self.get_weights_label("+ Assistant behavior"))
        self.wait(0.5)
        self.inference()
