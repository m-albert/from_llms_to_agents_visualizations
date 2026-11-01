"""
Next-word distributions for the agentic stage scenes, from small Qwen
models run locally. The texts are the models' own greedy outputs (most
likely token each time, no repetition penalty). For each word we store
the probability of that word (its first token), the top other candidates,
and the probabilities of the special words STOP (end of turn / end of
text), TOOL (start of a tool call), THINK and ANSWER (start and end of the
private thoughts of a reasoning model).

Stages 4 and 5 use a reasoning model (Qwen3), whose thoughts run to a
hundred words or more. Only some sentences of them get a record; the
words in between are stored as {"skip": n} (the scenes show "…").

    uv run python tools/compute_distributions.py

writes data/agentic_distributions.json.
"""
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

QUESTION = "What do recent papers say about microplastics and health?"
OUT = Path(__file__).parents[1] / "data" / "agentic_distributions.json"
N_OTHERS = 5

BASE_MODEL = "Qwen/Qwen2.5-0.5B"
CHAT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
REASONING_MODEL = "Qwen/Qwen3-1.7B"
SYSTEM_3 = "You are a helpful assistant. Answer in one short sentence."
SYSTEM_4 = "You are a helpful assistant. Answer in under 25 words."
SYSTEM_5 = (
    "You are a helpful assistant. Use tools when helpful. Answer in under 30 words "
    "and cite sources as (Author et al., year)."
)
# Sentences of the thoughts that get a record (matched by their start);
# the first sentence is always shown
SHOWN_4 = ["But I should mention"]
SHOWN_5_CALL = ["I'll use that"]
SHOWN_5_AFTER = ["The search results show"]
# What the search tool returns: two real papers, title + one-line finding
PAPERS = [
    dict(
        ref="Leslie et al., 2022",
        title="Discovery and quantification of plastic particle pollution in human blood",
        finding="plastic particles found in the blood of 17 of 22 healthy donors.",
    ),
    dict(
        ref="Marfella et al., 2024",
        title="Microplastics and Nanoplastics in Atheromas and Cardiovascular Events",
        finding="patients with plastic in artery plaque had a higher risk of heart attack, stroke or death.",
    ),
]
RESULT_5 = "\n".join(
    f"[{n + 1}] {p['ref']}, {p['title']}: {p['finding']}" for n, p in enumerate(PAPERS)
)

TOOLS = [
    {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": {arg: {"type": "string"}}, "required": [arg]},
    }}
    for name, desc, arg in [
        ("search_web", "Search the web", "query"),
        ("read_file", "Read a file", "path"),
        ("run_code", "Execute Python code", "code"),
    ]
]
# How the scenes show the tool names
TOOL_LABELS = {"search_web": "Search web", "read_file": "Read files", "run_code": "Execute code"}


def load(name):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)
    model.eval()
    return tok, model


def encode_chat(tok, messages, tools=None, **kwargs):
    text = tok.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False, **kwargs)
    return tok.encode(text)


def next_probs(model, ids):
    with torch.no_grad():
        return model(torch.tensor([ids])).logits[0, -1].float().softmax(-1)


def step(tok, model, ids, word, word_ids, specials, word_starts_with_space=True):
    """Distribution before `word` (given as its token ids); returns (record, ids + word_ids)."""
    probs = next_probs(model, ids)
    first_id = word_ids[0]
    special_ids = set(specials.values()) | set(tok.all_special_ids)
    others, seen = [], {word.strip("“”\"").lower()}
    for i in probs.argsort(descending=True)[:200].tolist():
        if i == first_id or i in special_ids:
            continue
        raw = tok.decode([i])
        label = raw.strip()
        # Alternatives shown are tokens that start a word (no sub-word pieces)
        starts_word = raw.startswith(" ") or not word_starts_with_space
        if not starts_word or not label.isascii() or not label.isalpha() or label.lower() in seen:
            continue
        seen.add(label.lower())
        others.append([label, round(probs[i].item(), 5)])
        if len(others) == N_OTHERS:
            break
    record = dict(
        word=word,
        p=round(probs[first_id].item(), 5),
        others=others,
        special={name: round(probs[i].item(), 6) for name, i in specials.items()},
    )
    return record, ids + word_ids


