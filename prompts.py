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


def explain_concept_prompt(text: str) -> str:
    """Build the prompt for the Explain Concept feature."""
    return f"""You are a friendly college tutor who explains concepts in simple,
student-friendly language.

Explain the concept below. Respond in markdown with these sections:

### Simple Definition
One or two sentences a beginner can understand.

### Easy Explanation
A short paragraph expanding the definition in everyday language.

### Step-by-Step Explanation
A numbered list showing how the concept works, only when a step-by-step
view makes sense. Skip this section if the concept is too simple for it.

### Real-World Example
One practical example or analogy that connects the concept to daily life.

### Key Points to Remember
3 to 5 short bullets for quick revision.

Avoid unnecessary jargon. If a technical term is needed, explain it in the
same sentence.

CONCEPT OR QUESTION:
{text}
"""


def generate_quiz_prompt(text: str) -> str:
    """Build the prompt for the Generate Quiz feature."""
    return f"""You are a quiz generator for college students.

Create exactly 5 multiple-choice questions from the content below.
Base the questions primarily on the provided material - do not go beyond it.

Format every question exactly like this (markdown):

**Q1.** <question text>
- **A.** <option>
- **B.** <option>
- **C.** <option>
- **D.** <option>

**Correct Answer:** <letter>
**Explanation:** <one or two sentences explaining why it is correct>

Rules:
- Exactly one option is correct; the other three are plausible but wrong.
- Spread the correct answers across different letters (not all the same).
- Cover different parts of the content, not one idea five times.

CONTENT:
{text}
"""


def improve_answer_prompt(text: str) -> str:
    """Build the prompt for the Improve Answer feature."""
    return f"""You are an academic writing assistant for college students.

Improve the student's written answer below.

Improve:
- Grammar and spelling
- Sentence structure and flow
- Clarity and organization
- Academic presentation

Very important rules:
- Preserve the original meaning of the answer exactly.
- Do NOT add new information, facts or examples that are not in the original.
- Keep roughly the same length.

Respond in markdown with exactly these sections:

### Improved Answer
The polished version of the student's answer.

### What Was Improved
2 to 4 short bullets describing the changes you made.

STUDENT'S ANSWER:
{text}
"""


def generate_flashcards_prompt(text: str) -> str:
    """Build the prompt for the Generate Flashcards feature."""
    return f"""You are a revision assistant for college students.

Convert the study material below into 5 to 10 flashcards.

Format every flashcard exactly like this (markdown):

**Card 1**
- **Q:** <question or term>
- **A:** <concise answer or explanation>

Rules:
- Answers must be short and useful for quick revision (one or two lines).
- Cover the different important ideas in the material.
- Questions should test real understanding, not trivial details.
- If the material is thin, fewer flashcards are fine (minimum 5, maximum 10).

STUDY MATERIAL:
{text}
"""
