"""
Interactive CLI: ask questions, get grounded answers, /dump the session
state at any point mid-conversation, and save a transcript on exit.
"""

from datetime import datetime

import config
from pipeline import answer_question
from session import Session


def main():
    print("Northbay Commerce AI - Q&A Assistant")
    print("Type your question, /dump to inspect session state, or /exit to quit.\n")

    session = Session()

    while True:
        question = input("> ").strip()
        if not question:
            continue

        if question.lower() in ("/exit", "/quit", "exit", "quit"):
            break

        if question.lower() == "/dump":
            print(session.dump())
            continue

        try:
            result = answer_question(question, history=session.get_history())
        except RuntimeError as e:
            # Both LLM providers failed for this turn (D-16). Report it and
            # keep the session alive - one bad turn shouldn't lose the
            # whole conversation and its transcript.
            print(f"\n[Error] {e}\n")
            continue

        session.add_turn(question, result)

        print(f"\n{result['answer']}")
        if result["abstained"]:
            print("(no confident answer found)")
        elif result["cited_docs"]:
            print(f"(sources: {', '.join(result['cited_docs'])})")
        print()

    if session.turns:
        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = config.TRANSCRIPTS_DIR / filename
        session.save_transcript(filepath)
        print(f"\nTranscript saved to {filepath}")


if __name__ == "__main__":
    main()
