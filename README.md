# 💰 Money Matters
### Smarter Money. Better Decisions.

> An AI-powered Financial Literacy Assistant built for the IBM SkillsBuild Internship.

---

## 🌟 Overview

Money Matters is a production-grade, AI-powered financial literacy platform that helps users
understand personal finance through simple, trusted, and up-to-date information.

It leverages **IBM Granite**, **watsonx.ai**, **RAG (Retrieval-Augmented Generation)**, and
**Agentic AI routing** to deliver intelligent, context-aware financial guidance.

---

## 🛠 Tech Stack

| Layer        | Technology                                      |
|---|---|
| Frontend     | Streamlit, Custom CSS, Streamlit Components     |
| Backend      | Python 3.11+                                    |
| AI Model     | IBM Granite (via watsonx.ai Runtime)            |
| RAG          | Custom RAG pipeline + IBM Cloud Object Storage  |
| Agent        | Lightweight Agentic Router                      |
| Auth         | Email + Google OAuth (Streamlit session state)  |
| Config       | python-dotenv, JSON                             |

---

## 📁 Project Structure

```
money-matters/
├── frontend/          # Streamlit pages, components, and CSS
├── backend/           # Core business logic and data models
├── agents/            # Agentic AI router
├── rag/               # RAG pipeline (retrieval, chunking, embeddings)
├── services/          # IBM watsonx, COS, news, calculator services
├── utils/             # Shared helpers (logger, validators, formatters)
├── api/               # External API wrappers
├── config/            # App config and sources_config.json
├── data/
│   ├── raw/           # Raw documents ingested for RAG
│   ├── processed/     # Chunked, cleaned documents
│   └── embeddings/    # Stored vector embeddings
├── scripts/           # One-time ingestion / maintenance scripts
├── assets/            # Images, icons, logo
├── .env               # Secrets (never commit)
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 🚀 Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/your-username/money-matters.git
cd money-matters

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Fill in your IBM credentials in .env

# 5. Run the application
streamlit run frontend/app.py
```

---

## 🤝 IBM Services Used

- **IBM Granite** — Foundation model for financial Q&A
- **watsonx.ai Runtime** — Model inference and orchestration
- **IBM Cloud Object Storage** — Document storage for RAG knowledge base

---

## 📄 License

MIT License — built for IBM SkillsBuild Internship 2025.
