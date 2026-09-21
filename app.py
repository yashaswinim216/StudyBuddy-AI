"""StudyBuddy AI - an AI-powered study assistant for college students."""

import streamlit as st

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
    st.button("Generate", type="primary", use_container_width=True)

    if not user_input.strip():
        st.warning("⚠️ Please enter some study material or a question first.")
    else:
        st.info("AI features will be integrated in the next update.")
