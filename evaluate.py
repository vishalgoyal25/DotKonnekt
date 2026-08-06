"""
Evaluation harness: runs every question in eval_set.json through the full
pipeline and scores it two ways - citation accuracy (deterministic, exact
doc-ID check) and an LLM-as-judge semantic comparison against a gold
answer. Prints a summary table and an overall pass rate.

This file has no knowledge of what's in docs/ - all corpus-specific
content lives in eval_set.json. Swap in a different eval_set.json written
against a different corpus and this file runs unchanged.
"""

import json
import time

import config
from llm_client import call_llm
from pipeline import answer_question

EVAL_SET_FILE = config.PROJECT_ROOT / "eval_set.json"

JUDGE_SYSTEM_PROMPT = """You are grading whether a generated answer matches \
a gold-standard reference answer for the same question.

Respond with exactly one word: "yes" if the generated answer is factually \
consistent with the gold answer, "partial" if it captures some but not all \
of the gold answer's substance, or "no" if it contradicts the gold answer \
or is missing entirely. No other text."""


def load_eval_set():
    with open(EVAL_SET_FILE, encoding="utf-8") as f:
        return json.load(f)


def check_citations(expected, actual):
    """Expected citations must all be present in what was actually cited -
    extra citations are not a failure, since a question can legitimately
    be supported by more than one relevant document."""
    return set(expected).issubset(set(actual))


def judge_answer(question, gold_answer, generated_answer):
    user_prompt = (
        f"Question: {question}\n\n"
        f"Gold answer: {gold_answer}\n\n"
        f"Generated answer: {generated_answer}"
    )
    verdict = call_llm(JUDGE_SYSTEM_PROMPT, user_prompt, purpose="judge")
    return verdict.strip().lower()


def run_eval():
    cases = load_eval_set()
    results = []

    for i, case in enumerate(cases, start=1):
        print(f"[{i}/{len(cases)}] {case['id']}: {case['question']}")

        result = answer_question(case["question"])

        if case.get("expect_abstain"):
            citation_ok = result["abstained"] is True
        else:
            citation_ok = check_citations(case["expected_citations"], result["cited_docs"])

        verdict = judge_answer(case["question"], case["gold_answer"], result["answer"])

        results.append({
            "id": case["id"],
            "question": case["question"],
            "citation_ok": citation_ok,
            "judge_verdict": verdict,
            "corrective_fired": result["corrective_fired"],
            "abstained": result["abstained"],
            "cited_docs": result["cited_docs"],
        })

        # The eval set alone is ~30-40 LLM calls in a burst - exactly
        # where a free tier throttles. Groq/Cerebras failover (D-01)
        # covers hard failures; this pacing reduces how often it needs to.
        time.sleep(1.5)

    return results


def print_report(results):
    print("\n" + "=" * 95)
    print(f"{'ID':<5} {'Citation':<9} {'Judge':<9} {'Corrective':<11} {'Abstained':<10} Question")
    print("-" * 95)

    for r in results:
        print(f"{r['id']:<5} {str(r['citation_ok']):<9} {r['judge_verdict']:<9} "
              f"{str(r['corrective_fired']):<11} {str(r['abstained']):<10} {r['question'][:42]}")

    total = len(results)
    citation_pass = sum(1 for r in results if r["citation_ok"])
    judge_yes = sum(1 for r in results if r["judge_verdict"] == "yes")
    judge_partial = sum(1 for r in results if r["judge_verdict"] == "partial")
    corrective_count = sum(1 for r in results if r["corrective_fired"])

    print("-" * 95)
    print(f"Citation accuracy      : {citation_pass}/{total} ({100 * citation_pass / total:.0f}%)")
    print(f"Judge verdict - yes    : {judge_yes}/{total}")
    print(f"Judge verdict - partial: {judge_partial}/{total}")
    print(f"Judge verdict - no     : {total - judge_yes - judge_partial}/{total}")
    print(f"Corrective loop fired  : {corrective_count}/{total} questions "
          f"({100 * corrective_count / total:.0f}%)")
    print("=" * 95)


if __name__ == "__main__":
    results = run_eval()
    print_report(results)
