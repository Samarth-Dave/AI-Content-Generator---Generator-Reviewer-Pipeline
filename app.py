from __future__ import annotations

import streamlit as st

from orchestrator_v2 import run_pipeline


st.set_page_config(page_title="Eklavya AI Content Pipeline", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stage-card {
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: #ffffff;
        margin-bottom: 0.85rem;
    }
    .stage-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    .stage-note {
        color: #555;
        font-size: 0.93rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AI Content Generator")
st.caption("Generator Agent -> Reviewer Agent -> bounded refinement -> audit trail")

with st.sidebar:
    st.subheader("Run settings")
    user_id = st.text_input("User ID", value="default_user")
    st.info("The Part 2 pipeline always uses the governed schema and bounded orchestration path.")

with st.form("pipeline_form"):
    left, right = st.columns(2)
    grade = left.selectbox("Grade", options=list(range(1, 13)), index=4)
    topic = right.text_input("Topic", value="Fractions as parts of a whole")
    submitted = st.form_submit_button("Run pipeline")


def render_output(title: str, explanation: str, mcqs) -> None:
    st.markdown(f"### {title}")
    st.write(explanation)
    for index, mcq in enumerate(mcqs, start=1):
        with st.expander(f"Q{index}. {mcq.question}"):
            for option in mcq.options:
                marker = "Correct" if option == mcq.options[mcq.correct_index] else "Option"
                st.write(f"- {marker}: {option}")
            st.info(f"Answer index: {mcq.correct_index}")


def render_agent_timeline(result) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="stage-card"><div class="stage-title">1. Generator Agent</div><div class="stage-note">Drafts the explanation, MCQs, and teacher notes for the selected grade and topic.</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="stage-card"><div class="stage-title">2. Reviewer Agent</div><div class="stage-note">Scores age appropriateness, correctness, clarity, and coverage.</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        note = "Runs only if the final status is approved." if result.final.tags is not None else "Stops after bounded review/refinement cycles."
        st.markdown(
            f'<div class="stage-card"><div class="stage-title">3. Tagger / Finalization</div><div class="stage-note">{note}</div></div>',
            unsafe_allow_html=True,
        )


if submitted:
    try:
        progress = st.progress(0, text="Starting agent pipeline...")

        with st.status("Pipeline working", expanded=True) as pipeline_status:
            pipeline_status.write(f"Reason: generate governed content for Grade {grade} on the topic '{topic}'.")
            pipeline_status.write("Structured input: {grade, topic, user_id}.")
            progress.progress(30, text="Running the governed generator/reviewer pipeline...")
            result = run_pipeline(grade=grade, topic=topic, user_id=user_id)
            pipeline_status.update(label="Pipeline complete", state="complete")

        progress.progress(100, text="Pipeline finished.")

        render_agent_timeline(result)

        left, right = st.columns(2)
        with left:
            st.markdown("### 1. Final Content")
            if result.final.content is not None:
                render_output("Final Content", result.final.content.explanation.text, result.final.content.mcqs)
            else:
                st.info("No final content was produced because generation failed schema validation.")

        with right:
            st.markdown("### 2. Final Decision")
            st.write(f"Status: {result.final.status}")
            if result.final.tags is not None:
                st.json(result.final.tags.model_dump(mode="json"))

        st.markdown("### Run Artifact")
        st.json(result.model_dump(mode="json", by_alias=True))
    except Exception as exc:  # pragma: no cover - UI safety net
        st.error(f"Unexpected error: {exc}")
