"""
Next-word distributions for the agentic stage scenes, from small Qwen
models run locally. The texts are the models' own greedy outputs (most
likely token each time, no repetition penalty). For each word we store
the probability of that word (its first token), the top other candidates,
and the probabilities of the special words STOP (end of turn / end of
text) and TOOL (start of a tool call).

    uv run python tools/compute_distributions.py

writes data/agentic_distributions.json.
"""
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

QUESTION = "What do recent papers say about microplastics and health?"
OUT = Path(__file__).parents[1] / "data" / "agentic_distributions.json"
N_OTHERS = 5

BASE_MODEL = "Qwen/Qwen2.5-0.5B"
CHAT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SYSTEM_3 = "You are a helpful assistant. Answer in one short sentence."
SYSTEM_4 = (
    "You are a helpful assistant. Use tools when helpful. Answer in under 20 words "
    "and end with one source in parentheses, e.g. (Smith et al., 2020)."
)
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
RESULT_4 = "\n".join(
    f"[{n + 1}] {p['ref']}, {p['title']}: {p['finding']}" for n, p in enumerate(PAPERS)
)

TOOLS = [
    {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": {"input": {"type": "string"}}, "required": ["input"]},
    }}
    for name, desc in [
        ("Search", "Search scientific papers"),
        ("Read", "Read a file"),
        ("Code", "Run Python code"),
    ]
]


def load(name):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)
    model.eval()
    return tok, model


def encode_chat(tok, messages, tools=None):
    text = tok.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
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
    tool = tok.convert_tokens_to_ids("<tool_call>")
    messages = [
        {"role": "system", "content": SYSTEM_3},
        {"role": "user", "content": QUESTION},
    ]
    ids = encode_chat(tok, messages)
    answer = greedy(tok, model, ids, 80).split("<|im_end|>")[0].strip()
    data["stage3_text"] = dict(system=SYSTEM_3, answer=answer)
    data["stage3"], _ = run(tok, model, ids, answer.split() + ["STOP"], {"STOP": stop}, first_space=False)

    # Stage 4: tools listed in the system prompt. The model's own tool call,
    # in its real format <tool_call>{"name": ..., "arguments": {...}}
    specials = {"STOP": stop, "TOOL": tool}
    messages[0]["content"] = SYSTEM_4
    ids = encode_chat(tok, messages, tools=TOOLS)
    raw_call = greedy(tok, model, ids, 60)
    assert raw_call.startswith("<tool_call>"), raw_call
    call_json = json.loads(raw_call.split("<tool_call>")[1].split("</tool_call>")[0])
    name, query = call_json["name"], call_json["arguments"]["input"]
    call = []
    record, ids = step(tok, model, ids, "TOOL", [tool], specials, False)
    call.append(record)
    ids += tok.encode('\n{"name": "')
    record, ids = step(tok, model, ids, name, tok.encode(name), specials, False)
    call.append(record)
    ids += tok.encode('", "arguments": {"input": "')
    records, ids = run(tok, model, ids, query.split(), specials, first_space=False)
    call += records
    # Shown as: TOOL Search “query words”
    call[2]["word"] = "“" + call[2]["word"]
    call[-1]["word"] = call[-1]["word"] + "”"
    data["stage4_call"] = call

    messages_after = messages + [
        {"role": "assistant", "content": "", "tool_calls": [
            {"type": "function", "function": {"name": name, "arguments": {"input": query}}}
        ]},
        {"role": "tool", "content": RESULT_4},
    ]
    ids = encode_chat(tok, messages_after, tools=TOOLS)
    answer = greedy(tok, model, ids, 80).split("<|im_end|>")[0].strip()
    data["stage4_text"] = dict(system=SYSTEM_4, tool=name, query=query, papers=PAPERS, answer=answer)
    data["stage4_answer"], _ = run(tok, model, ids, answer.split() + ["STOP"], specials, first_space=False)

    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    for key, records in data.items():
        print(key)
        if key.endswith("_text"):
            print("  ", records)
            continue
        for r in records:
            print(f"  {r['word']:>14} {r['p']:.3f}  {r['special']}  {[o[0] for o in r['others'][:4]]}")


if __name__ == "__main__":
    main()
