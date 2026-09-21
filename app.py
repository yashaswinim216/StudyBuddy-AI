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

# ----------------------------------------------------------- persistent state
# Values kept in session state so the theme and results survive reruns
st.session_state.setdefault("theme", "☀️ Light Mode")
st.session_state.setdefault("ai_result", None)
st.session_state.setdefault("ai_success", False)
st.session_state.setdefault("planner_hours", 4.0)

# --------------------------------------------------------------- base styling
# Hide Streamlit's built-in developer menu, deploy button and footer so the
# interface shows only the student study features. Also set the shared layout,
# spacing and transition rules used by both themes.
BASE_CSS = """
    header[data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Comfortable, centered reading width and tidy section spacing */
    .stApp .block-container { max-width: 960px; padding-top: 1.2rem; padding-bottom: 3rem; }
    .stApp h1 { margin-bottom: 0.25rem; }
    .stApp h3 { margin-bottom: 0.15rem; }

    /* Consistent rounded controls */
    .stApp [data-testid="baseButton"] { border-radius: 10px; }
    .stApp [data-testid="stPills"] button { border-radius: 999px; }

    /* AI output readability */
    .stApp [data-testid="stMarkdownContainer"] { line-height: 1.6; }
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3 { margin-top: 1.1rem; }

    /* Gentle theme transition, skipped when reduced motion is requested */
    .stApp, .stApp * { transition: background-color .25s ease, border-color .25s ease, color .2s ease; }
    @media (prefers-reduced-motion: reduce) {
        .stApp, .stApp * { transition: none; }
    }
"""

# Bright, clean light theme
LIGHT_CSS = """
    .stApp {
        --background-color: #f7f8fb;
        --secondary-background-color: #ffffff;
        --primary-color: #2f6bff;
        --text-color: #1a1c20;
        background-color: #f7f8fb;
        color: #1a1c20;
    }
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-color: #e3e7ee;
    }
    .stApp textarea, .stApp input {
        background-color: #ffffff;
        color: #1a1c20;
        border-color: #d6dbe4;
    }
"""

# Dark theme with light readable text
DARK_CSS = """
    .stApp {
        --background-color: #0e1117;
        --secondary-background-color: #161b26;
        --primary-color: #7aa2ff;
        --text-color: #e8eaf0;
        background-color: #0e1117;
        color: #e8eaf0;
    }
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b26;
        border-color: #2a3140;
    }
    .stApp textarea, .stApp input {
        background-color: #12161f !important;
        color: #e8eaf0 !important;
        border-color: #2a3140 !important;
    }
    .stApp [data-testid="stPills"] button {
        background-color: #161b26;
        color: #c9cfdb;
        border-color: #2a3140;
    }
    .stApp [data-testid="stPills"] button[aria-checked="true"] {
        background-color: #25355c;
        color: #d9e5ff;
        border-color: #4a6baf;
    }
    .stApp hr { border-color: #2a3140; }
    .stApp [data-testid="stMarkdownContainer"] code {
        background-color: #1c2230;
        color: #d9e5ff;
    }
    .stApp a { color: #8fb1ff; }
"""

theme_css = DARK_CSS if st.session_state["theme"].startswith("🌙") else LIGHT_CSS
st.markdown(
    f"<style>{BASE_CSS}{theme_css}</style>", unsafe_allow_html=True
)

# ---------------------------------------------------------------- app header
# Title block on the left, compact theme toggle on the right
title_col, toggle_col = st.columns([4, 1], vertical_alignment="center")

with title_col:
    st.title("🎓 StudyBuddy AI")
    st.subheader("Your AI-Powered Study Assistant")
    st.caption("Learn smarter, revise faster, and improve your answers with AI.")

with toggle_col:
    st.segmented_control(
        "Theme",
        ["☀️ Light Mode", "🌙 Dark Mode"],
        key="theme",
        label_visibility="collapsed",
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

# Friendly loading message for every feature, shown while the AI is working
SPINNER_MESSAGES = {
    "📝 Summarize Notes": "📝 Summarizing your notes...",
    "💡 Explain Concept": "💡 Preparing a simple explanation...",
    "❓ Generate Quiz": "❓ Creating your quiz...",
    "✍️ Improve Answer": "✍️ Polishing your answer...",
    "🗂️ Generate Flashcards": "🗂️ Building your flashcards...",
    "📅 Study Planner": "📅 Planning your schedule...",
}


def clear_all() -> None:
    """Reset every input, the selected feature and the previous AI output."""
    st.session_state["study_input"] = ""
    st.session_state["feature_pills"] = FEATURES[0]
    st.session_state["planner_subjects"] = ""
    st.session_state["planner_topics"] = ""
    st.session_state["planner_hours"] = 4.0
    st.session_state["planner_date"] = date.today()
    st.session_state["ai_result"] = None
    st.session_state["ai_success"] = False


# ---------------------------------------------------------------- input area
with st.container(border=True):
    heading_col, clear_col = st.columns([4, 1])

    with heading_col:
        st.markdown("##### 📚 Your Study Material")

    with clear_col:
        st.button("🗑️ Clear", on_click=clear_all, use_container_width=True)

    user_input = st.text_area(
        "Your study material",
        key="study_input",
        placeholder="Enter your notes, question, concept, or answer here...",
        height=200,
        label_visibility="collapsed",
    )

    if len(user_input) > MAX_INPUT_CHARS:
        st.warning(
            f"⚠️ Your input is {len(user_input)} characters. Please keep it under "
            f"{MAX_INPUT_CHARS} characters for faster, more reliable results."
        )

    selected_feature = st.pills(
        "Choose a feature", FEATURES, default=FEATURES[0], key="feature_pills"
    )


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
    with st.container(border=True):
        st.markdown("##### 📅 Plan Your Exam Preparation")
        st.caption("Fill in your exam details below to get a personalized schedule.")

        subjects = st.text_input(
            "Subjects (comma-separated)",
            key="planner_subjects",
            placeholder="e.g. Data Structures, DBMS, Mathematics",
        )
        topics = st.text_area(
            "Topics to cover (comma-separated)",
            key="planner_topics",
            placeholder="e.g. Linked Lists, Normalization, Probability",
            height=90,
        )
        left, right = st.columns(2)
        exam_date = left.date_input("Exam date", min_value=date.today(), key="planner_date")
        hours = right.number_input(
            "Available study hours per day",
            min_value=0.5,
            max_value=16.0,
            step=0.5,
            key="planner_hours",
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

        with st.spinner(SPINNER_MESSAGES["📅 Study Planner"]):
            try:
                success, result = get_gemini_response(prompt)
            except RuntimeError as err:
                success, result = False, str(err)

        # Keep the result so it stays visible while the user reads it
        st.session_state["ai_success"] = success
        st.session_state["ai_result"] = result


def show_output(success: bool, result: str) -> None:
    """Display the AI result (or a friendly error) in the output section."""
    if success:
        st.success("✅ Done! Your result is ready below.")
        with st.container(border=True):
            st.markdown(result)
    else:
        st.error(f"❌ {result}")


# -------------------------------------------------------------- AI output box
st.markdown("---")
st.header("🤖 AI Output")

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
        with st.spinner(SPINNER_MESSAGES.get(selected_feature, "🤖 Thinking...")):
            try:
                success, result = get_gemini_response(prompt)
            except RuntimeError as err:
                success, result = False, str(err)

        st.session_state["ai_success"] = success
        st.session_state["ai_result"] = result

# Render the stored result so it stays on screen while the user reads it
if st.session_state.get("ai_result") is not None:
    show_output(st.session_state["ai_success"], st.session_state["ai_result"])
