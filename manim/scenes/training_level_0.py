from manim_imports_ext import *
from _2024.transformers.chm import LotsOfTextIntoTheMachine
from scenes.stills import BuildStills


class TrainingLevel0(BuildStills, LotsOfTextIntoTheMachine):
    """
    3b1b's LotsOfTextIntoTheMachine, shortened: snippets of text from all
    over fly into the model. Snippets come from data/pile_of_text.txt.
    """
    run_time = 10
    still_interval = 1.0  # The scene is one long play()
