"""StudyBuddy AI - an AI-powered study assistant for college students."""

from datetime import date

import streamlit as st

from gemini_helper import get_gemini_response
from prompts import (
    MAX_INPUT_CHARS,
    explain_concept_prompt,
    generate_flashcards_prompt,
    generate_quiz_prompt,
    improve_answer_prompt,
    study_planner_prompt,
    summarize_notes_prompt,
)

# Basic page setup: title, icon and a wide layout that works on desktop and mobile
st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🎓",
    layout="wide",
)

# ---------------------------------------------------------------- app header
st.title("🎓 StudyBuddy AI")
st.subheader("Your AI-Powered Study Assistant")
st.caption("Learn smarter, revise faster, and improve your answers with AI.")

# ---------------------------------------------------------------- input area
user_input = st.text_area(
    "Your study material",
    placeholder="Enter your notes, question, concept, or answer here...",
    height=220,
)

# Friendly guard against oversized requests (they slow the AI down)
if len(user_input) > MAX_INPUT_CHARS:
    st.warning(
        f"⚠️ Your input is {len(user_input)} characters. Please keep it under "
        f"{MAX_INPUT_CHARS} characters for faster, more reliable results."
    )

# ------------------------------------------------------------- feature cards
FEATURES = [
    "📝 Summarize Notes",
    "💡 Explain Concept",
    "❓ Generate Quiz",
    "✍️ Improve Answer",
    "🗂️ Generate Flashcards",
    "📅 Study Planner",
]

selected_feature = st.pills("Choose a feature", FEATURES, default=FEATURES[0])

# -------------------------------------------------------------- AI output box
st.markdown("---")
st.header("🤖 AI Output")

def build_prompt(feature: str, text: str) -> str:
    """Pick the right prompt template for the selected feature."""
    if feature == "📝 Summarize Notes":
        return summarize_notes_prompt(text)
    if feature == "💡 Explain Concept":
        return explain_concept_prompt(text)
    if feature == "❓ Generate Quiz":
        return generate_quiz_prompt(text)
    if feature == "✍️ Improve Answer":
        return improve_answer_prompt(text)
    if feature == "🗂️ Generate Flashcards":
        return generate_flashcards_prompt(text)
    return text


def run_study_planner() -> None:
    """Study planner: collects exam details, validates them and builds a plan."""
    st.markdown("Fill in your exam details below to get a personalized schedule.")

    subjects = st.text_input(
        "Subjects (comma-separated)",
        placeholder="e.g. Data Structures, DBMS, Mathematics",
    )
    topics = st.text_area(
        "Topics to cover (comma-separated)",
        placeholder="e.g. Linked Lists, Normalization, Probability",
        height=100,
    )
    left, right = st.columns(2)
    exam_date = left.date_input("Exam date", min_value=date.today())
    hours = right.number_input(
        "Available study hours per day",
        min_value=0.5,
        max_value=16.0,
        value=4.0,
        step=0.5,
    )

    plan_clicked = st.button(
        "📅 Create Study Plan", type="primary", use_container_width=True
    )
    if not plan_clicked:
        return

    # Validate every required field before calling the API
    problems = []
    if not subjects.strip():
        problems.append("Please enter at least one subject.")
    if not topics.strip():
        problems.append("Please enter the topics you need to cover.")
    if exam_date <= date.today():
        problems.append("Exam date must be a future date.")
    if hours <= 0:
        problems.append("Study hours per day must be greater than zero.")
    if problems:
        for problem in problems:
            st.warning(f"⚠️ {problem}")
        return

    days_left = (exam_date - date.today()).days
    prompt = study_planner_prompt(
        subjects.strip(),
        topics.strip(),
        exam_date.strftime("%d %B %Y"),
        days_left,
        hours,
    )

    with st.spinner("🤖 Planning your schedule... please wait"):
        try:
            success, result = get_gemini_response(prompt)
        except RuntimeError as err:
            success, result = False, str(err)

    if success:
        st.success("✅ Study plan ready! Follow it day by day.")
        st.markdown(result)
    else:
        st.error(f"❌ {result}")


if selected_feature == "📅 Study Planner":
    run_study_planner()
else:
    generate_clicked = st.button("Generate", type="primary", use_container_width=True)

    if not user_input.strip():
        st.warning("⚠️ Please enter some study material or a question first.")
    elif generate_clicked:
        if len(user_input) > MAX_INPUT_CHARS:
            st.error(
                f"❌ Input is too long ({len(user_input)} characters). "
                f"Please shorten it to {MAX_INPUT_CHARS} characters or less."
            )
            st.stop()

        prompt = build_prompt(selected_feature, user_input)

        # Send the prompt to Gemini and display the result (or a friendly error)
        with st.spinner("🤖 Thinking... please wait"):
            try:
                success, result = get_gemini_response(prompt)
            except RuntimeError as err:
                success, result = False, str(err)

        if success:
            st.success("✅ Done! Your result is ready below.")
            st.markdown(result)
        else:
            st.error(f"❌ {result}")
