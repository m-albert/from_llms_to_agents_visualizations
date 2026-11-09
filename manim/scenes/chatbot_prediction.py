from manim_imports_ext import *
from _2024.transformers.helpers import get_paragraph
from _2024.transformers.generation import ChatBotPrompt, clean_text
from scenes.stills import BuildStills
from scenes.agentic_common import SPECIAL_WORDS, SYSTEM_PROMPT, TRAINED_FILL
from scenes.stage_outputs import STAGE3


class ChatbotPrediction(BuildStills, ChatBotPrompt):
    """
    3b1b's ChatBotPrompt: next-word prediction on a transcript of a chat
    turns the model into an assistant. The first word is animated in full,
    the rest are shown one highlighted word at a time. System prompt and
    answer are the ones of Stage3Assistant: the words and bars come from
    scenes/stage_outputs.py (its first sentence), not from a model.
    """
    system_prompt = SYSTEM_PROMPT
    user_prompt = "User: What do recent papers say about microplastics and health?"
    ai_seed = "Assistant: "
    # Upstream recolors the first len(seed_text) letters of the answer text,
    # so the seed is just the "Assistant:" prefix, in the text color
    seed_text = "Assistant:"
    seed_text_color = WHITE
    max_predictions = 40

    def construct(self):
        self.n_predicted = 0
        text_mob, next_word_line, machine = self.init_text_and_machine()
        # Trained model: blue, as in the stage scenes
        machine[0].set_fill(TRAINED_FILL)

        all_strs = list(map(clean_text, [self.system_prompt, self.user_prompt, self.ai_seed]))
        system_prompt, user_prompt, ai_seed = all_text = VGroup(
            get_paragraph(
                s.split(" "),
                font_size=self.font_size,
                line_len=self.line_len
            )
            for s in all_strs
        )
        all_text.arrange(DOWN, aligned_edge=LEFT, buff=0.75)
        all_text.move_to(self.text_corner, UL)
        self.remove(text_mob)
        self.add(all_text)

        self.text_corner = ai_seed.get_corner(UL)
        next_word_line.next_to(ai_seed, RIGHT, aligned_edge=DOWN)
        self.cur_str = "\n\n".join(all_strs)
        self.save_still()

        # Comment on system prompt
        sys_rect = SurroundingRectangle(system_prompt)
        sys_rect.set_stroke(GREEN, 2)
        self.play(
            ShowCreation(sys_rect),
            system_prompt.animate.set_color(GREEN_B)
        )
        self.wait()

        # User's prompt
        user_rect = SurroundingRectangle(user_prompt)
        user_rect.set_stroke(BLUE, 2)
        self.play(
            ReplacementTransform(sys_rect, user_rect),
            user_prompt.animate.set_color(BLUE_B),
        )
        self.wait()
        self.play(FadeOut(user_rect))

        # Run predictions until the answer's first sentence is complete
        text_mob = all_text
        # Keep the prompts; the answer line is redrawn each cycle
        self.add(VGroup(system_prompt, user_prompt).copy())
        for n in range(self.max_predictions):
            self.still_on_wait = (n > 0)
            text_mob = self.new_selection_cycle(
                text_mob, next_word_line, machine,
                skip_anims=(n > 0),
            )
            if self.cur_str.endswith("."):
                break
        self.skip_animations = False
        self.still_on_wait = False
        self.play(FadeOut(next_word_line))
        self.wait(3)

    def predict_next_token(self, text):
        """The scripted distribution of the next word of the stage 3 answer (picked word first)."""
        record = STAGE3[self.n_predicted]
        self.n_predicted += 1
        rows = [(record["word"], record["p"])]
        rows += [(word, p) for word, p in record["others"] if word not in SPECIAL_WORDS]
        return [" " + word for word, p in rows], [p for word, p in rows]

    def wait(self, *args, **kwargs):
        super().wait(*args, **kwargs)
        # The skipped prediction cycles only show up during one short wait each
        if getattr(self, "still_on_wait", False) and not self.skip_animations:
            self.save_still()

    def animate_random_sample(self, bar_groups):
        # Same flicker as upstream, but always land on the most likely word,
        # which keeps the answer coherent and the render reproducible
        widths = np.array([group[1].get_width() for group in bar_groups[:-1]])
        dist = widths / widths.sum()
        seed = random.randint(0, 1000)
        buff = 0.025
        highlight_rect = SurroundingRectangle(bar_groups[0], buff=buff)
        highlight_rect.set_stroke(YELLOW, 2)
        highlight_rect.set_fill(YELLOW, 0.25)

        def highlight_randomly(rect, alpha):
            np.random.seed(seed + int(10 * alpha))
            index = 0 if alpha >= 0.9 else np.random.choice(np.arange(len(dist)), p=dist)
            rect.surround(bar_groups[index], buff=buff)
            rect.stretch(1.1, 0)

        self.play(
            UpdateFromAlphaFunc(highlight_rect, highlight_randomly),
            Animation(bar_groups)
        )
        bar_groups.add_to_back(highlight_rect)
