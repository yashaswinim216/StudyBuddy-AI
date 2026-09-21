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
st.session_state.setdefault("theme", "☀️")
st.session_state.setdefault("ai_result", None)
st.session_state.setdefault("ai_success", False)
st.session_state.setdefault("selected_feature", None)
st.session_state.setdefault("planner_hours", 4.0)

# ----------------------------------------------------------------- feature data
FEATURES = [
    ("📝 Summarize Notes", "Turn long notes into concise revision points."),
    ("💡 Explain Concept", "Understand ideas with simple examples."),
    ("❓ Generate Quiz", "Practice with 5 multiple-choice questions."),
    ("✍️ Improve Answer", "Polish grammar, clarity and structure."),
    ("🗂️ Generate Flashcards", "Revise quickly with Q&A cards."),
    ("📅 Study Planner", "Get a day-by-day exam study schedule."),
]

FEATURE_NAMES = [name for name, _ in FEATURES]

# Friendly loading message for every feature, shown while the AI is working
SPINNER_MESSAGES = {
    "📝 Summarize Notes": "📝 Summarizing your notes...",
    "💡 Explain Concept": "💡 Preparing a simple explanation...",
    "❓ Generate Quiz": "❓ Creating your quiz...",
    "✍️ Improve Answer": "✍️ Polishing your answer...",
    "🗂️ Generate Flashcards": "🗂️ Building your flashcards...",
    "📅 Study Planner": "📅 Planning your schedule...",
}

# ---------------------------------------------------------------- theme styling
# Hide Streamlit's built-in developer menu, deploy button and footer so the
# interface shows only the student study features. Shared layout, spacing and
# transition rules used by both themes live here.
BASE_CSS = """
    header[data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Comfortable, centered reading width and tidy section spacing */
    .stApp .block-container { max-width: 900px; padding-top: 1.4rem; padding-bottom: 3rem; }

    /* Header typography */
    .stApp h1 { font-size: 2.1rem; letter-spacing: -0.02em; margin-bottom: 0.1rem; }
    .stApp h1 + div p { font-size: 1.05rem; }

    /* Compact, clean theme toggle in the header */
    .stApp [data-testid="stSegmentedControl"] { justify-content: flex-end; }
    .stApp [data-testid="stSegmentedControl"] button {
        min-height: 34px; padding: 0.15rem 0.55rem; font-size: 0.95rem; border-radius: 9px;
    }

    /* Feature cards: equal size, subtle hover lift */
    .stApp [data-testid="stBaseButton-secondary"] {
        min-height: 58px; font-weight: 600; border-radius: 12px; width: 100%;
        transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    }
    .stApp [data-testid="stBaseButton-secondary"]:hover {
        transform: translateY(-2px);
    }
    .stApp [data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px);
    }
    .stApp [data-testid="stBaseButton-primary"], .stApp [data-testid="stBaseButton-secondary"] {
        transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    }

    /* Let card rows wrap gracefully on narrow screens */
    div.feature-grid-anchor ~ div [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    div.feature-grid-anchor ~ div [data-testid="stColumn"] { min-width: 168px; }

    /* AI output readability */
    .stApp [data-testid="stMarkdownContainer"] { line-height: 1.65; }
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3 { margin-top: 1.15rem; margin-bottom: 0.3rem; }
    .stApp [data-testid="stMarkdownContainer"] ul { padding-left: 1.25rem; }
    .stApp [data-testid="stMarkdownContainer"] li { margin: 0.3rem 0; }

    /* Gentle theme transition, skipped when reduced motion is requested */
    .stApp, .stApp * { transition: background-color .25s ease, border-color .25s ease, color .2s ease; }
    @media (prefers-reduced-motion: reduce) {
        .stApp, .stApp * { transition: none; }
    }
"""

# Bright, clean light theme
# Selectors deliberately match Streamlit's own .stApp[data-theme=...] specificity
# so the chosen theme always wins over Streamlit's OS-following default.
LIGHT_CSS = """
    .stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
        --background-color: #f6f8fc;
        --secondary-background-color: #ffffff;
        --primary-color: #2f6bff;
        --text-color: #171a20;
        background-color: #f6f8fc;
        color: #171a20;
    }
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-color: #e4e8f0;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
    }
    .stApp textarea, .stApp input {
        background-color: #ffffff !important;
        color: #171a20 !important;
        border-color: #d7dce6 !important;
    }
    .stApp [data-testid="stBaseButton-secondary"] {
        background-color: #ffffff; border-color: #d7dce6; color: #2b3442;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
    }
    .stApp [data-testid="stBaseButton-secondary"]:hover { border-color: #9db4e8; }
    .stApp [data-testid="stBaseButton-primary"] { box-shadow: 0 1px 3px rgba(47, 107, 255, 0.35); }
    .stApp [data-testid="stCaptionContainer"], .stApp small { color: #5a6474; }
"""

