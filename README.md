# From next-token prediction to agentic AI

`llm_to_agentic_ai.svg` is a single 16:9 figure (viewBox `0 0 1600 900`) for the retreat talk
"Understanding AI: From Next-Token Prediction to Agentic AI". It is meant to be understood in
30–60 seconds by scientists who use AI but don't know how it works inside.

## The idea in one sentence

The same model, running on the same kind of computer, gets the same question four times. Three
steps (pre-training, post-training, tools + agent loop) change what it can do, and next-token
prediction keeps running underneath all of it.

## Layout

The figure has four columns, one per stage, read left to right. Each column has three rows,
labelled on the left margin:

| Row | Shows |
|---|---|
| **STEPS** (top) | The three steps, drawn as tinted cards that sit *between* the columns. A line runs down from each card to an arrow between two neighbouring models. |
| **MODEL** (middle) | The model inside a computer screen, with what the computer is set to do with it. |
| **CHAT** (bottom) | The same chat window and the same question at every stage, with that stage's answer. |

A band along the bottom reads: *"Next-token prediction runs underneath every stage: later steps
build on it, they don't replace it."* A footnote says that words stand in for tokens, that STOP and
TOOL are special tokens, and that the outputs are schematic.

## Steps (top row)

1. **Pre-training**: "Learn by predicting the next word". Icons for books, web, code and papers
   lead into the model.
2. **Post-training**: "Answer helpfully, then stop". Examples (Q&A), human feedback, and special
   words (e.g. **STOP**).
3. **Tools + agent loop**: "Run the model in a loop with tools". Decide → Use tool → Observe,
   with an arrow labelled *continue* looping back to the start.

## Stages (middle and bottom rows)

The question is the same everywhere: *"What do recent papers say about microplastics & health?"*

| # | Stage | Message | Model (middle row) | Chat answer (bottom row) |
|---|---|---|---|---|
| 1 | Untrained model | Random output: nothing learned yet | Grey network, random weights. Computer: *Generate 10 words* | Ten random word chips ("orbit lamp the seven…") |
| 2 | Pre-trained base model | Completes text, not yet an assistant | Blue network, learned language patterns. Computer: *Generate 10 words* | Continues the question instead of answering it (10 words), with the note "No stop word: cut off after 10" |
| 3 | AI assistant | Helpful answers, but may hallucinate | Same network. Computer: *Generate until* **STOP** | A helpful-looking answer that ends in **STOP**. One claim is highlighted amber with the warning "Plausible, but unsupported" |
| 4 | Tool-using agent | Can retrieve and act; needs oversight | Same network and computer, plus Files, Web, Code and Papers tools, each attached to a **TOOL** special word | Tool steps (**TOOL** Search papers / Read PDFs / Summarize findings), a cautious answer ending in **STOP**, and placeholder sources Paper A/B/C |

## Ideas the figure is built to get across

- **One model throughout.** The network, screen and chat window look the same in every stage. Only
  the weights, the learned behaviour and the tools around the model change.
- **Next-token prediction is never replaced.** Later steps build on it.
- **The stop word is learned.** Stages 1 and 2 have no stop word, so the computer cuts the output
  off after a fixed number of words. From stage 3 on, the model ends its own answer with STOP.
- **Tools are called through special words.** The agent emits TOOL. The computer runs the tool and
  returns the result, and the loop continues.
- **Fallibility is shown honestly.** Post-training doesn't remove hallucinations, and tools or
  citations don't guarantee truth: the agent still "needs oversight".
- **No real citations.** All example outputs are schematic: there are no real paper titles,
  findings or reference numbers.

## Visual style

- Off-white background, navy text, and one blue accent for the progression (step cards,
  connectors, trained network).
- Teal for tool use, amber for possible hallucinations, and dark chips for special words
  (STOP, TOOL).
- System sans-serif fonts. Body text is 18 units or larger, except the screen text, the chip
  labels and the footnote.
- Plain, editable SVG: real `<text>` elements, no images, `foreignObject`, filters or external
  fonts. Parts are grouped with named ids (`pretraining`, `posttraining`, `tools`, `agent-loop`,
  `middle-row-model`, `model-1` … `model-4`, `stage-1` … `stage-4`, `unsupported-claim`,
  `hallucination-warning`, `connectors`, `next-token-baseline`, `footnote`).

---
