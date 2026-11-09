# 💬 CustomBot

A friendly chatbot that answers questions in **simple, human, easy-to-understand language**. It reads your company FAQ, finds the most relevant information, and uses **Google Gemini** to explain it clearly.

Every answer can be **copied** or **downloaded** as a **Text**, **Word**, or **PDF** file.

---

## ✨ Features

- Answers explained in plain, everyday language (no jargon)
- Uses your own FAQ data (RAG: Retrieval-Augmented Generation)
- Remembers recent messages so follow-up questions work
- One-click copy of any answer
- Download answers as `.txt`, `.docx`, or `.pdf`
- Simple Streamlit chat interface

---

## 📁 Project Structure

```
CustomBot/
│
├── app.py              # Streamlit chat UI + copy/download features
├── rag.py              # Retrieval + Gemini answer generation
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your API key
├── .gitignore
│
└── data/
    └── company_faq.txt # Your knowledge base (edit this!)
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CustomBot.git
cd CustomBot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Get a free key from [Google AI Studio](https://aistudio.google.com/apikey), then:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and replace the placeholder:

```
GEMINI_API_KEY=your_real_api_key_here
```

### 5. Run the bot

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## 🧠 How It Works

1. `rag.py` reads `data/company_faq.txt` and splits it into chunks (one Q&A per chunk).
2. Each chunk is converted into an embedding using Gemini.
3. When a user asks a question, the 3 most similar chunks are retrieved.
4. Gemini receives those chunks plus the question and writes a short, simple, friendly answer.
5. `app.py` shows the answer and lets the user copy it or download it.

If a question is not covered by the FAQ, the bot explains the concept using general knowledge and clearly says so. It does not invent company-specific facts.

---

## ✏️ Customizing

**Use your own data**
Replace the contents of `data/company_faq.txt`. Keep the format of `Q:` / `A:` blocks separated by a blank line:

```
Q: Your question here?
A: Your answer here.

Q: Another question?
A: Another answer.
```

**Change the tone or style**
Edit `SYSTEM_PROMPT` in `rag.py`. For example, make it more formal, shorter, or add a language preference.

**Change the Gemini model**
Set these optional values in `.env`:

```
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBED_MODEL=gemini-embedding-001
```

---

## 📥 Copy & Download

Under every answer, open **"📋 Copy or download this answer"** to:

| Option | How |
|--------|-----|
| Copy | Click the copy icon at the top-right of the answer box |
| Text | Click **Text (.txt)** |
| Word | Click **Word (.docx)** |
| PDF | Click **PDF (.pdf)** |

> **Note:** PDF export supports basic Latin characters only. Other scripts (e.g. Urdu, Arabic) will appear as `?` in the PDF, but work fine in Text and Word.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `GEMINI_API_KEY not found` | Make sure you created `.env` (not just `.env.example`) and added your key |
| `ModuleNotFoundError` | Activate your virtual environment and run `pip install -r requirements.txt` |
| Model not found error | Update `GEMINI_CHAT_MODEL` in `.env` to a currently available Gemini model |
| Rate limit / quota error | Wait a minute and retry, or check your usage in Google AI Studio |

---

## 🔒 Security

- Never commit your `.env` file. It is already listed in `.gitignore`.
- Never share your API key publicly.

---

## 🧰 Tech Stack

- [Streamlit](https://streamlit.io/) for the UI
- [Google Gemini API](https://ai.google.dev/) for embeddings and answers
- [NumPy](https://numpy.org/) for similarity search
- [python-docx](https://python-docx.readthedocs.io/) for Word export
- [fpdf2](https://py-pdf.github.io/fpdf2/) for PDF export

---

## 📄 License

This project is licensed under the MIT License. Feel free to use and modify it.
