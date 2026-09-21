"""StudyBuddy AI - an AI-powered study assistant for college students."""

import streamlit as st

from gemini_helper import get_gemini_response
from prompts import (
    MAX_INPUT_CHARS,
    explain_concept_prompt,
    generate_flashcards_prompt,
    generate_quiz_prompt,
    improve_answer_prompt,
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

if selected_feature == "📅 Study Planner":
    # The planner gets its own input form, shown in later commits.
    st.info("The study planner will be available soon.")
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
    # The study planner is added in the next commit.
    return text
