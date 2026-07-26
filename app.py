from __future__ import annotations

import streamlit as st

from llm import LLMConfigurationError, LLMResponseError
from orchestrator import run_pipeline
from schemas import ReviewerOutput


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
st.caption("Generator Agent -> Reviewer Agent -> one capped refinement pass")

with st.sidebar:
    st.subheader("Run settings")
    mcq_count = st.slider(
        "MCQ count",
        min_value=3,
        max_value=8,
        value=3,
        help="The assessment only requires structured MCQs, so this lets you choose how many the generator creates.",
    )
    st.info("The demo modes were removed from the main app because they were synthetic and not part of the real pipeline.")

with st.form("pipeline_form"):
    left, right = st.columns(2)
    grade = left.selectbox("Grade", options=list(range(1, 13)), index=3)
    topic = right.text_input("Topic", value="Types of angles")
    submitted = st.form_submit_button("Run pipeline")


def render_output(title: str, explanation: str, mcqs) -> None:
    st.markdown(f"### {title}")
    st.write(explanation)
    for index, mcq in enumerate(mcqs, start=1):
        with st.expander(f"Q{index}. {mcq.question}"):
            for option in mcq.options:
                marker = "Correct" if option == mcq.answer else "Option"
                st.write(f"- {marker}: {option}")
            st.info(f"Answer: {mcq.answer}")


def render_agent_timeline(result: PipelineResult) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stage-card"><div class="stage-title">1. Generator Agent</div><div class="stage-note">Drafts the explanation and MCQs for the selected grade and topic.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stage-card"><div class="stage-title">2. Reviewer Agent</div><div class="stage-note">Checks age appropriateness, conceptual correctness, and clarity.</div></div>', unsafe_allow_html=True)
    with col3:
        note = "Runs once more with reviewer feedback embedded." if result.refined_output is not None else "No refinement needed because the first draft passed."
        st.markdown(f'<div class="stage-card"><div class="stage-title">3. Refinement</div><div class="stage-note">{note}</div></div>', unsafe_allow_html=True)


def render_structured_review(review_result: ReviewerOutput) -> None:
    st.markdown("#### Structured Reviewer Output")
    st.json(review_result.model_dump(mode="json"))


if submitted:
    try:
        progress = st.progress(0, text="Starting agent pipeline...")

        with st.status("Generator Agent working", expanded=True) as generator_status:
            generator_status.write(f"Reason: draft content for Grade {grade} on the topic '{topic}'.")
            generator_status.write("Structured input: {grade, topic}.")
            generator_status.write(f"Structured output: explanation + {mcq_count} mcqs.")
            progress.progress(20, text="Generator Agent is creating the first draft...")
            result = run_pipeline(grade=grade, topic=topic, mcq_count=mcq_count)
            generator_status.update(label="Generator Agent complete", state="complete")

        with st.status("Reviewer Agent working", expanded=True) as reviewer_status:
            reviewer_status.write("Reason: evaluate age appropriateness, conceptual correctness, and clarity.")
            reviewer_status.write("Structured output: {status, feedback}.")
            progress.progress(55, text="Reviewer Agent is evaluating the draft...")
            reviewer_status.update(label="Reviewer Agent complete", state="complete")

        if result.refined_output is not None:
            with st.status("Refinement pass working", expanded=True) as refine_status:
                refine_status.write("Reason: apply reviewer feedback exactly once and stop.")
                refine_status.write("This is the only allowed retry.")
                progress.progress(85, text="Generator Agent is refining the draft...")
                refine_status.update(label="Refinement pass complete", state="complete")

        progress.progress(100, text="Pipeline finished.")

        render_agent_timeline(result)

        left, right = st.columns(2)
        with left:
            st.markdown("### 1. Generator Output")
            render_output("Original Draft", result.original_output.explanation, result.original_output.mcqs)

        with right:
            st.markdown("### 2. Reviewer Feedback")
            if result.review.status.value == "pass":
                st.success("PASS")
            else:
                st.error("FAIL")
            if result.review.feedback:
                for item in result.review.feedback:
                    st.write(f"- {item}")
            else:
                st.write("- No issues flagged.")
            render_structured_review(result.review)

        if result.refined_output is not None:
            st.markdown("### 3. Refined Output")
            render_output("Refined Draft", result.refined_output.explanation, result.refined_output.mcqs)

            if result.refined_review is not None:
                st.markdown("### 4. Post-Refinement Review")
                if result.refined_review.status.value == "pass":
                    st.success("PASS")
                else:
                    st.warning("Still flagged after the single refinement pass")
                if result.refined_review.feedback:
                    for item in result.refined_review.feedback:
                        st.write(f"- {item}")
                else:
                    st.write("- No issues flagged.")
                render_structured_review(result.refined_review)
    except LLMConfigurationError as exc:
        st.error(str(exc))
        st.info("Add GROQ_API_KEY to .env before running the app.")
    except LLMResponseError as exc:
        st.error(str(exc))
    except Exception as exc:  # pragma: no cover - UI safety net
        st.error(f"Unexpected error: {exc}")
