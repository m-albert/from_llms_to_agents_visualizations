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
| **MODEL** (middle) | The model inside a computer screen, with what the computer is set to do with it (two short lines on the screen, e.g. *Generate / 10 words*). |
| **CHAT** (bottom) | The same chat window and the same question at every stage, with that stage's answer. A small person icon marks the human user's message, and a blue sparkle icon marks the model's reply. |

A band along the bottom reads: *"Next-token prediction runs underneath every stage: later steps
build on it, they don't replace it."* The figure has no title or footnote, so the slide can supply
its own. Points the old footnote made (words stand in for tokens, STOP and TOOL are special
tokens, the outputs are schematic) now need to be said aloud or put on the slide.

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
| 1 | Untrained model | Random output: nothing learned yet | Grey network, random weights. Computer: *Generate 10 words* | Ten random words as plain text, in the same bubble style as stage 2 ("orbit lamp the seven glass of whenever banana north quietly") |
| 2 | Pre-trained base model | Completes text, not yet an assistant | Blue network, learned language patterns. Computer: *Generate 10 words* | Continues the question instead of answering it (10 words), with the note "Doesn't know when to stop" |
| 3 | AI assistant | Helpful answers, but may hallucinate | Same network. Computer: *Generate until* **STOP** | A helpful-looking answer that ends in **STOP**. One claim is highlighted amber with the warning "Plausible, but unsupported" |
| 4 | Tool-using agent | Can retrieve and act; needs oversight | Same network, on a wider screen: the tools sit *inside* the computer, to the right of the model behind a dashed divider. They name concrete actions (*Search web*, *Read files*, *Execute code*, …), each attached to a **TOOL** special word | Tool steps (**TOOL** Search papers / Read PDFs / Summarize findings), a cautious answer ending in **STOP**, and placeholder sources Paper A/B/C |

## Ideas the figure is built to get across

- **One model throughout.** The network, screen and chat window look the same in every stage. Only
  the weights, the learned behaviour and the tools around the model change.
- **Next-token prediction is never replaced.** Later steps build on it.
- **The model learns where an answer ends.** In stages 1 and 2 the computer cuts the output off
  after a fixed number of words. From stage 3 on, the model ends its own answer with STOP.
  STOP is a deliberate simplification: base models already have an end-of-document token from
  pre-training. What post-training adds is an end-of-turn token (e.g. `<|im_end|>`) that marks the
  end of the assistant's reply, so the model knows where *an answer* ends. The stage 2 note is
  worded with this in mind.
- **Tools are called through special words.** The agent emits TOOL. The computer runs the tool and
  returns the result, and the loop continues.
- **Fallibility is shown honestly.** Post-training doesn't remove hallucinations, and tools or
  citations don't guarantee truth: the agent still "needs oversight".
- **No real citations.** All example outputs are schematic: there are no real paper titles,
  findings or reference numbers.

## Visual style

- White background (the figure is meant to sit on a white slide), navy text, and one blue accent for the progression (step cards,
  connectors, trained network).
- Teal for tool use, amber for possible hallucinations, and dark chips for special words
  (STOP, TOOL).
- System sans-serif fonts. Body text is 18 units or larger, except the screen text and the chip
  labels.
- Plain, editable SVG: real `<text>` elements, no images, `foreignObject`, filters or external
  fonts. Parts are grouped with named ids (`pretraining`, `posttraining`, `tools`, `agent-loop`,
  `middle-row-model`, `model-1` … `model-4`, `stage-1` … `stage-4`, `unsupported-claim`,
  `hallucination-warning`, `connectors`, `next-token-baseline`). Everything except the background
  sits in a `figure` group, shifted up by 46 units so the content is vertically centred. The steps row
  has extra space below it to separate it from the stage headers.

---
