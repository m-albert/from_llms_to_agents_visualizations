from manim_imports_ext import *
from scenes.agentic_common import *


class Stage3Assistant(AgenticScene):
    """
    Post-training (many example conversations, then human feedback on
    pairs of answers) turns the base model into an assistant. The software
    joins a system prompt and the chat into one text, with STOP after each
    turn, and now loops until the model writes STOP. The answer is fluent
    and helpful-looking, but one claim is invented: it comes from patterns
    in the weights, not from any source.
    """
    stage_number = 3
    stage_title = "AI assistant"
    stage_subtitle = "Helpful answers, but may hallucinate"
    loop_rule = "stop"
    input_font_size = 18
    # The generated answer (illustrative)
    answer = "Studies suggest microplastics may be linked to inflammation. A landmark study proved direct harm in humans."
    claim = "A landmark study proved direct harm in humans."
    # Post-training data (made up, in the style of real datasets)
    example_conversations = [
        ("How far away is the Moon?", "About 384,000 km."),
        ("Translate 'Danke' into English.", "Thank you."),
        ("Give me a synonym for fast.", "Quick."),
        ("Is 17 a prime number?", "Yes, 17 is prime."),
        ("Name a primary color.", "Red."),
        ("Summarize: the meeting moved to Friday.", "The meeting is now on Friday."),
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

        # Post-training, part 1: many example conversations
        header = VGroup(
            text("Post-training", font_size=34, color=ACCENT, weight=BOLD),
            text("Answer helpfully, then stop", font_size=24, color=MUTED),
        ).arrange(DOWN, buff=0.15)
        center_x = (self.chat_left + self.chat_right) / 2
        header.move_to([center_x, 2.3, 0])
        self.play(FadeIn(header, 0.2 * DOWN))

        part1 = self.get_part_label("1", "Learn from example conversations", "Supervised fine-tuning")
        self.play(FadeIn(part1, 0.1 * DOWN))
        cards = [self.get_example_card(*pair) for pair in self.example_conversations]
        for card in cards:
            card.move_to([center_x, 0.75, 0], UP)
        first = cards[0]
        self.play(FadeIn(first, 0.2 * UP))
        stops = VGroup(*(line[-1] for line in first.lines))
        stop_rects = VGroup(SurroundingRectangle(stop, buff=0.05).set_stroke(WARN, 2) for stop in stops)
        stop_note = text("Each answer ends with the special word STOP", font_size=18, color=WARN)
        stop_note.next_to(first, DOWN, buff=0.2)
        self.play(ShowCreation(stop_rects, lag_ratio=0.3), FadeIn(stop_note))
        self.wait()
        self.play(FadeOut(stop_rects), FadeOut(stop_note))
        self.play(self.absorb(first), run_time=1.5)

        self.stills_every(1.0)
        for n, card in enumerate(cards[1:]):
            run_time = interpolate(0.9, 0.5, n / (len(cards) - 2))
            self.play(FadeIn(card, 0.2 * UP), run_time=0.4 * run_time)
            self.play(self.absorb(card), run_time=run_time)
        self.stills_every(None)

        # Part 2: people compare answers, the model is nudged towards the preferred one
        part2 = self.get_part_label("2", "Learn from human feedback", "Reinforcement learning from human feedback")
        part2.move_to(part1)
        self.play(FadeOut(part1, 0.1 * UP), FadeIn(part2, 0.1 * UP))
        comparisons = [self.get_comparison_card(*comp) for comp in self.comparisons]
        for card in comparisons:
            card.move_to([center_x, 0.75, 0], UP)
        first = comparisons[0]
        marks = first.marks
        first.remove(marks)
        self.play(FadeIn(first, 0.2 * UP))
        rater = person_icon(0.5)
        rater.next_to(first, DOWN, buff=0.2)
        rater_label = text("Human rater: which answer is better?", font_size=18, color=MUTED)
        rater_label.next_to(rater, RIGHT, buff=0.15)
        VGroup(rater, rater_label).match_x(first)
        self.play(FadeIn(rater), FadeIn(rater_label))
        self.play(LaggedStart((FadeIn(mark, scale=1.5) for mark in marks), lag_ratio=0.5))
        first.add(marks)
        self.wait()
        self.play(self.absorb(first), FadeOut(rater), FadeOut(rater_label), run_time=1.5)
        self.stills_every(1.0)
        for card in comparisons[1:]:
            self.play(FadeIn(card, 0.2 * UP), run_time=0.5)
            self.wait(0.6)
            self.play(self.absorb(card), run_time=0.8)
        self.stills_every(None)

        self.play(
            FadeOut(header, 0.2 * UP),
            FadeOut(part2, 0.2 * UP),
            FadeTransform(weights_label, self.get_weights_label("+ Assistant behavior")),
        )

        # The software loop, now repeating until the model writes STOP
        self.play(self.build_loop())
        stop_rect = self.flash_rule()
        self.play(FadeOut(stop_rect))

        # The chat message goes to the input, with the system prompt put in front
        card = self.get_system_prompt_card()
        self.play(FadeIn(card, 0.2 * UP))
        self.play(FadeIn(self.chat_window), FadeIn(self.user_bubble, 0.25 * LEFT))
        self.wait()
        self.join_system_prompt(card)

        # Generate the answer: one word per pass, the same way each time
        answer_group, flow, bubble = self.get_answer(self.user_bubble.get_bottom()[1] - 0.3)
        self.play(FadeIn(answer_group[0]))
        words = self.answer.split(" ")
        self.emit_word(words[0], flow, bubble, slow=True)
        for word in words[1:]:
            self.emit_word(word, flow, bubble, run_time=0.3)
        self.emit_word("STOP", flow, bubble, run_time=0.5)
        stop_rect = self.flash_rule()
        self.wait(0.5)
        self.play(FadeOut(stop_rect))
        self.wait()

        # The hallucinated claim
        claim_words = self.find_words(flow, self.claim.split(" "))
        highlights = VGroup(
            SurroundingRectangle(word, buff=0.04).set_fill(WARN_FILL, 1).set_stroke(width=0)
            for word in claim_words
        )
        underlines = VGroup(
            DashedLine(word.get_corner(DL), word.get_corner(DR), dash_length=0.05).shift(0.05 * DOWN)
            for word in claim_words
        ).set_stroke(WARN, 2)
        self.add(highlights, flow)
        self.play(FadeIn(highlights), ShowCreation(underlines))
        self.wait()

        # Where it comes from: the weights, not a source
        memory_arrow = CurvedArrow(
            bubble.bg.get_left() + 0.1 * LEFT + (claim_words.get_y() - bubble.bg.get_y()) * UP,
            machine[0].get_right() + 0.15 * RIGHT + 0.45 * DOWN,
            angle=40 * DEGREES,
        )
        memory_arrow.set_color(WARN)
        memory_label = text("From memory: learned patterns", font_size=24, color=WARN)
        memory_label.next_to(memory_arrow.pfp(0.5), UP, buff=0.15)
        memory_label.set_x(min(memory_label.get_x(), self.window_right - 0.2 - memory_label.get_width() / 2))
        self.play(ShowCreation(memory_arrow), FadeIn(memory_label))
        self.wait()

        notes = VGroup(
            text("Every word was a likely next word", font_size=20, color=MUTED),
            text("No source was looked up or checked", font_size=20, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        notes.next_to(bubble.bg, DOWN, buff=0.3).align_to(bubble.bg, LEFT)
        warning = warning_label(["Plausible, but from memory", "and potentially hallucinated"], font_size=24)
        warning.next_to(notes, DOWN, buff=0.35).align_to(notes, LEFT)
        self.play(FadeIn(notes, lag_ratio=0.5, run_time=2))
        self.play(FadeIn(warning, 0.2 * UP))
        self.wait()

        takeaway = text("Post-training teaches the format and when to STOP, not what is true", font_size=24)
        takeaway.move_to(3.72 * DOWN)
        self.play(
            FadeIn(takeaway, 0.2 * UP),
            FadeOut(memory_arrow),
            FadeOut(memory_label),
        )
        self.wait(3)

    def get_part_label(self, number, title, subtitle):
        label = VGroup(
            text(f"{number}.  {title}", font_size=24, weight=BOLD),
            text(subtitle, font_size=18, color=MUTED),
        ).arrange(DOWN, buff=0.1)
        label.move_to([(self.chat_left + self.chat_right) / 2, 1.3, 0])
        return label

    def absorb(self, card):
        """A training example goes into the model; the dials shift a little."""
        return AnimationGroup(
            card.animate.scale(0.1).move_to(self.machine[0]).set_opacity(0).set_anim_args(remover=True),
            self.randomize_dials(lag_factor=1),
            self.block_flash(),
        )

    def get_card(self, content, title):
        title_mob = text(title, font_size=18, color=MUTED, weight=BOLD)
        title_mob.next_to(content, UP, buff=0.2, aligned_edge=LEFT)
        group = VGroup(title_mob, content)
        bg = SurroundingRectangle(group, buff=0.2).round_corners(0.1)
        bg.set_stroke(FRAME_GREY, 1).set_fill(TRUE_WHITE, 1)
        return VGroup(bg, group)

    def get_example_card(self, question, answer, width=4.4, font_size=21):
        lines = VGroup()
        for speaker, string in [("User:", question), ("Assistant:", answer)]:
            flow = FlowText(ORIGIN, width, font_size=font_size)
            flow.add_word(speaker, color=MUTED)
            flow.add_words(string.split(" "))
            flow.add_word("STOP")
            lines.add(flow)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        card = self.get_card(lines, "Example conversation")
        card.lines = lines
        return card

    def get_comparison_card(self, question, answer1, answer2, first_better, width=4.0, font_size=19):
        prompt = FlowText(ORIGIN, width + 0.5, font_size=font_size)
        prompt.add_word("User:", color=MUTED)
        prompt.add_words(question.split(" "))
        answers = VGroup()
        marks = VGroup()
        for string, good in [(answer1, first_better), (answer2, not first_better)]:
            flow = FlowText(ORIGIN, width, font_size=font_size)
            flow.add_words(string.split(" "))
            if not string.endswith("."):
                flow.add_word("...", color=MUTED)
            bubble = ChatBubble(flow, PANEL_FILL, buff=0.1)
            mark = Tex(R"\checkmark" if good else R"\times", font_size=34)
            mark.set_color(TOOL_COLOR if good else RED_E)
            answers.add(bubble)
            marks.add(mark)
        answers.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        content = VGroup(prompt, answers).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        answers.shift(0.5 * RIGHT)
        for mark, bubble in zip(marks, answers):
            mark.next_to(bubble, LEFT, buff=0.15)
        card = self.get_card(content, "Which answer is better?")
        card.marks = marks
        card.add(marks)
        return card

    def find_words(self, flow, words):
        """The last run of mobs in flow matching the given words."""
        n = len(words)
        return VGroup(*flow[len(flow) - n - 1:len(flow) - 1])
