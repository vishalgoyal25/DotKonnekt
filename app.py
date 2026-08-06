"""
Streamlit UI - same pipeline.py engine as main.py, in a browser instead of
a terminal. One file, no multi-page app, no custom CSS.

Every CLI behaviour from main.py is available here too:
  - ask a question, get a grounded answer with citations   -> the chat box
  - /dump  (inspect the full session state, on demand)      -> the checkbox below
  - /exit  (save a transcript, then end the session)        -> "Clear conversation"
                                                                 saves first, then resets

Uses Streamlit's native chat primitives (st.chat_input / st.chat_message)
rather than a plain text box + button: the input stays pinned at the
bottom and clears itself automatically after each question, so asking a
follow-up never means scrolling back to re-use the original box.
"""

from datetime import datetime

import streamlit as st

import config
from pipeline import answer_question
from session import Session

st.set_page_config(page_title="Northbay Commerce AI - Q&A Assistant")

st.title("Northbay Commerce AI - Q&A Assistant")
st.caption(
    "Answers are grounded only in Northbay's own (synthetic) documentation - "
    "no outside knowledge, and an honest abstain when the evidence is weak."
)

if "session" not in st.session_state:
    st.session_state.session = Session()
session = st.session_state.session

# Shown once, right after a save-then-clear action - set below, read here
# because Streamlit reruns the whole script top to bottom on every action.
if "last_saved_transcript" in st.session_state:
    st.success(f"Transcript saved to {st.session_state.pop('last_saved_transcript')}")

col1, col2 = st.columns(2)

with col1:
    # Mirrors the CLI's /exit: save a transcript first, then end the
    # session and start fresh - never silently discard a conversation
    # that was never saved anywhere.
    if st.button("Clear conversation"):
        if session.turns:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = config.TRANSCRIPTS_DIR / filename
            session.save_transcript(filepath)
            st.session_state.last_saved_transcript = str(filepath)
        st.session_state.session = Session()
        st.rerun()

with col2:
    # Mirrors the CLI's /dump - the full session state, on demand, without
    # resetting anything. A checkbox (not a button) so it stays open
    # across reruns instead of flashing once and disappearing.
    show_dump = st.checkbox("Show full session dump (/dump)")

if show_dump:
    with st.expander("Full session dump", expanded=True):
        st.code(session.dump(), language=None)

st.divider()

# Render every turn so far, oldest first - a chat reads top to bottom.
for turn in session.turns:
    with st.chat_message("user"):
        st.markdown(turn["question"])

    with st.chat_message("assistant"):
        st.markdown(turn["answer"])

        if turn["abstained"]:
            st.caption("No confident answer found.")
        elif turn["cited_docs"]:
            st.caption(f"Sources: {', '.join(turn['cited_docs'])}")

        with st.expander("How I got here"):
            st.write(f"**Query transformation:** {turn['transform_action']}")
            st.write(f"**Search queries used:** {turn['search_queries']}")
            st.write(f"**Candidates retrieved and fused:** {turn['num_candidates_fused']}")

            note = f'  (reformulated to: *"{turn["reformulated_query"]}"*)' if turn["reformulated_query"] else ""
            st.write(f"**Corrective loop fired:** {turn['corrective_fired']}{note}")

            st.write(f"**Top rerank score:** {turn['top_score']} "
                     f"(abstain threshold: {config.ABSTAIN_THRESHOLD})")
            st.write(f"**Abstained:** {turn['abstained']}")

            if turn["invalid_citations"]:
                st.warning(f"Fabricated citation caught and discarded: {turn['invalid_citations']}")

            st.write("**Retrieved sources, individually scored:**")
            for src in turn["sources"]:
                st.markdown(f"`{src['doc_id']}` — relevance score **{src['score']}**")
                st.caption(src["excerpt"] + "...")

# Pinned at the bottom, submits on Enter, clears itself after submission -
# this is what removes the "go back and overlap the original box" problem.
question = st.chat_input("Ask a question about Northbay Commerce AI...")

if question:
    with st.spinner("Thinking..."):
        try:
            result = answer_question(question, history=session.get_history())
            session.add_turn(question, result)
            st.rerun()  # redraw so the new turn appears via the loop above
        except RuntimeError as e:
            # Both LLM providers failed for this turn (D-16) - show it
            # inline, without adding a turn, so the user can just retry.
            st.error(f"Both providers failed for this question: {e}")
