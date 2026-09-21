# StudyBuddy AI

### An AI-Powered Student Study Assistant

StudyBuddy AI is an AI-powered student utility application designed to help college students understand, revise, and organize their study material using the Google Gemini API.

## Overview

Students can provide notes, questions, concepts, or written answers and receive AI-powered assistance through a simple Streamlit interface.

**Student Input → Feature Selection → Prompt Generation → Gemini API → AI Response → Display Output**

## Features

### 📝 Summarize Notes

Generates:

- Concise summary
- Five key points
- Important terms

### 💡 Explain Concept

Provides:

- Simple definition
- Easy explanation
- Example
- Important points

### ❓ Generate Quiz

Generates:

- Five multiple-choice questions
- Four options per question
- Correct answers
- Short explanations

### ✍️ Improve Answer

Improves:

- Grammar
- Spelling
- Clarity
- Structure
- Academic presentation

The original meaning of the answer is preserved.

### 🗂️ Generate Flashcards

Creates 5–10 question-and-answer flashcards from study material.

### 📅 AI Study Planner

Creates a personalized study schedule based on:

- Subjects
- Topics
- Exam date
- Available study hours

## Additional Features

### ☀️ Light Mode / 🌙 Dark Mode

Allows users to switch between light and dark themes.

### 🗑️ Clear / Reset

Clears entered content and previous AI output.

### ✅ Input Validation

Prevents empty or incomplete requests.

### ⚠️ Error Handling

Handles API failures, timeouts, quota issues, invalid credentials, and empty responses with user-friendly messages.

## Technology Stack

| Technology        | Purpose                         |
| ----------------- | ------------------------------- |
| Python            | Application development         |
| Streamlit         | User interface                  |
| Google Gemini API | AI response generation          |
| Google GenAI SDK  | Gemini API integration          |
| python-dotenv     | Environment variable management |
| Git               | Version control                 |
| GitHub            | Source code hosting             |

## Project Structure

```text
StudyBuddy-AI/
│
├── app.py
├── gemini_helper.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

## Installation and Setup

### Clone the repository

```bash
git clone https://github.com/yashaswinim216/StudyBuddy-AI.git
cd StudyBuddy-AI
```

### Create virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure the Gemini API key

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Users must obtain their own Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) and store it securely. Never hard-code the key in the source code and never commit it to the repository.

### Run the application

```bash
streamlit run app.py
```

The application should normally open at:

```text
http://localhost:8501
```

## Security

- API keys must never be hard-coded in the source code.
- API keys must never be committed to GitHub.
- `.env` is ignored by Git, so it is never uploaded to the repository.
- For deployment, use environment variables or Streamlit secrets instead of committing a `.env` file.
- If an API key is accidentally exposed, it should be revoked immediately and replaced with a new one.

## GitHub Usage

```text
git add .
git commit -m "commit message"
git push
```

## Project Objective

This project demonstrates:

- Practical LLM API integration
- Prompt engineering
- Student-focused AI utilities
- Input validation
- Error handling
- Secure API key management
- User interface development

## Future Enhancements

- PDF/document-based study material
- Subject-wise study history
- More advanced quiz modes
- Voice-based interaction
- Progress tracking

## Author

**Yashaswini M**

GitHub: [https://github.com/yashaswinim216](https://github.com/yashaswinim216)
