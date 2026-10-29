# Manim scenes (light theme)

Scenes adapted from 3Blue1Brown's video
[Large Language Models explained briefly](https://www.youtube.com/watch?v=LPZh9BOjkQs)
([source](https://github.com/3b1b/videos/blob/master/_2024/transformers/chm.py)),
re-coloured for a white background.

## Scenes

Described in [scenes.md](scenes.md); one file per scene in `scenes/`.

| Scene | File | Based on (3b1b) |
|---|---|---|
| `NextWordPrediction` | `scenes/next_word_prediction.py` | `PredictTheNextWord` (opening) |
| `ChatbotPrediction` | `scenes/chatbot_prediction.py` | `ChatBotPrompt` (generation.py) |
| `TrainingLevel0` | `scenes/training_level_0.py` | `LotsOfTextIntoTheMachine` |
| `TrainingLevel1` | `scenes/training_level_1.py` | `ShowMachineWithDials`, without the final zoom-out to many parameters |
| `TrainingLevel2` | `scenes/training_level_2.py` | `ShowSingleTrainingExample` + reverse "backprop" flash + fast iterations over many snippets (real predictions, dials nudged each time) |

### From next-word prediction to agentic AI

New scenes (no 3b1b counterpart) for the four stages of `../llm_to_agentic_ai.svg`.
Shared pieces (windows, model, code panel, chips, bars, chat) are in `scenes/agentic_common.py`.

| Scene | File | What it shows |
|---|---|---|
| `AgenticOverview` | `scenes/overview.py` | The schematic, built stage by stage. Also writes `AgenticOverview.svg` (copied to `../llm_to_agentic_ai_v2.svg`) |
| `Stage1Untrained` | `scenes/stage_1_untrained.py` | Random weights in a "repeat 10 times" loop: all words about equally likely, 10 random words |
| `Stage2BaseModel` | `scenes/stage_2_base_model.py` | Pre-training recap; same loop now continues the question like web text and is cut off after 10 words |
| `Stage3Assistant` | `scenes/stage_3_assistant.py` | Post-training recap (examples, feedback, STOP); the chat as the model reads it; loop until STOP; a hallucinated claim from memory |
| `Stage4Agent` | `scenes/stage_4_agent.py` | Tools in the software; TOOL calls run by the software, results pasted into the text; decide / use tool / observe; sources and remaining risk |

The core idea in all four: the model only turns text into next-word probabilities.
The software around it (shown as a small loop of pseudo-code) picks the words, decides
when to stop, and runs tools.

## Render

```sh
./render.sh scenes/next_word_prediction.py NextWordPrediction -l    # 480p preview
./render.sh scenes/next_word_prediction.py NextWordPrediction       # 1080p (config default)
./render.sh scenes/next_word_prediction.py NextWordPrediction --uhd # 4K
```

Output goes to `media/<SceneName>/`:

- `<SceneName>.mp4`: the native manim render
- `stills/<SceneName>_NNN.png`: one PNG per build (end of every `play()`), from the
  `BuildStills` mixin in `scenes/stills.py`. Scenes made of one long animation set
  `still_interval` to also save a frame every N seconds.

The first run sets up the environment with `uv` and downloads the prediction model
(~1 GB, see below).

Interactive preview (opens a window): `PYTHONPATH=. uv run manimgl <file.py> <Scene>`;
add `-se <line>` to drop into an IPython shell at that line.

## Layout

| Path | What it is |
|---|---|
| `scenes/` | The presentation scenes (subclass or adapt the 3b1b scenes) |
| `_2024/transformers/` | Vendored from `3b1b/videos` (`chm.py` and the modules it imports) |
| `custom/`, `manim_imports_ext.py` | Vendored from `3b1b/videos` (shared helpers) |
| `light_theme.py` | Rebinds 3b1b colour names for a white background (see below) |
| `custom_config.yml` | White background, dark default colours, 1080p, CMU Serif |
| `data/pile_of_text.txt` | Text snippets for `TrainingLevel0` (upstream's file isn't public) |
| `assets/fonts/` | CMU Serif (copied from TeX Live), registered at import time |
| `render.sh` | Wrapper: sets `PYTHONPATH`, provides ffmpeg, writes to `media/<Scene>/` |

Upstream versions: `3b1b/videos` @ `306a134`, `3b1b/manim` @ `fafa083` (pinned in
`pyproject.toml`).

## Light theme

The 3b1b code assumes a black background. Instead of editing every scene,
`light_theme.py` rebinds the colour names that every module gets through
`from manim_imports_ext import *`:

- `WHITE` and `BLACK` are swapped (foreground/background). Use `TRUE_WHITE` /
  `TRUE_BLACK` when you mean the literal colour.
- The grey scale is flipped (`GREY_A` ↔ `GREY_E`, `GREY_B` ↔ `GREY_D`).
- Pale tints (`*_A`, `*_B`) map to the dark shades of the same hue.
- `YELLOW` is a dark gold.

Not covered: colours used as defaults inside manimlib itself (e.g. `SurroundingRectangle`
and `FlashAround` still default to bright yellow). Pass a colour explicitly where it matters.

## Changes to the vendored code

- `chm.py`: `LaggedStartMap` needs a `VGroup`, not a list (newer manimgl API).
- `generation.py`: scenes with `model = "gpt3"` used OpenAI's retired completions endpoint.
  They now fall back to a local Hugging Face model (`hf_model_name`, default
  `Qwen/Qwen2.5-0.5B`) instead of GPT-2 small, whose predictions were poor.
  The probabilities shown are that model's real outputs.
  Whitespace-only tokens are left out of the bar charts.
- `chm.py`: `ShowMachineWithDials` referred to an undefined `dots` (now `out_dots`).
- `helpers.py`: `DATA_DIR` points to the local `data/` folder.
- `manim_imports_ext.py`: registers the bundled fonts and imports `light_theme`.

## Scene notes

- `NextWordPrediction`: starts with the model on screen (`show_machine_intro = True`
  adds 3b1b's 3D build-up). The single word shown first is the model's top prediction.
  Bars are stretched so the top one is readable (the predictions are spread thin);
  the percentages are the real ones.
- `ChatbotPrediction`: always picks the most likely word (after the same "sampling"
  flicker), so the answer is reproducible, and stops at the end of the first sentence.

- Agentic scenes: example outputs are schematic, like in the original figure. The bar
  values are illustrative, except the first step of `Stage2BaseModel`, which shows the real
  next-word probabilities of Qwen2.5-0.5B (base) for the bare question. That model's top
  pick, " Micro...", starts an answer, because modern pre-training data contains much Q&A.
  The second pick, " What" (10%), continues with another question, which is the behaviour
  the stage shows.
- Special words, in reality (checked against the Qwen2.5-Instruct chat template): STOP is an
  end-of-turn token such as `<|im_end|>`, which ends every turn, the user's too. TOOL is a
  call such as `<tool_call>{"name": ..., "arguments": ...}</tool_call>`. The software runs
  it, adds the result to the text (`<tool_response>`) and calls the model again.

## License

The 3b1b code is CC BY-NC-SA 4.0 (`LICENSE.txt`): fine for a non-commercial talk;
credit 3Blue1Brown on the slide.
