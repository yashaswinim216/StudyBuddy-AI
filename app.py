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

# Summarize Notes is highlighted from the start so a card is always selected
st.session_state.setdefault("selected_feature", FEATURE_NAMES[0])
st.session_state.setdefault("planner_hours", 4.0)

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
# Design system: "Ink & Highlighter". Actions are ink, the selected feature is
# highlighted like a marked line in study notes, everything else stays quiet.
#
# Streamlit computes many component colors from its own OS-following theme, so
# every component below gets explicit theme-aware colors. Without this, labels,
# alerts and AI output can render in the "other" theme's colors (for example
# near-white text on the light paper background).
#
# Hide Streamlit's built-in developer menu, deploy button and footer so the
# interface shows only the student study features. Shared layout, typography
# and transition rules used by both themes live here.
BASE_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700&display=swap');

    header[data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Hide the developer-only install nudge shown by some Streamlit builds */
    [data-testid="stStatusWidget"], [data-testid="stAppStatusWidget"] { display: none; }

    /* Lexend: designed to improve reading fluency for students.
       Listed explicitly because Streamlit declares its own font on some
       wrapper elements, which would beat plain inheritance. */
    .stApp, .stApp button, .stApp input, .stApp textarea, .stApp select,
    .stApp label, .stApp p,
    .stApp [data-testid="stHeadingWithActionElements"],
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stSegmentedControl"],
    .stApp [data-testid="stButtonGroup"] {
        font-family: 'Lexend', 'Segoe UI', system-ui, sans-serif;
    }

    /* Comfortable, centered reading width and tidy section spacing */
    .stApp .block-container { max-width: 900px; padding-top: 1.4rem; padding-bottom: 3rem; }

    /* Header typography */
    .stApp h1 { font-size: 2.1rem; letter-spacing: -0.02em; margin-bottom: 0.1rem; }
    .stApp h1 + div p { font-size: 1.05rem; }

    /* Compact, clean theme toggle in the header */
    .stApp [data-testid="stSegmentedControl"] { justify-content: flex-end; }
    .stApp [data-testid="stSegmentedControl"] button,
    .stApp [data-testid="stButtonGroup"] [role="radio"] {
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
    .stApp [data-testid="stBaseButton-primary"] {
        border-radius: 12px;
        transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    }
    .stApp [data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px);
    }

    /* The selected feature card is "highlighted" like a marked line in notes.
       Scoped to the feature grid so the Generate button keeps its own style. */
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-primary"] {
        min-height: 58px; font-weight: 600; width: 100%;
    }

    /* Let card rows wrap gracefully on narrow screens */
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }

    /* AI output readability: generous leading and a comfortable measure */
    .stApp [data-testid="stMarkdownContainer"] { line-height: 1.65; max-width: 46rem; }
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3 { margin-top: 1.15rem; margin-bottom: 0.3rem; }
    .stApp [data-testid="stMarkdownContainer"] ul { padding-left: 1.25rem; }
    .stApp [data-testid="stMarkdownContainer"] li { margin: 0.3rem 0; }

    /* Keyboard focus stays visible in every theme */
    .stApp button:focus-visible, .stApp textarea:focus-visible, .stApp input:focus-visible {
        outline: 2px solid currentColor; outline-offset: 2px;
    }

    /* Gentle theme transition, skipped when reduced motion is requested */
    .stApp, .stApp * { transition: background-color .25s ease, border-color .25s ease, color .2s ease; }
    @media (prefers-reduced-motion: reduce) {
        .stApp, .stApp * { transition: none; }
    }
