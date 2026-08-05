"""
In-memory conversation state - a Python list held for the life of the
process, no database. Stores every turn's full pipeline output, not just
the final answer, so the session is inspectable at any point (CLAUDE.md
Constraint 1), not just at the end.
"""

from datetime import datetime

import config


class Session:
    def __init__(self):
        self.turns = []

    def add_turn(self, question, result):
        """result: the dict returned by pipeline.answer_question()."""
        self.turns.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            **result,
        })

    def get_history(self):
        """Formatted for query_transform.py's history parameter - the last
        HISTORY_TURNS question/answer pairs, oldest first."""
        recent = self.turns[-config.HISTORY_TURNS:]
        return [{"question": t["question"], "answer": t["answer"]} for t in recent]

    def dump(self):
        """Full, human-readable record of every turn, including the
        intermediate steps a plain Q&A log would hide - the printable
        state dump Constraint 1 requires."""
        if not self.turns:
            return "(no turns yet)"

        lines = []
        for i, t in enumerate(self.turns, start=1):
            lines.append("=" * 70)
            lines.append(f"Turn {i}  [{t['timestamp']}]")
            lines.append(f"Question: {t['question']}")
            lines.append(f"  Transform action : {t['transform_action']}")
            lines.append(f"  Search queries   : {t['search_queries']}")
            lines.append(f"  Candidates fused : {t['num_candidates_fused']}")
            note = f' (reformulated: "{t["reformulated_query"]}")' if t["reformulated_query"] else ""
            lines.append(f"  Corrective loop  : {t['corrective_fired']}{note}")
            lines.append(f"  Top score        : {t['top_score']}  (threshold: {config.ABSTAIN_THRESHOLD})")
            lines.append(f"  Abstained        : {t['abstained']}")
            lines.append(f"  Cited docs       : {t['cited_docs']}")
            if t["invalid_citations"]:
                lines.append(f"  Invalid citations flagged: {t['invalid_citations']}")
            lines.append(f"\nAnswer: {t['answer']}\n")
        return "\n".join(lines)

    def save_transcript(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.dump())
