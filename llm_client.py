"""
Single entry point for talking to an LLM: call_llm(system_prompt, user_prompt).

Groq is tried first. On a rate limit (429) or a server error (5xx), the same
request is retried once against Cerebras. Both providers speak the OpenAI
API shape, so switching between them is a base_url/key/model swap, not a
different code path - see config.py.
"""

import time

from openai import OpenAI, APIStatusError

import config
from tracing import log_call

_groq_client = OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
_cerebras_client = OpenAI(api_key=config.CEREBRAS_API_KEY, base_url=config.CEREBRAS_BASE_URL)


def _try_provider(client, model, provider_name, system_prompt, user_prompt):
    """One attempt against one provider. Returns (text, usage) or raises."""
    response = client.chat.completions.create(
        model=model,
        temperature=config.LLM_TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = response.choices[0].message.content
    return text, response.usage


def call_llm(system_prompt, user_prompt, purpose="general"):
    """Send one prompt to Groq, falling back to Cerebras on 429/5xx.

    purpose is only used for the trace log (e.g. "rerank", "generate") -
    it has no effect on the request itself.
    """
    providers = [
        (_groq_client, config.GROQ_MODEL, "groq"),
        (_cerebras_client, config.CEREBRAS_MODEL, "cerebras"),
    ]

    last_error = None

    for i, (client, model, name) in enumerate(providers):
        start = time.time()
        try:
            text, usage = _try_provider(client, model, name, system_prompt, user_prompt)
            latency = time.time() - start
            log_call(purpose, name, model, user_prompt, text, usage, latency)
            return text

        except APIStatusError as e:
            latency = time.time() - start
            last_error = e
            log_call(purpose, name, model, user_prompt, None, None, latency,
                      error=f"HTTP {e.status_code}: {e.message}")

            # Only 429 (rate limit) and 5xx (server error) are worth
            # retrying on the other provider. A 400 (bad request) would
            # fail identically on Cerebras, so don't waste the call.
            is_retryable = e.status_code == 429 or e.status_code >= 500
            is_last_provider = i == len(providers) - 1
            if not is_retryable or is_last_provider:
                raise RuntimeError(
                    f"Both providers failed. Last error from {name}: "
                    f"HTTP {e.status_code}: {e.message}"
                ) from last_error
            # else: loop continues to the next provider

    # Unreachable - the loop above always returns or raises - but keeps
    # the function's control flow explicit rather than falling off the end.
    raise RuntimeError("No provider was attempted.")


if __name__ == "__main__":
    print("Calling Groq (with Cerebras as fallback)...\n")

    reply = call_llm(
        system_prompt="You are a concise assistant. Answer in one short sentence.",
        user_prompt="What is 2 + 2?",
        purpose="smoke_test",
    )

    print(f"Reply: {reply}")
    print(f"\nCheck logs/trace.jsonl for the call record.")