def run(tok, model, ids, words, specials, first_space=True):
    """Teacher-force the words one by one; special words map to their token."""
    records = []
    for n, word in enumerate(words):
        if word in specials:
            word_ids = [specials[word]]
        else:
            word_ids = tok.encode(word if (n == 0 and not first_space) else " " + word)
        record, ids = step(tok, model, ids, word, word_ids, specials, n > 0 or first_space)
        records.append(record)
    return records, ids


def run_thought(tok, model, ids, thought, shown, specials, show_first=True):
    """
    Teacher-force the model's own thoughts. Sentences that start with one
    of `shown` (and the first, if show_first) get a record per word; runs
    of other words become {"skip": n}.
    """
    body = thought.strip()
    lead = thought[:len(thought) - len(thought.lstrip())]
    trail = thought[len(thought.rstrip()):]
    ids = ids + tok.encode(lead)
    records = []
    show = False
    pieces = re.findall(r"\s*\S+", body)
    for n, piece in enumerate(pieces):
        word = piece.strip()
        if n == 0 or pieces[n - 1].strip()[-1] in ".?!":
            rest = "".join(pieces[n:]).lstrip()
            show = (n == 0 and show_first) or any(rest.startswith(s) for s in shown)
        word_ids = tok.encode(piece)
        if show:
            record, ids = step(tok, model, ids, word, word_ids, specials, piece.startswith(" "))
            records.append(record)
        else:
            ids = ids + word_ids
            if records and "skip" in records[-1]:
                records[-1]["skip"] += 1
            else:
                records.append(dict(skip=1))
    return records, ids + tok.encode(trail)


def greedy(tok, model, ids, max_new_tokens):
    out = model.generate(
        torch.tensor([ids]), max_new_tokens=max_new_tokens,
        do_sample=False, repetition_penalty=1.0,
        attention_mask=torch.ones(1, len(ids), dtype=torch.long),
    )
    return tok.decode(out[0][len(ids):], skip_special_tokens=False)


