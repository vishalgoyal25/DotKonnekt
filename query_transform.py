"""
Query transformation: rewrite a history-dependent question into a standalone
one, or decompose a genuinely multi-part question into sub-questions.
Returns the question unchanged when neither applies - the prompt explicitly
allows this no-op, otherwise the model tends to split or rewrite every
question, even ones that were already fine. See DECISIONS.md D-10.
"""

import json

import config
from llm_client import call_llm

SYSTEM_PROMPT = """You transform a user's question before it is used for \
document retrieval.

Given the question and, if provided, recent conversation history, decide \
which ONE of these applies:

1. "rewrite" - the question depends on prior conversation (pronouns like \
"it"/"they", phrases like "what about X", a missing subject). Rewrite it \
into a single, standalone question that would make sense with no prior \
context.
2. "decompose" - the question genuinely asks about more than one distinct \
thing, and answering it requires looking up separate pieces of \
information. Split it into standalone sub-questions.
3. "unchanged" - the question is already specific, standalone, and asks \
about one thing. Return it exactly as given. Do NOT force a rewrite or \
split when the question is already fine as-is - this is the most common \
case, not the exception.

Respond with ONLY valid JSON, no other text, no markdown fences:
{"action": "rewrite" | "decompose" | "unchanged", "queries": ["..."]}

"queries" holds one item for "rewrite" and "unchanged", and up to """ + \
    str(config.MAX_SUB_QUESTIONS) + """ items for "decompose"."""


def _format_history(history):
    if not history:
        return "(none - this is the first question)"
    recent = history[-config.HISTORY_TURNS:]
    lines = []
    for turn in recent:
        lines.append(f'Q: {turn["question"]}')
        lines.append(f'A: {turn["answer"]}')
    return "\n".join(lines)


def _parse_response(text):
    # gpt-oss sometimes wraps JSON in ```json fences despite being told not
    # to - strip them before parsing rather than treating it as a failure.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    return json.loads(cleaned)


def transform_query(question, history=None):
    """Returns {"original": ..., "action": ..., "queries": [...]}.

    On any parse failure, falls back to "unchanged" with the original
    question - a broken transform step should degrade retrieval quality,
    not crash the pipeline.
    """
    user_prompt = (
        f"Conversation history:\n{_format_history(history)}\n\n"
        f"Current question: {question}"
    )

    raw = call_llm(SYSTEM_PROMPT, user_prompt, purpose="transform")

    try:
        parsed = _parse_response(raw)
        action = parsed.get("action", "unchanged")
        queries = parsed.get("queries") or [question]
        if not isinstance(queries, list) or not queries:
            queries = [question]
    except (json.JSONDecodeError, AttributeError, TypeError):
        action, queries = "unchanged", [question]

    return {"original": question, "action": action, "queries": queries}


if __name__ == "__main__":
    print("Test 1: simple standalone question (expect: unchanged)")
    result = transform_query("What connectors does Northbay support?")
    print(f"  {result}\n")

    print("Test 2: history-dependent follow-up (expect: rewrite)")
    history = [{
        "question": "What's included in the Growth tier?",
        "answer": "Up to 6 agentic templates, 10 data sources, priority "
                  "support, a 14-day trial, and one FDE engagement up to 8 weeks.",
    }]
    result = transform_query("What about Enterprise?", history=history)
    print(f"  {result}\n")

    print("Test 3: genuinely multi-part question (expect: decompose)")
    result = transform_query(
        "What is the trial length, and what does the Growth tier include?"
    )
    print(f"  {result}\n")
