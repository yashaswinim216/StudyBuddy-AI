# StudyBuddy AI 🎓

**Your AI-Powered Study Assistant**

Learn smarter, revise faster, and improve your answers with AI.

## What is StudyBuddy AI?

StudyBuddy AI is an AI-powered study assistant built for college students.
Paste your notes, questions, concepts, or written answers, choose one of six
study features, and get an instant, well-structured AI response.

### Why it was created

Students spend hours condensing notes, hunting for practice questions, and
trying to understand difficult concepts on their own. This project shows how
a modern Large Language Model (LLM) API can be integrated into a simple,
practical tool that supports everyday study work.

### How it helps students

- **Revise faster** — turn long notes into crisp summaries and flashcards
- **Understand deeply** — get simple explanations with real-world examples
- **Practice effectively** — generate quizzes with answers and explanations
- **Write better** — polish written answers without losing their meaning
- **Plan smarter** — build a day-by-day study schedule before exams

## Features

### 📝 Note Summarization
Generates a concise summary, exactly **5 key points**, and a list of
important terms with short explanations — perfect for exam revision.

### 💡 Concept Explanation
Explains any concept like a friendly tutor: simple definition, easy
explanation, step-by-step breakdown, a real-world example, and key points
to remember.

### ❓ Quiz Generation
Creates **5 multiple-choice questions** (A–D options) based on your content,
each with the correct answer and a short explanation.

### ✍️ Answer Improvement
Improves grammar, spelling, sentence structure, clarity, organization, and
academic presentation of your written answers — while carefully **preserving
your original meaning**.

### 🗂️ Flashcard Generation
Converts study material into **5–10 question-and-answer flashcards** for
quick revision.

### 📅 AI Study Planner
Enter your subjects, topics, exam date, and available study hours per day to
receive a realistic, day-by-day study schedule with revision slots.

### ☀️🌙 Light / Dark Mode
A compact theme toggle at the top of the page switches between a bright
clean light theme and a dark theme. The choice stays active while you use
the app, and all inputs, cards and output adapt to it.

### 🗑️ Clear / Reset
One click clears the entered text, resets the selected feature and planner
fields, and removes the previous AI output so you can start fresh.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python | Core programming language |
| Streamlit | Web application interface |
| Google Gemini API | AI response generation |
| Google GenAI SDK | Official Python SDK for the Gemini API |
| python-dotenv | Secure environment variable handling |
| GitHub | Version control and project hosting |

## Installation

### 1. Clone or download the project

```bash
git clone <your-repository-url>
cd studybuddy-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

> On Linux/macOS use `source venv/bin/activate` instead.

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a file named `.env` in the project root and add your key:

```env
GEMINI_API_KEY=your_key_here
```

You can get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 5. Run the application

```bash
streamlit run app.py
```

The app opens automatically in your browser (usually at
`http://localhost:8501`).

## Usage

1. Paste your notes, concept, question, or written answer into the text area
2. Click a feature button (Summarize, Explain, Quiz, Improve, Flashcards)
3. Press **Generate** and wait a few seconds for the AI response
4. For the **Study Planner**, fill in subjects, topics, exam date, and daily
   study hours, then press **Create Study Plan**
5. Use the **🗑️ Clear** button to reset the form, and the ☀️/🌙 toggle to
   switch between light and dark themes

## Security

- The Gemini API key is stored **only in environment variables**, loaded from
  a `.env` file using `python-dotenv`
- The `.env` file is listed in `.gitignore`, so it is **never committed to
  GitHub**
- The key is never hard-coded in the source code, never displayed in the
  interface, and never sent to the browser
- Requests always run from the Python backend — the key stays on your machine

## Project Objective

This project demonstrates **practical LLM API integration for a real student
use case**: designing effective prompts, handling API errors gracefully,
securing API keys with environment variables, and building a clean,
beginner-friendly interface with Streamlit. Every feature maps to a genuine
study task, making the project easy to demonstrate and extend.

---

Made for students, by a student. Happy studying! 📚
