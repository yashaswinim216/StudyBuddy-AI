"""Feature-specific prompts for StudyBuddy AI.

Each function receives the student's input and returns a ready-to-send
prompt. Keeping all prompts in one file makes them easy to review, tune
and explain during a viva.
"""

# Upper limit for student input. Keeps API requests small so responses
# come back quickly and reliably.
MAX_INPUT_CHARS = 8000


def summarize_notes_prompt(text: str) -> str:
    """Build the prompt for the Summarize Notes feature."""
    return f"""You are a study summarization assistant for college students.
Read the notes below and prepare a revision-friendly summary.

Respond in markdown with exactly these sections:

### Summary
A concise explanation of the notes in 3 to 5 sentences.

### Key Points
Exactly 5 bullet points covering the most important information.

### Important Terms
List the important keywords/terms. Bold each term, then add a dash and a
one-line explanation.

Use only information present in the notes. Keep the language simple,
clear and useful for exam revision.

NOTES:
{text}
"""