"""

# Light theme: ink on paper.
# Selectors deliberately match Streamlit's own .stApp[data-theme=...] specificity
# so the chosen theme always wins over Streamlit's OS-following default.
LIGHT_CSS = """
    .stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
        --background-color: #f6f7f2;
        --secondary-background-color: #ffffff;
        --primary-color: #1a2238;
        --text-color: #1a2238;
        background-color: #f6f7f2;
        color: #1a2238;
    }
    /* Ink text everywhere Streamlit would otherwise use its own theme color */
    .stApp label, .stApp p, .stApp li, .stApp span, .stApp div { color: #1a2238; }
    .stApp strong, .stApp b { color: #1a2238; font-weight: 600; }
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] * { color: #1a2238; }
    .stApp [data-testid="stMarkdownContainer"] li::marker { color: #1a2238; }
    .stApp [data-testid="stSpinner"] { color: #1a2238; }

    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-color: #e5e5dc;
        box-shadow: 0 1px 3px rgba(26, 34, 56, 0.06);
    }
    /* Inputs: white fields, dark text, medium-gray placeholders */
    .stApp textarea, .stApp input,
    .stApp [data-testid="stDateInputField"], .stApp [data-testid="stDateInputButton"],
    .stApp [data-testid="stNumberInputField"], .stApp [data-testid="stNumberInputStepUp"],
    .stApp [data-testid="stNumberInputStepDown"] {
        background-color: #ffffff !important;
        color: #1a2238 !important;
        border-color: #d8d8cf !important;
    }
    .stApp [data-testid="stNumberInputStepUp"], .stApp [data-testid="stNumberInputStepDown"] {
        border-left: 1px solid #d8d8cf;
    }
    .stApp textarea::placeholder, .stApp input::placeholder {
        color: #767e8c !important; opacity: 1;
    }
    /* Date picker calendar popover */
    .stApp [data-testid="stDatePickerPopover"],
    .stApp [data-testid="stDatePickerPopover"] * {
        background-color: #ffffff; color: #1a2238; border-color: #d8d8cf;
    }

    /* Alerts: dark, readable text per message kind on their pale tints */
    .stApp [data-testid="stAlertContainer"] { color: #1a2238; }
    .stApp [data-testid="stAlertContentInfo"],
    .stApp [data-testid="stAlertContentInfo"] * { color: #1a2238; }
    .stApp [data-testid="stAlertContentSuccess"],
    .stApp [data-testid="stAlertContentSuccess"] * { color: #1e5c2f; }
    .stApp [data-testid="stAlertContentWarning"],
    .stApp [data-testid="stAlertContentWarning"] * { color: #5f4400; }
    .stApp [data-testid="stAlertContentError"],
    .stApp [data-testid="stAlertContentError"] * { color: #8c1d18; }

    /* Unselected feature cards: quiet paper tiles */
    .stApp [data-testid="stBaseButton-secondary"] {
        background-color: #ffffff; border-color: #d8d8cf; color: #2a3348;
        box-shadow: 0 1px 2px rgba(26, 34, 56, 0.05);
    }
    .stApp [data-testid="stBaseButton-secondary"]:hover { border-color: #1a2238; color: #1a2238; }

    /* Actions are ink */
    .stApp [data-testid="stBaseButton-primary"] {
        background-color: #1a2238; color: #ffffff; border-color: #1a2238;
    }
    .stApp [data-testid="stBaseButton-primary"]:hover { background-color: #273156; color: #ffffff; }

    /* The selected feature card is the highlighter moment */
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-primary"] {
        background-color: #ffd84d; color: #1a2238; border-color: #e8c233;
        box-shadow: none;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-primary"]:hover {
        background-color: #ffdf66; color: #1a2238;
    }

    /* Quiet utility buttons (Clear) */
    .stApp [data-testid="stBaseButton-tertiary"] {
        background-color: transparent; color: #2a3348; border-color: transparent;
    }
    .stApp [data-testid="stBaseButton-tertiary"]:hover {
        background-color: #eceee7; color: #1a2238;
    }

    /* Theme toggle: ink text, calm paper chips, highlighter for the active one */
    .stApp [data-testid="stButtonGroup"] [role="radio"] {
        background-color: #eceee7; color: #2a3348; border: 1px solid #d8d8cf;
    }
    .stApp [data-testid="stButtonGroup"] [role="radio"]:hover {
        border-color: #1a2238; color: #1a2238;
    }
    .stApp [data-testid="stButtonGroup"] [role="radio"][data-selected="true"] {
        background-color: #ffd84d; color: #1a2238; border-color: #e8c233;
    }

    .stApp [data-testid="stCaptionContainer"], .stApp small { color: #5a6474; }
    .stApp hr { border-color: #e5e5dc; }
    .stApp [data-testid="stMarkdownContainer"] code {
        background-color: #efefe8; color: #1a2238;
    }
    .stApp a { color: #27408b; }
"""

# Dark theme: chalk on chalkboard, with the same highlighter for selection.
DARK_CSS = """
    .stApp, .stApp[data-theme="light"], .stApp[data-theme="dark"] {
        --background-color: #11151c;
        --secondary-background-color: #171c26;
        --primary-color: #e9edf5;
        --text-color: #e9edf5;
        background-color: #11151c;
        color: #e9edf5;
    }
    /* Chalk text everywhere Streamlit would otherwise use its own theme color */
    .stApp label, .stApp p, .stApp li, .stApp span, .stApp div { color: #e9edf5; }
    .stApp strong, .stApp b { color: #f4f6fb; font-weight: 600; }
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] * { color: #e9edf5; }
    .stApp [data-testid="stMarkdownContainer"] li::marker { color: #e9edf5; }
    .stApp [data-testid="stSpinner"] { color: #e9edf5; }

    .stApp [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #171c26;
        border-color: #2b3342;
    }
    /* Inputs: dark fields, light text, soft-gray placeholders */
    .stApp textarea, .stApp input,
    .stApp [data-testid="stDateInputField"], .stApp [data-testid="stDateInputButton"],
    .stApp [data-testid="stNumberInputField"], .stApp [data-testid="stNumberInputStepUp"],
    .stApp [data-testid="stNumberInputStepDown"] {
        background-color: #12161e !important;
        color: #e9edf5 !important;
        border-color: #2b3342 !important;
    }
    .stApp [data-testid="stNumberInputStepUp"], .stApp [data-testid="stNumberInputStepDown"] {
        border-left: 1px solid #2b3342;
    }
    .stApp textarea::placeholder, .stApp input::placeholder {
        color: rgba(233, 237, 245, 0.55) !important; opacity: 1;
    }
    /* Date picker calendar popover */
    .stApp [data-testid="stDatePickerPopover"],
    .stApp [data-testid="stDatePickerPopover"] * {
        background-color: #171c26; color: #e9edf5; border-color: #2b3342;
    }

    /* Alerts: bright, readable text per message kind on the dark background */
    .stApp [data-testid="stAlertContainer"] { color: #e9edf5; }
    .stApp [data-testid="stAlertContentInfo"],
    .stApp [data-testid="stAlertContentInfo"] * { color: #e9edf5; }
    .stApp [data-testid="stAlertContentSuccess"],
    .stApp [data-testid="stAlertContentSuccess"] * { color: #9fd8ae; }
    .stApp [data-testid="stAlertContentWarning"],
    .stApp [data-testid="stAlertContentWarning"] * { color: #f5d061; }
    .stApp [data-testid="stAlertContentError"],
    .stApp [data-testid="stAlertContentError"] * { color: #ff9d94; }

    /* Unselected feature cards: quiet chalkboard panels */
    .stApp [data-testid="stBaseButton-secondary"] {
        background-color: #171c26; border-color: #2b3342; color: #d5dae6;
    }
    .stApp [data-testid="stBaseButton-secondary"]:hover { border-color: #556179; color: #f4f6fb; }

    /* Actions are chalk: light button, ink text */
    .stApp [data-testid="stBaseButton-primary"] {
        background-color: #e9edf5; color: #14202e; border-color: #e9edf5;
    }
    .stApp [data-testid="stBaseButton-primary"]:hover { background-color: #ffffff; color: #14202e; }

    /* The selected feature card keeps the highlighter glow */
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-primary"] {
        background-color: #ffde59; color: #1a2238; border-color: #d9b826;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stBaseButton-primary"]:hover {
        background-color: #ffe473; color: #1a2238;
    }

    /* Quiet utility buttons (Clear) */
    .stApp [data-testid="stBaseButton-tertiary"] {
        background-color: transparent; color: #d5dae6; border-color: transparent;
    }
    .stApp [data-testid="stBaseButton-tertiary"]:hover {
        background-color: #1d2431; color: #f4f6fb;
    }

    /* Theme toggle: chalk text, calm panels, highlighter for the active one */
    .stApp [data-testid="stButtonGroup"] [role="radio"] {
        background-color: #171c26; color: #d5dae6; border: 1px solid #2b3342;
    }
    .stApp [data-testid="stButtonGroup"] [role="radio"]:hover {
        border-color: #556179; color: #f4f6fb;
    }
    .stApp [data-testid="stButtonGroup"] [role="radio"][data-selected="true"] {
        background-color: #ffde59; color: #1a2238; border-color: #d9b826;
    }

    .stApp [data-testid="stCaptionContainer"], .stApp small { color: #97a1b5; }
    .stApp hr { border-color: #2b3342; }
    .stApp [data-testid="stMarkdownContainer"] code {
        background-color: #1d2431; color: #f2e2a0;
    }
    .stApp a { color: #a9c0ff; }
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
