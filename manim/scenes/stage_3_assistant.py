from manim_imports_ext import *
from scenes.agentic_common import *


class Stage3Assistant(AgenticScene):
    """
    Post-training (example conversations ending in STOP, then human
    feedback on pairs of answers) turns the base model into an assistant.
    The input is now the system prompt plus the conversation in chat format,
    and the software repeats until the model picks STOP, which is always
    among the options. Bars and answer are the real outputs of a small chat
    model (Qwen2.5-0.5B-Instruct, always its most likely word): fluent, but
    it cites "recent papers" it never read, and its specifics come from
    learned patterns, not from any source.
    """
    stage_number = 3
    stage_title = "AI assistant"
    stage_subtitle = "Helpful answers, but may hallucinate"
    roles = True
    system_prompt = [("You are a helpful assistant. Answer in one short sentence.", INK)]
    stop_rule = "stop"
    special_rows = ("STOP",)
    input_font_size = 17
    # Cites "papers" it never read; the specific claim comes from learned patterns
    claims = ["Recent papers suggest", "particularly in the gastrointestinal tract."]
    example_conversations = [
        ("How far away is the Moon?", "About 384,000 km."),
        ("Translate 'Danke' into English.", "Thank you."),
        ("Give me a synonym for fast.", "Quick."),
        ("Is 17 a prime number?", "Yes, 17 is prime."),
        ("Name a primary color.", "Red."),
    ]
    comparisons = [
        ("Is coffee bad for you?",
         "In moderation, it is fine for most adults.",
         "Coffee was first discovered in Ethiopia, where legend says goats ate the berries and",
         True),
        ("What is 15% of 80?", "15% of 80 is 15.", "12.", False),
        ("How long should I boil an egg?",
         "About 9 minutes for a hard-boiled egg.",
         "Eggs are a great source of protein, and chickens lay around",
         True),
    ]
    random_seed = 4

    def construct(self):
        self.setup_stage()
        machine = self.machine
        weights_label = self.get_weights_label("Learned language patterns")
        self.add(self.title_group, self.software_window, machine[:2], weights_label)
        self.wait()

        self.post_training()
        self.play(FadeTransform(weights_label, self.get_weights_label("+ Assistant behavior")))

        # The software: the system prompt is part of the input from the start
        self.play(self.build_software())
        self.wait()
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.25)
        self.play(FadeIn(answer_group[0]))
        self.open_turn()
        for n, record in enumerate(DISTRIBUTIONS["stage3"]):
            self.run_pass(n, self.distribution_from_record(record), (flow, bubble), fast_time=0.4)
        self.flash_rule()
        self.wait()

        # Fluent, but the specific claims come from learned patterns, not sources
        n_first, n_last = (len(claim.split(" ")) for claim in self.claims)
        claim_words = VGroup(*flow[:n_first], *flow[-n_last:])
        highlights, underlines = self.highlight_words(claim_words)
        self.add(highlights, flow)
        self.play(FadeIn(highlights), ShowCreation(underlines))
        warning = warning_label(["Plausible, but from memory", "and potentially hallucinated"], font_size=20)
        warning.next_to(bubble.bg, DOWN, buff=0.3).align_to(bubble.bg, LEFT)
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait(3)

    # Post-training

    def post_training(self):
        center_x = (self.chat_left + self.chat_right) / 2
        header = VGroup(
            text("Post-training", font_size=32, color=ACCENT, weight=BOLD),
            text("Answer helpfully, then STOP", font_size=20, color=MUTED),
        ).arrange(DOWN, buff=0.12)
        header.move_to([center_x, 2.3, 0])
        self.play(FadeIn(header, 0.2 * DOWN))

        # 1. Example conversations, each turn ending in STOP
        label = self.get_part_label("1. Example conversations")
        self.play(FadeIn(label, 0.1 * DOWN))
        cards = [self.get_example_card(*pair) for pair in self.example_conversations]
        first = cards[0]
        self.play(FadeIn(first, 0.2 * UP))
        stop_rects = VGroup(
            SurroundingRectangle(line[-1], buff=0.04).set_stroke(WARN, 2) for line in first.lines
        )
        self.play(ShowCreation(stop_rects, lag_ratio=0.3))
        self.wait()
        self.play(FadeOut(stop_rects))
        self.play(self.absorb(first), run_time=1.3)
        self.stills_every(1.0)
        for n, card in enumerate(cards[1:]):
            run_time = interpolate(0.8, 0.45, n / (len(cards) - 2))
            self.play(FadeIn(card, 0.2 * UP), run_time=0.4 * run_time)
            self.play(self.absorb(card), run_time=run_time)
        self.stills_every(None)

        # 2. People pick the better of two answers
        label2 = self.get_part_label("2. Human feedback")
        self.play(FadeOut(label, 0.1 * UP), FadeIn(label2, 0.1 * UP))
        comparisons = [self.get_comparison_card(*comp) for comp in self.comparisons]
        first = comparisons[0]
        marks = first.marks
        first.remove(marks)
        self.play(FadeIn(first, 0.2 * UP))
        self.play(LaggedStart((FadeIn(mark, scale=1.5) for mark in marks), lag_ratio=0.5))
        first.add(marks)
        self.wait()
        self.play(self.absorb(first), run_time=1.3)
        self.stills_every(1.0)
        for card in comparisons[1:]:
            self.play(FadeIn(card, 0.2 * UP), run_time=0.4)
            self.wait(0.4)
            self.play(self.absorb(card), run_time=0.7)
        self.stills_every(None)
        self.play(FadeOut(header, 0.2 * UP), FadeOut(label2, 0.2 * UP))

    def get_part_label(self, string):
        label = text(string, font_size=22, weight=BOLD)
        label.move_to([(self.chat_left + self.chat_right) / 2, 1.45, 0])
        return label

    def absorb(self, card):
        """A training example goes into the model; the dials shift a little."""
        return AnimationGroup(
            card.animate.scale(0.1).move_to(self.machine[0]).set_opacity(0).set_anim_args(remover=True),
            self.randomize_dials(lag_factor=1),
            self.block_flash(),
        )

    def place_card(self, content, title):
        title_mob = text(title, font_size=16, color=MUTED, weight=BOLD)
        title_mob.next_to(content, UP, buff=0.15, aligned_edge=LEFT)
        group = VGroup(title_mob, content)
        bg = SurroundingRectangle(group, buff=0.15).round_corners(0.1)
        bg.set_stroke(FRAME_GREY, 1).set_fill(TRUE_WHITE, 1)
        card = VGroup(bg, group)
        card.move_to([(self.chat_left + self.chat_right) / 2, 1.1, 0], UP)
        return card

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

    def get_comparison_card(self, question, answer1, answer2, first_better, width=2.9, font_size=16):
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
            answers.add(ChatBubble(flow, PANEL_FILL, buff=0.08))
            mark = Tex(R"\checkmark" if good else R"\times", font_size=28)
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