# Professional dark theme with light readable text
DARK_CSS = """
    .stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
        --background-color: #0e1117;
        --secondary-background-color: #151a24;
        --primary-color: #7aa2ff;
        --text-color: #e8eaf0;
        background-color: #0e1117;
        color: #e8eaf0;
    }
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #151a24;
        border-color: #2a3140;
    }
    .stApp textarea, .stApp input {
        background-color: #10141d !important;
        color: #e8eaf0 !important;
        border-color: #2a3140 !important;
    }
    .stApp [data-testid="stPills"] button {
        background-color: #151a24; color: #c9cfdb; border-color: #2a3140;
    }
    .stApp [data-testid="stPills"] button[aria-checked="true"] {
        background-color: #25355c; color: #d9e5ff; border-color: #4a6baf;
    }
    .stApp [data-testid="stBaseButton-secondary"] {
        background-color: #151a24; border-color: #2a3140; color: #d5dae6;
    }
    .stApp [data-testid="stBaseButton-secondary"]:hover { border-color: #4a6baf; }
    .stApp [data-testid="stBaseButton-primary"] { background-color: #2f54b8; color: #f2f6ff; }
    .stApp hr { border-color: #2a3140; }
    .stApp [data-testid="stMarkdownContainer"] code {
        background-color: #1b2231; color: #d9e5ff;
    }
    .stApp [data-testid="stCaptionContainer"], .stApp small { color: #97a1b5; }
    .stApp a { color: #8fb1ff; }
"""

theme_css = DARK_CSS if st.session_state["theme"] == "🌙" else LIGHT_CSS
st.markdown(f"<style>{BASE_CSS}{theme_css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------- header
def clear_all() -> None:
    """Reset every input, the selected feature and the previous AI output."""
    st.session_state["study_input"] = ""
    st.session_state["selected_feature"] = FEATURE_NAMES[0]
    st.session_state["planner_subjects"] = ""
    st.session_state["planner_topics"] = ""
    st.session_state["planner_hours"] = 4.0
    st.session_state["planner_date"] = date.today()
    st.session_state["ai_result"] = None
    st.session_state["ai_success"] = False


title_col, toggle_col = st.columns([5, 1], vertical_alignment="center")

with title_col:
    st.title("🎓 StudyBuddy AI")

with toggle_col:
    st.segmented_control("Theme", ["☀️", "🌙"], key="theme", label_visibility="collapsed")

# Subtitle and description sit below the title row, full width
st.subheader("Your AI-Powered Student Study Assistant")
st.caption("Learn smarter, revise faster, and improve your answers with AI.")


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
        exam_date = left.date_input(
            "Exam date", min_value=date.today(), key="planner_date"
        )
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


# ------------------------------------------------------------------ input area
with st.container(border=True):
    st.markdown("#### What would you like to study?")

    head_col, clear_col = st.columns([5, 1])
    with clear_col:
        st.button("🗑️ Clear", on_click=clear_all, type="tertiary", use_container_width=True)

    user_input = st.text_area(
        "Your study material",
        key="study_input",
        placeholder="Paste your notes, ask a question, enter a concept, or add your answer here...",
        height=190,
        label_visibility="collapsed",
    )

    if len(user_input) > MAX_INPUT_CHARS:
        st.warning(
            f"⚠️ Your input is {len(user_input)} characters. Please keep it under "
            f"{MAX_INPUT_CHARS} characters for faster, more reliable results."
        )

    # ------------------------------------------------------------ feature cards
    st.markdown("**Choose a feature**")
    st.markdown('<div class="feature-grid-anchor"></div>', unsafe_allow_html=True)

    for row_start in range(0, len(FEATURES), 3):
        cols = st.columns(3)
        for col, (name, blurb) in zip(cols, FEATURES[row_start:row_start + 3]):
            with col:
                is_selected = st.session_state["selected_feature"] == name
                if col.button(
                    name,
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["selected_feature"] = name
                    is_selected = True
                col.caption(blurb)

selected_feature = st.session_state["selected_feature"] or FEATURE_NAMES[0]

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
