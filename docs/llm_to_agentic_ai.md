# From next-token prediction to agentic AI

[`llm_to_agentic_ai.svg`](../llm_to_agentic_ai.svg) is a single wide figure (viewBox `0 0 1980 1040`) for the retreat talk
"Understanding AI: From Next-Token Prediction to Agentic AI". It is meant to be understood in
30–60 seconds by scientists who use AI but don't know how it works inside.

## The idea in one sentence

The same model, running inside the same kind of software environment, gets the same question five times. Four
steps (pre-training, post-training, reasoning training, tools + agent loop) change what it can do, and next-token
prediction keeps running underneath all of it.

## Layout

The figure has five columns, one per stage, read left to right. Each column has three rows,
labelled on the left margin:

| Row | Shows |
|---|---|
| **STEPS** (top) | The four steps, drawn as tinted cards that sit *between* the columns. A line runs down from each card to an arrow between two neighbouring models. |
| **MODEL** (middle) | The model inside a software environment, drawn as an app window (title bar with window dots and a `</>` mark). The window shows what the software is set to do with the model, in two short lines, e.g. *Generate / 10 words*. In stages 3–5 the window is wider and also holds a **system prompt** panel (dashed, tinted, labelled SYSTEM PROMPT): the hidden text the software puts in front of every conversation. Stage 4 adds a second, plain panel (SPLIT OUTPUT) showing how the software splits the model's output. The model row is tall enough for the stage 5 system prompt, which is the longest. |
| **CHAT** (bottom) | The same chat window and the same question at every stage, with that stage's answer. A small person icon marks the human user's message, and a small blue robot (chatbot) icon marks the model's reply. |

The figure has no title, footnote or bottom band, so the slide can supply
its own. Points the old footnote made (words stand in for tokens, STOP and TOOL are special
tokens, the outputs are schematic) now need to be said aloud or put on the slide.

## Steps (top row)

1. **Pre-training**: "Learn by predicting the next word". Icons for books, web, code and papers
   lead into the model.
2. **Post-training**: "Answer helpfully, then stop". Examples (Q&A), human feedback, and special
   words (e.g. **STOP**).
3. **Reasoning training**: "Think privately, then answer". Problems (x=?), rewards for correct
   answers, and special words (**THINK**, **ANSWER**).
4. **Tools + agent loop**: "Run the model in a loop with tools". Decide → Use tool → Observe,
   with an arrow labelled *continue* looping back to the start.

## Stages (middle and bottom rows)

The question is the same everywhere: *"What do recent papers say about microplastics & health?"*

Above each stage title is an approximate year with a short reference point. Stages 1 and 2 have a
short grey note inside the chat window, under the answer. Stages 3–5 have an amber hallucination
warning centred under the chat window.

| # | Year shown | What it refers to |
|---|---|---|
| 1 | ≈ 2017 · Transformer architecture | The architecture behind today's LLMs (the untrained network). Every model starts untrained, so this marks when the design appeared, not a period when people used untrained models. |
| 2 | ≈ 2018–2020 · GPT-1 to GPT-3 | Large pre-trained base models. |
| 3 | ≈ 2022 · ChatGPT | Post-trained chat assistants (InstructGPT early 2022, ChatGPT late 2022). |
| 4 | ≈ 2024 · o1, DeepSeek-R1 | Reasoning models trained to think before answering (OpenAI o1 in late 2024, DeepSeek-R1 in early 2025). |
| 5 | ≈ 2024–today · tool use & agents | Function calling existed from 2023; agent loops, especially for coding, took off in 2024–2025. |

The years are approximate. The figure is a conceptual sequence, not a strict history.

