# ⚡ AutoAgent v2.0 — Multi-tool AI Agent Platform

A production-ready autonomous AI agent with multi-user auth, file upload, history, and export.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key (or enter in sidebar)
cp .env.example .env
# Edit .env → GROQ_API_KEY=gsk_...

# 3. Run
streamlit run app.py
```

Get a **free** Groq API key at: https://console.groq.com

## 🔐 Demo Login
- Username: `demo` · Password: `demo1234`
- First registered user becomes regular user
- Set `role='admin'` in DB to unlock admin panel

## ✅ Features
| Feature | Details |
|---|---|
| 🔐 Auth | Register / Login / Sessions (SQLite) |
| ⚡ Agent | ReAct loop · 8 steps · LLaMA 3.3 70B |
| 🌐 Web Search | Live DuckDuckGo |
| 🐍 Code Runner | Safe Python execution (15s timeout) |
| 📁 File Upload | Upload & inject files into agent context |
| 📜 History | Per-user query history with delete |
| 💾 Export | CSV / JSON / TXT download |
| 🛡 Admin | View all users, global stats, full export |
| 🔑 Security | PBKDF2 hashed passwords, masked API keys |

## 📁 Structure
```
AutoAgent/
├── app.py                    # Main Streamlit app
├── autoagent/
│   ├── agent.py              # ReAct agent loop
│   ├── tools.py              # Web search, Python, file reader
│   ├── database.py           # SQLite: users, sessions, history, files
│   ├── auth.py               # Login/register UI + session helpers
│   ├── file_handler.py       # Upload, validate, read files
│   ├── export.py             # CSV / JSON / TXT export
│   └── security.py           # Key masking, input sanitization
├── db/                       # Auto-created: autoagent.db
├── uploads/                  # Auto-created: user files
├── requirements.txt
└── .env.example
```