def main():
    data = {}

    # Stage 2: base model continues the bare question. Its top pick is
    # " Micro" (11%); we take its second, " What" (10%), and from there its
    # most likely word each time: it repeats the question. (The smaller base
    # model shows this more clearly than the 1.5B one.)
    tok, model = load(BASE_MODEL)
    ids = tok.encode(QUESTION)
    text = "What" + greedy(tok, model, ids + tok.encode(" What"), 30)
    data["stage2"], _ = run(tok, model, ids, text.split()[:10], {})

    # Stage 3: chat model, its own answer, then STOP
    tok, model = load(CHAT_MODEL)
    stop = tok.convert_tokens_to_ids("<|im_end|>")
    messages = [
        {"role": "system", "content": SYSTEM_3},
        {"role": "user", "content": QUESTION},
    ]
    ids = encode_chat(tok, messages)
    answer = greedy(tok, model, ids, 80).split("<|im_end|>")[0].strip()
    data["stage3_text"] = dict(system=SYSTEM_3, answer=answer)
    data["stage3"], _ = run(tok, model, ids, answer.split() + ["STOP"], {"STOP": stop}, first_space=False)

    # Stages 4 and 5: a reasoning model. THINK and ANSWER are its real
    # <think> and </think> tokens
    tok, model = load(REASONING_MODEL)
    think, answer_start = (tok.convert_tokens_to_ids(t) for t in ["<think>", "</think>"])
    stop = tok.convert_tokens_to_ids("<|im_end|>")
    tool = tok.convert_tokens_to_ids("<tool_call>")

    def split_thought(raw):
        thought, rest = raw.split("<think>")[1].split("</think>")
        return thought, rest

    # Stage 4: thinks, then answers
    specials = {"THINK": think, "ANSWER": answer_start, "STOP": stop}
    messages = [
        {"role": "system", "content": SYSTEM_4},
        {"role": "user", "content": QUESTION},
    ]
    ids = encode_chat(tok, messages, enable_thinking=True)
    thought, rest = split_thought(greedy(tok, model, ids, 600))
    answer = rest.split("<|im_end|>")[0].strip()
    records = []
    record, ids = step(tok, model, ids, "THINK", [think], specials, False)
    records.append(record)
    thought_records, ids = run_thought(tok, model, ids, thought, SHOWN_4, specials)
    records += thought_records
    record, ids = step(tok, model, ids, "ANSWER", [answer_start], specials, False)
    records.append(record)
    ids += tok.encode("\n\n")
    answer_records, _ = run(tok, model, ids, answer.split() + ["STOP"], specials, first_space=False)
    data["stage4_text"] = dict(system=SYSTEM_4, thought=thought.strip(), answer=answer)
    data["stage4"] = records + answer_records

    # Stage 5: tools listed in the system prompt. The model thinks, then
    # calls a tool in its real format <tool_call>{"name": ..., "arguments": {...}}.
    # Qwen3 closes its thoughts before the call and opens new ones after the
    # result; the scene keeps call and result inside the private thoughts
    # (as chat apps show them), so those two tokens are not shown
    specials = {"THINK": think, "ANSWER": answer_start, "TOOL": tool, "STOP": stop}
    messages[0]["content"] = SYSTEM_5
    ids = encode_chat(tok, messages, tools=TOOLS, enable_thinking=True)
    thought, rest = split_thought(greedy(tok, model, ids, 600))
    call_json = json.loads(rest.split("<tool_call>")[1].split("</tool_call>")[0])
    name, query = call_json["name"], call_json["arguments"]["query"]
    call = []
    record, ids = step(tok, model, ids, "THINK", [think], specials, False)
    call.append(record)
    thought_records, ids = run_thought(tok, model, ids, thought, SHOWN_5_CALL, specials)
    call += thought_records
    ids += [answer_start] + tok.encode("\n\n")
    record, ids = step(tok, model, ids, "TOOL", [tool], specials, False)
    call.append(record)
    ids += tok.encode('\n{"name": "')
    record, ids = step(tok, model, ids, TOOL_LABELS[name], tok.encode(name), specials, False)
    call.append(record)
    ids += tok.encode('", "arguments": {"query": "')
    records, ids = run(tok, model, ids, query.split(), specials, first_space=False)
    # Shown as: TOOL Search web “query words”
    records[0]["word"] = "“" + records[0]["word"]
    records[-1]["word"] = records[-1]["word"] + "”"
    call += records
    data["stage5_call"] = call

    # The software runs the tool and adds its result; the model thinks again
    ids += tok.encode(
        '"}}\n</tool_call><|im_end|>\n<|im_start|>user\n<tool_response>\n'
        + RESULT_5 + "\n</tool_response><|im_end|>\n<|im_start|>assistant\n"
    )
    thought_after, rest = split_thought(greedy(tok, model, ids, 600))
    # Its most likely next word after the first paragraph is a line break
    # (54%), followed by the same citations again; we take STOP (46%) there
    answer = rest.split("<|im_end|>")[0].strip().split("\n")[0].strip()
    ids += [think]
    records, ids = run_thought(tok, model, ids, thought_after, SHOWN_5_AFTER, specials, show_first=False)
    record, ids = step(tok, model, ids, "ANSWER", [answer_start], specials, False)
    records.append(record)
    ids += tok.encode("\n\n")
    answer_records, _ = run(tok, model, ids, answer.split() + ["STOP"], specials, first_space=False)
    data["stage5_text"] = dict(
        system=SYSTEM_5, thought=thought.strip(), tool=TOOL_LABELS[name], query=query,
        papers=PAPERS, thought_after=thought_after.strip(), answer=answer,
    )
    data["stage5_answer"] = records + answer_records

    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    for key, records in data.items():
        print(key)
        if key.endswith("_text"):
            print("  ", records)
            continue
        for r in records:
            if "skip" in r:
                print(f"  {'…':>14} (+{r['skip']} words)")
                continue
            print(f"  {r['word']:>14} {r['p']:.3f}  {r['special']}  {[o[0] for o in r['others'][:4]]}")


if __name__ == "__main__":
    main()