| # | Stage | Message | Model (middle row) | Chat answer (bottom row) |
|---|---|---|---|---|
| 1 | Untrained model | Random output: nothing learned yet | Grey network, random weights. Software: *Generate 10 words* | Ten random words as plain text, in the same bubble style as stage 2 ("orbit lamp the seven glass of whenever banana north quietly") |
| 2 | Pre-trained base model | Completes text, not yet an assistant | Blue network, learned language patterns. Software: *Generate 10 words* | Continues the question instead of answering it (10 words), with the note "Continues from input prompt" |
| 3 | AI assistant | Helpful answers, but may hallucinate | Same network, in a wider window. Software: *Generate until* **STOP**, plus a system prompt: *“What follows is a conversation between a human and a helpful, knowledgeable and kind assistant…”* | A helpful-looking answer that ends in **STOP**. One claim is highlighted amber with the warning "Plausible, but from memory and potentially hallucinated" |
| 4 | Reasoning model | Thinks first, but still no sources | Same network and window. The system prompt is the stage 3 assistant text, shortened. Below it, a separate SPLIT OUTPUT panel (white, solid border) shows that the software turns **THINK** into *Private thoughts* and **ANSWER** into the answer. The special words are learned in training, so they are deliberately *not* in the system prompt | A dashed grey thought bubble (**THINK** *Harm in humans proven? Not yet → don't overclaim.*), then the answer bubble (**ANSWER** Microplastics are found in human tissue, but harm is still unclear. **STOP**), and the amber warning "More careful, but still answers from memory" |
| 5 | Tool-using agent | Can retrieve and act; needs oversight | Same network and window. The system prompt now opens with the same text (shortened to *“What follows is a conver…”*) and continues: *“The assistant can use these tools by writing* **TOOL** *+ tool + <input>:”*, followed by the available tools (*Search web*, *Read files*, *Execute code*, …). Both the tool list and how to call a tool are part of the system prompt. Under *Generate until* **STOP**, a teal PROGRAMS row shows the same tools as small program tiles (web, files, code): the programs the software actually runs when the model writes TOOL | A dashed THINK bubble (**THINK** *Need sources first.*) that contains one tool call (**TOOL** Search web *“microplastics health publication”*) and a hint of its results (↳ Paper 1: Microplastics in hu… / ↳ Paper 2: The effects of micro…). Then a longer answer bubble that cites them (**ANSWER** Microplastics are found in human blood and tissue (Paper 1). Whether they harm health is not yet proven (Paper 2). **STOP**), so it is clear the answer did not get worse, and the amber warning "Less likely to hallucinate, but still possible" |

## Ideas the figure is built to get across

- **One model throughout.** The network, software window and chat window look the same in every stage. Only
  the weights, the learned behaviour and the tools around the model change.
- **Next-token prediction is never replaced.** Later steps build on it. The figure no longer
  states this in words (the bottom band was removed); it shows it through the same model in every
  stage, so say it aloud.
- **The model learns where an answer ends.** In stages 1 and 2 the software cuts the output off
  after a fixed number of words. From stage 3 on, the model ends its own answer with STOP.
  STOP is a deliberate simplification: base models already have an end-of-document token from
  pre-training. What post-training adds is an end-of-turn token (e.g. `<|im_end|>`) that marks the
  end of the assistant's reply, so the model knows where *an answer* ends. That's why the stage 2 note
  describes what the base model does, rather than claiming it has no stop word.
- **The software adds a hidden system prompt.** From stage 3 on, the model doesn't see the user's question
  alone: the software puts a system prompt in front of it that casts the model as an assistant. In stage 5 it
  also lists the available tools and how to call them (TOOL + tool + <input>), which is how the model knows they exist.
  The THINK/ANSWER words in stage 4 are *not* in the system prompt: the model learns them in reasoning training,
  and the software only uses them to split the output.
  (The stage 3 wording is in the style of early assistant prompts; real system prompts are much longer.)
- **Reasoning is still next-token prediction.** A reasoning model writes private thoughts first,
  marked by THINK, then the answer marked by ANSWER. The software hides or collapses the thoughts.
  Real models use tokens like `<think>`…`</think>`; THINK/ANSWER is a simplification. Thinking makes
  answers more careful, but without tools they still come from memory.
- **Tools are called through special words.** The agent emits TOOL while thinking. The software runs the
  matching program and returns the result, and the loop continues. The tool is listed in the system prompt
  (so the model knows it exists) and is a program in the software (so it can actually run).
- **Fallibility is shown honestly.** Post-training doesn't remove hallucinations, and tools or
  citations don't guarantee truth: the agent still "needs oversight". The three amber warnings
  make the contrast explicit: stage 3 answers *from memory* (learned patterns) and may hallucinate;
  stage 4 thinks first and is more careful, but still answers from memory; stage 5 answers from retrieved sources, so hallucination is less likely but still possible.
- **No real citations.** All example outputs are schematic: there are no real paper titles,
  findings or reference numbers.

## Visual style

- White background (the figure is meant to sit on a white slide), navy text, and one blue accent for the progression (step cards,
  connectors, trained network).
- Teal for tool use, grey italic in a dashed bubble for private thoughts, amber for possible
  hallucinations, and dark chips for special words (STOP, THINK, ANSWER, TOOL).
- System sans-serif fonts. Body text is 18 units or larger, except the text inside the software windows (including the
  system prompt panels, 12–15) and the chip labels.
- Plain, editable SVG: real `<text>` elements, no images, `foreignObject`, filters or external
  fonts. Parts are grouped with named ids (`pretraining`, `posttraining`, `reasoning`, `tools`, `agent-loop`,
  `middle-row-model`, `model-1` … `model-5`, `system-prompt-3` … `system-prompt-5`, `output-split-4`, `programs-5`, `stage-1` … `stage-5`, `stage-4-thoughts`, `stage-5-thoughts`, `stage-5-tool-call`, `stage-5-tool-result`, `unsupported-claim`,
  `hallucination-warning`, `connectors`). Everything except the background
  sits in a `figure` group, shifted up by 66 units so the content is vertically centred. The steps row
  has extra space below it to separate it from the stage headers.

---
