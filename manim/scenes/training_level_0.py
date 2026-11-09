from manim_imports_ext import *
from _2024.transformers.chm import LotsOfTextIntoTheMachine
from _2024.transformers.helpers import get_paragraph
from _2024.transformers.ml_basics import Dial
from scenes.agentic_common import ACCENT, TRAINED_FILL, WARN_FILL
from scenes.stills import BuildStills


class TrainingLevel0(BuildStills, LotsOfTextIntoTheMachine):
    """
    3b1b's LotsOfTextIntoTheMachine, shortened: snippets of text from all
    over fly into the model. Snippets come from data/pile_of_text.txt, plus
    a few about microplastics and health (the question of the stage scenes),
    whose key words are highlighted. The model turns from grey (untrained)
    to blue (trained) as the text goes in.
    """
    run_time = 10
    still_interval = 1.0  # The scene is one long play()
    topic_snippets = [
        "Microplastics have been found in human blood, lungs and placenta.",
        "Plastic bottles slowly break down into tiny particles called microplastics.",
        "A study links microplastics in arteries to a higher risk of heart attack.",
        "How microplastics affect human health is still being studied.",
    ]
    topic_words = ["Microplastics", "microplastics", "health"]
    # Where the topic snippets go in the shuffled pile
    topic_positions = [6, 16, 26, 36]

    def construct(self):
        # Add machine (as upstream)
        text_mob, next_word_line, machine = self.init_text_and_machine()
        machine.scale(1.5)
        self.clear()
        self.add(machine)

        blocks, title = machine[:2]
        dials = Dial().get_grid(8, 12).set_width(0.9 * blocks[-1].get_width()).move_to(blocks[-1])
        dials.set_stroke(opacity=0.1)
        blocks[-1].add(dials)

        machine.center()
        machine[1].set_stroke(BLACK, 3)

        # Feed in lots of text
        snippets = self.get_text_snippets()
        for position, snippet in zip(self.topic_positions, self.topic_snippets):
            snippets.insert(position, snippet)
        text_mobs = VGroup(self.get_snippet_mob(snippet) for snippet in snippets)
        directions = compass_directions(12, start_vect=UR)
        for text_mob, vect in zip(text_mobs, it.cycle(directions)):
            text_mob.set_max_width(self.max_snippet_width)
            text_mob.move_to(5 * vect).shift_onto_screen(buff=0.25)

        self.play(
            LaggedStart(
                (Succession(
                    FadeIn(text_mob),
                    text_mob.animate.set_opacity(0).move_to(machine.get_center()),
                )
                for text_mob in text_mobs),
                lag_ratio=0.05,
                run_time=self.run_time
            ),
            blocks.animate.set_fill(TRAINED_FILL).set_anim_args(run_time=self.run_time, rate_func=linear),
        )
        self.remove(text_mobs)
        self.wait()

    def get_snippet_mob(self, snippet):
        mob = get_paragraph(snippet.split(" "), line_len=25)
        if snippet not in self.topic_snippets:
            return mob
        # The question's topic: key words in blue, on a highlight
        words = VGroup(*(part for word in self.topic_words for part in mob[word]))
        words.set_color(ACCENT)
        highlights = VGroup(
            SurroundingRectangle(word, buff=0.04).set_fill(WARN_FILL, 1).set_stroke(width=0)
            for word in words
        )
        return VGroup(highlights, mob)
