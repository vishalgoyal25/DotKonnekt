"""
Proves both providers individually respond, before anything is built on top
of them. call_llm() only shows Groq succeeding (it's tried first) unless
Groq happens to fail - this script calls each provider directly so a
Cerebras key problem doesn't stay hidden until the day failover is needed.
"""

from openai import OpenAI

import config


def ping(label, api_key, base_url, model):
    if not api_key:
        print(f"{label}: SKIPPED - no API key in .env\n")
        return

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=config.LLM_TEMPERATURE,
        messages=[{"role": "user", "content": "Reply with just the word: ready"}],
    )
    reply = response.choices[0].message.content
    print(f"{label}: {reply.strip()}\n")


if __name__ == "__main__":
    print("Pinging Groq...")
    ping("Groq", config.GROQ_API_KEY, config.GROQ_BASE_URL, config.GROQ_MODEL)

    print("Pinging Cerebras...")
    ping("Cerebras", config.CEREBRAS_API_KEY, config.CEREBRAS_BASE_URL, config.CEREBRAS_MODEL)
