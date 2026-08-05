"""
Trace log for every LLM call.

One JSON line per call, appended to logs/trace.jsonl. Hand-rolled on purpose:
the requirement is basic observability, not a tracing platform.
"""

import json
from datetime import datetime

from config import TRACE_FILE

# Prompts get long once retrieved context is stuffed in - a rerank prompt with
# 8 candidates runs to thousands of characters. Storing a preview plus the full
# length keeps the log readable while still showing what was actually sent.
PREVIEW_CHARS = 300


def log_call(purpose, provider, model, prompt, response, usage, latency_s,
             error=None):
    """Append one call record to the trace file.

    purpose  - which pipeline step made the call: transform, rerank,
               generate, corrective, judge
    usage    - the `usage` object from the API response, or None if the call
               failed. Token counts come from here and nowhere else: tiktoken
               is OpenAI's tokenizer and would report wrong numbers for
               gpt-oss.
    """
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "purpose": purpose,
        "provider": provider,
        "model": model,
        "prompt_preview": prompt[:PREVIEW_CHARS],
        "prompt_chars": len(prompt),
        "response_chars": len(response) if response else 0,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "latency_s": round(latency_s, 4),
    }

    if error:
        record["error"] = error

    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    log_call(
        purpose="self_test",
        provider="none",
        model="none",
        prompt="Does the trace file get written correctly?",
        response="Yes.",
        usage=None,
        latency_s=0.123,
    )

    print(f"Wrote a test record to {TRACE_FILE}\n")
    print("Last line in the file:")
    with open(TRACE_FILE, encoding="utf-8") as f:
        print(" ", f.readlines()[-1].strip())
