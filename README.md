# ⚡ AutoAgent v2.0 — Multi-tool AI Agent Platform

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-FF6B6B.svg)](https://console.groq.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/Tayyabah-Rehman/AutoAgent)

A production-ready autonomous AI agent with multi-user auth, file upload, history, and export.

---

## 📸 Screenshots

### Login Page
![Login Page](login%20page.PNG)

### Main Interface
![UI Interface](UI%20Interface.PNG)

---

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

> Get a free Groq API key at: https://console.groq.com

---

## 🔐 Demo Login

| Field    | Value      |
|----------|------------|
| Username | `demo`     |
| Password | `demo1234` |

- First registered user becomes a regular user  
- Set `role='admin'` in DB to unlock the admin panel

---

## ✨ Features

| Feature       | Details                                          |
|---------------|--------------------------------------------------|
| 🔐 Auth       | Register / Login / Sessions (SQLite)             |
| ⚡ Agent      | ReAct loop · 8 steps · LLaMA 3.3 70B            |
| 🌐 Web Search | Live DuckDuckGo                                  |
| 🐍 Code Runner| Safe Python execution (15s timeout)              |
| 📁 File Upload| Upload & inject files into agent context         |
| 📜 History    | Per-user query history with delete               |
| 💾 Export     | CSV / JSON / TXT download                        |
| 🛡 Admin      | View all users, global stats, full export        |
| 🔑 Security   | PBKDF2 hashed passwords, masked API keys         |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **LLM:** Groq API (LLaMA 3.3 70B)  
- **Database:** SQLite  
- **Authentication:** PBKDF2 hashed passwords  
- **Tools:** DuckDuckGo Search, Python Eval, File Reader  

---


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


## 🔧 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///db/autoagent.db
```

---

## 🎯 Usage

1. **Register/Login** — Create an account or use demo credentials  
2. **Ask Questions** — Type your query and press Enter  
3. **Upload Files** — Upload documents for context  
4. **View History** — See all your past queries  
5. **Export Data** — Download your history as CSV / JSON / TXT  

### Example Queries

- `"What is today's AI news?"`  
- `"Calculate compound interest for 10k at 8% over 5 years"`  
- `"Explain what LangChain is"`  
- `"Write Python to find prime numbers up to 100"`  

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository  
2. Create your feature branch: `git checkout -b feature/AmazingFeature`  
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`  
4. Push to the branch: `git push origin feature/AmazingFeature`  
5. Open a Pull Request  

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://console.groq.com/) for the LLM API  
- [Streamlit](https://streamlit.io/) for the amazing framework  
- [DuckDuckGo](https://duckduckgo.com/) for search capabilities
