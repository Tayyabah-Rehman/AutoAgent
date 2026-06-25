"""
AutoAgent — Multi-tool AI Agent
Main Application Entry Point with Auth
"""
import streamlit as st
import sys
import os
from dotenv import load_dotenv

# ── Load .env FIRST ──────────────────────────────────────────
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from autoagent.database import init_db
from autoagent.auth import show_auth_page, get_current_user, logout
from autoagent.security import load_api_key, validate_api_key_format, mask_key, sanitize_input

st.set_page_config(
    page_title="AutoAgent — AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── Seed demo account ──────────────────────────────────────
from autoagent.database import create_user as _cu
_cu("demo", "demo@autoagent.ai", "demo1234")   # silently fails if exists

# ── Auth gate ─────────────────────────────────────────────
user = get_current_user()
if not user:
    show_auth_page()
    st.stop()

# ── Shared CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#F8F9FC;}
#MainMenu,footer,.stDeployButton{display:none!important;}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E8EBF0;}
.block-container{padding:1.5rem 2rem 3rem;max-width:920px;}

.aa-header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);border-radius:16px;padding:1.75rem 2.5rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;}
.aa-header h1{color:#FFF;font-size:1.9rem;font-weight:700;margin:0;letter-spacing:-0.5px;}
.aa-header p{color:#94A3C4;font-size:0.88rem;margin:0.3rem 0 0;}
.aa-badge{background:rgba(99,179,237,0.15);border:1px solid rgba(99,179,237,0.3);color:#63B3ED;font-size:0.7rem;font-weight:600;padding:0.25rem 0.65rem;border-radius:20px;letter-spacing:0.5px;text-transform:uppercase;white-space:nowrap;}

.cap-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.7rem;margin-bottom:1.5rem;}
.cap-card{background:#FFF;border:1px solid #E8EBF0;border-radius:12px;padding:0.9rem;text-align:center;}
.cap-card:hover{box-shadow:0 4px 16px rgba(0,0,0,0.07);}
.cap-icon{font-size:1.4rem;margin-bottom:0.3rem;}
.cap-title{font-size:0.78rem;font-weight:600;color:#1a1a2e;}
.cap-desc{font-size:0.7rem;color:#718096;margin-top:0.2rem;}

.step-card{background:#FFF;border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.75rem;border-left:4px solid #E8EBF0;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.step-card.thought{border-left-color:#6366F1;}
.step-card.action{border-left-color:#F59E0B;}
.step-card.observation{border-left-color:#10B981;}
.step-card.answer{border-left-color:#3B82F6;background:#EFF6FF;}
.step-card.error{border-left-color:#EF4444;background:#FEF2F2;}
.step-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.35rem;}
.step-label.thought{color:#6366F1;}
.step-label.action{color:#D97706;}
.step-label.observation{color:#059669;}
.step-label.answer{color:#2563EB;}
.step-label.error{color:#DC2626;}
.step-content{font-size:0.875rem;color:#374151;line-height:1.6;white-space:pre-wrap;}
.step-content.code{font-family:'JetBrains Mono',monospace;font-size:0.8rem;background:#F3F4F6;padding:0.5rem 0.75rem;border-radius:6px;}

.answer-box{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border:1px solid #BFDBFE;border-radius:14px;padding:1.5rem;margin-top:1rem;}
.answer-title{font-size:0.75rem;font-weight:700;color:#2563EB;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.75rem;}
.answer-text{font-size:0.9rem;color:#1E293B;line-height:1.7;white-space:pre-wrap;}

/* ── Chat messages ── */
.chat-msg-user{background:#EFF6FF;border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.5rem;max-width:80%;margin-left:auto;border:1px solid #BFDBFE;}
.chat-msg-user-label{font-size:0.65rem;font-weight:700;color:#2563EB;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.25rem;}
.chat-msg-user-content{font-size:0.88rem;color:#1E293B;}

.chat-msg-agent{background:#F8F9FC;border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.5rem;max-width:85%;border-left:3px solid #6366F1;}
.chat-msg-agent-label{font-size:0.65rem;font-weight:700;color:#6366F1;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.25rem;}
.chat-msg-agent-content{font-size:0.88rem;color:#1E293B;line-height:1.7;}
.chat-msg-agent-content p{margin-bottom:0.5rem;}
.chat-msg-agent-content strong{font-weight:700;color:#1a1a2e;}
.chat-msg-agent-content ul, .chat-msg-agent-content ol{margin:0.5rem 0;padding-left:1.5rem;}
.chat-msg-agent-content li{margin-bottom:0.25rem;}
.chat-msg-agent-content code{background:#F1F5F9;padding:0.1rem 0.4rem;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:0.8rem;}
.chat-msg-agent-content pre{background:#F1F5F9;padding:0.75rem;border-radius:8px;overflow-x:auto;margin:0.5rem 0;}

/* ── Status bar ── */
.status-bar{background:#F1F5F9;border-radius:10px;padding:0.5rem 1rem;margin-bottom:0.75rem;font-size:0.82rem;color:#475569;display:flex;align-items:center;gap:0.75rem;}
.status-bar .spinner{width:18px;height:18px;border:3px solid #E2E8F0;border-top-color:#6366F1;border-radius:50%;animation:spin 0.8s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:0.5rem;}
.status-dot.running{background:#F59E0B;animation:pulse 1s infinite;}
.status-dot.done{background:#10B981;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.3;}}

/* ── Enhanced text input ── */
div[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 2px solid #6366F1 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.25rem !important;
    font-size: 1rem !important;
    color: #1E293B !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
    outline: none !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94A3B8 !important;
    font-weight: 400 !important;
}

div[data-testid="stTextInput"] input:disabled {
    background: #F1F5F9 !important;
    border-color: #94A3B8 !important;
    opacity: 0.7 !important;
}

.stTextArea textarea{background:#FFF;border:1.5px solid #E2E8F0;border-radius:10px;font-family:'Inter',sans-serif;font-size:0.9rem;color:#1E293B;}
.stTextArea textarea:focus{border-color:#6366F1;box-shadow:0 0 0 3px rgba(99,102,241,0.1);}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#6366F1,#8B5CF6);color:white;border:none;border-radius:10px;font-weight:600;font-size:0.9rem;padding:0.65rem 2rem;width:100%;}
.stButton>button[kind="primary"]:hover{box-shadow:0 4px 15px rgba(99,102,241,0.35);}
.stButton>button{border-radius:8px;font-weight:500;font-size:0.85rem;}

.file-card{background:#FFF;border:1px solid #E8EBF0;border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:0.75rem;}
.file-icon{font-size:1.3rem;}
.file-name{font-size:0.82rem;font-weight:600;color:#1E293B;}
.file-meta{font-size:0.7rem;color:#94A3B8;}

.stat-card{background:#FFF;border:1px solid #E8EBF0;border-radius:10px;padding:0.75rem 1rem;text-align:center;}
.stat-num{font-size:1.4rem;font-weight:700;color:#1a1a2e;}
.stat-lbl{font-size:0.7rem;color:#94A3B8;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;}

.iter-badge{display:inline-flex;align-items:center;background:#F3F4F6;color:#6B7280;font-size:0.68rem;font-weight:600;padding:0.15rem 0.5rem;border-radius:20px;margin-bottom:0.35rem;}

.user-pill{display:inline-flex;align-items:center;gap:0.4rem;background:#EDE9FE;color:#5B21B6;font-size:0.78rem;font-weight:600;padding:0.3rem 0.75rem;border-radius:20px;}

/* ── Fixed input container ── */
.input-container{position:sticky;bottom:0;background:#F8F9FC;padding:1rem 0;border-top:1px solid #E8EBF0;margin-top:1rem;box-shadow:0 -4px 20px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────
for k, v in {"is_running": False, "active_file_path": None, "active_file_name": "", "chat_history": [], "query_processed": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;">
        <div style="font-size:1.6rem;">⚡</div>
        <div>
            <div style="font-weight:700;font-size:1rem;color:#1a1a2e;">AutoAgent</div>
            <div style="font-size:0.72rem;color:#94A3B8;">AI Agent v2.0</div>
        </div>
    </div>
    <div class="user-pill">👤 {user['username']} {'· Admin' if user['role']=='admin' else ''}</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        logout()

    st.markdown("---")

    # ── API Key ─────────────────────────────────────────────
    st.markdown('<div style="font-size:0.72rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">🔑 API Key</div>', unsafe_allow_html=True)

    env_key = os.environ.get("GROQ_API_KEY", "")

    if env_key and env_key != "your_groq_api_key_here":
        st.markdown(f'<div style="background:#F0FDF4;color:#16A34A;font-size:0.78rem;font-weight:500;padding:0.4rem 0.75rem;border-radius:8px;">✓ Loaded from .env ({mask_key(env_key)})</div>', unsafe_allow_html=True)
        active_key = env_key
        st.session_state.api_key_loaded = True
    else:
        manual_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_... or load from .env",
            key="sidebar_key"
        )
        if manual_key and validate_api_key_format(manual_key):
            st.markdown(f'<div style="background:#F0FDF4;color:#16A34A;font-size:0.78rem;padding:0.4rem 0.75rem;border-radius:8px;">✓ {mask_key(manual_key)}</div>', unsafe_allow_html=True)
            active_key = manual_key
            st.session_state.api_key_loaded = True
        elif manual_key:
            st.markdown('<div style="background:#FEF2F2;color:#DC2626;font-size:0.78rem;padding:0.4rem 0.75rem;border-radius:8px;">✗ Invalid format</div>', unsafe_allow_html=True)
            active_key = None
            st.session_state.api_key_loaded = False
        else:
            st.warning("⚠️ No API key found. Add GROQ_API_KEY to .env or enter manually.")
            active_key = None
            st.session_state.api_key_loaded = False
        st.markdown("[Get free key →](https://console.groq.com)")

    st.markdown("---")

    # ── Show reasoning toggle ──────────────────────────────────
    show_reasoning = st.checkbox("🔍 Show agent reasoning", value=False, help="Show or hide the step-by-step reasoning")
    st.session_state.show_reasoning = show_reasoning

    st.markdown("---")

    # Model Info
    st.markdown('<div style="font-size:0.72rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">🧠 Model</div>', unsafe_allow_html=True)
    st.markdown("""<div style="background:#F8F9FC;border-radius:8px;padding:0.75rem;font-size:0.8rem;color:#475569;">
        <b style="color:#1a1a2e;">LLaMA 3.3 70B</b><br>Groq · 128K ctx · Ultra-fast</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Tools list
    st.markdown('<div style="font-size:0.72rem;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">🛠 Tools</div>', unsafe_allow_html=True)
    for icon, name, desc in [("🌐","Web Search","Live DuckDuckGo"), ("🐍","Python","Safe execution"), ("📄","File Reader","Uploaded files"), ("🧩","Reasoning","General Q&A")]:
        st.markdown(f"""<div style="display:flex;gap:0.5rem;margin-bottom:0.5rem;">
            <div style="font-size:0.9rem;">{icon}</div>
            <div><div style="font-size:0.78rem;font-weight:600;color:#1E293B;">{name}</div>
            <div style="font-size:0.68rem;color:#94A3B8;">{desc}</div></div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Admin panel link
    if user.get("role") == "admin":
        st.markdown("🛡 **Admin:** [Open Admin Panel](#admin)", unsafe_allow_html=True)

# ── Navigation tabs ────────────────────────────────────────
tab_agent, tab_files, tab_history, tab_export = st.tabs([
    "⚡ Agent", "📁 File Upload", "📜 History", "💾 Export"
])


# ═══════════════════════════════════════════════════════════
# TAB 1: AGENT
# ═══════════════════════════════════════════════════════════
with tab_agent:
    import time
    from autoagent.agent import run_agent
    from autoagent.database import save_query, get_user_history
    import json

    st.markdown("""
    <div class="aa-header">
        <div>
            <h1>⚡ AutoAgent</h1>
            <p>Autonomous AI that searches the web, runs code, and reads your files</p>
        </div>
        <div class="aa-badge">Groq · LLaMA 3.3 70B</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cap-grid">
        <div class="cap-card"><div class="cap-icon">🌐</div><div class="cap-title">Web Search</div><div class="cap-desc">Live internet results</div></div>
        <div class="cap-card"><div class="cap-icon">🐍</div><div class="cap-title">Run Code</div><div class="cap-desc">Execute Python safely</div></div>
        <div class="cap-card"><div class="cap-icon">📄</div><div class="cap-title">Read Files</div><div class="cap-desc">Analyze your uploads</div></div>
        <div class="cap-card"><div class="cap-icon">🔁</div><div class="cap-title">Auto Loop</div><div class="cap-desc">8-step reasoning</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Active file banner ──────────────────────────────────
    if st.session_state.active_file_path:
        st.markdown(f"""
        <div style="background:#FEF3C7;border:1px solid #FCD34D;border-radius:10px;padding:0.6rem 1rem;
                    font-size:0.82rem;color:#92400E;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
            📎 <b>File in context:</b> {st.session_state.active_file_name}
            &nbsp;·&nbsp; Agent will read it automatically
        </div>
        """, unsafe_allow_html=True)
        if st.button("✕ Remove file from context"):
            st.session_state.active_file_path = None
            st.session_state.active_file_name = ""
            st.rerun()

    # ── CHAT HISTORY (Display all messages) ──────────────
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-msg-user">
                <div class="chat-msg-user-label">You</div>
                <div class="chat-msg-user-content">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-msg-agent">
                <div class="chat-msg-agent-label">AutoAgent</div>
                <div class="chat-msg-agent-content">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── INPUT BOX with form for Enter key support ──────────
    st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-size:0.9rem;font-weight:600;color:#1E293B;margin-bottom:0.5rem;">💬 Ask me anything</div>', unsafe_allow_html=True)

    # Use form to enable Enter key submission
    with st.form(key="chat_form", clear_on_submit=True):  # ← KEY CHANGE: clear_on_submit=True
        col_input, col_btn = st.columns([6, 1])

        with col_input:
            user_query = st.text_input(
                "Ask me anything...",
                value="",  # Always empty
                placeholder="Type your question here and press Enter..." if not st.session_state.is_running else "⏳ Agent is running...",
                key="chat_input",
                label_visibility="collapsed",
                disabled=st.session_state.is_running
            )

        with col_btn:
            submitted = st.form_submit_button("➤ Send", type="primary", use_container_width=True, disabled=st.session_state.is_running)

    # ── Clear chat button ──────────────────────────────────
    col_clear, col_spacer = st.columns([1, 5])
    with col_clear:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # ── Process query ──────────────────────────────────────
    if submitted and user_query.strip() and not st.session_state.is_running:
        # Store the query for processing
        query_text = user_query.strip()

        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": query_text})

        # ── Get API key ────────────────────────────────────
        resolved_key = os.environ.get("GROQ_API_KEY", "")
        if not resolved_key or resolved_key == "your_groq_api_key_here":
            resolved_key = st.session_state.get("sidebar_key", "")
        if not resolved_key:
            resolved_key = load_api_key("")
        if not resolved_key:
            st.error("⚠️ Please add your Groq API key to .env or enter it in the sidebar.")
            st.stop()

        query_clean = sanitize_input(query_text)

        # Inject file context
        if st.session_state.active_file_path:
            from autoagent.file_handler import read_file_for_agent
            file_content = read_file_for_agent(st.session_state.active_file_path)
            query_clean = f"{query_clean}\n\n[Uploaded file: {st.session_state.active_file_name}]\n{file_content[:4000]}"

        st.session_state.is_running = True

        st.markdown("---")

        # ── STATUS BAR ──────────────────────────────────────
        status_placeholder = st.empty()

        steps = []
        tool_count = 0
        start_time = time.time()
        final_answer = None

        ICONS = {"thought": ("💭","thought"), "action": ("⚡","action"),
                 "observation": ("👁","observation"), "answer": ("✅","answer"), "error": ("❌","error")}

        show_reasoning = st.session_state.get("show_reasoning", False)

        # ── PROCESS AGENT WITH LIVE UPDATES ─────────────────
        with st.container():
            status_placeholder.markdown(f"""
            <div class="status-bar">
                <div class="spinner"></div>
                <span>🔄 Agent is thinking...</span>
            </div>
            """, unsafe_allow_html=True)

            step_count = 0
            for step in run_agent(query_clean, resolved_key):
                step_count += 1

                status_placeholder.markdown(f"""
                <div class="status-bar">
                    <div class="spinner"></div>
                    <span>Step {step_count}: {step.get('type', '').capitalize()}... ({round(time.time() - start_time, 1)}s)</span>
                </div>
                """, unsafe_allow_html=True)

                if step["type"] == "answer":
                    final_answer = step["content"]
                    break
                elif step["type"] == "action":
                    tool_count += 1

                # ── Display steps if toggle is ON ──
                if show_reasoning:
                    icon, cls = ICONS.get(step["type"], ("•","thought"))
                    if step["type"] == "action":
                        content_html = f'<span class="step-content code">{step["content"]}</span>'
                    else:
                        content_html = f'<span class="step-content">{step["content"]}</span>'
                    iter_html = f'<span class="iter-badge">Step {step["iteration"]}</span><br>' if "iteration" in step else ""
                    st.markdown(f"""<div class="step-card {cls}">{iter_html}
                        <div class="step-label {cls}">{icon} {step['type'].title()}</div>
                        {content_html}</div>""", unsafe_allow_html=True)

                steps.append(step)

            elapsed = round(time.time() - start_time, 1)
            status_placeholder.markdown(f"""
            <div class="status-bar">
                <span class="status-dot done"></span>
                <span>✅ Done! {len(steps)} steps · {elapsed}s · {tool_count} tool call{"s" if tool_count!=1 else ""}</span>
            </div>
            """, unsafe_allow_html=True)

        # ── Display Answer ──────────────────────────────────
        if final_answer:
            # Add to chat history with markdown rendering
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})

            # Display in chat with markdown support
            st.markdown(f"""
            <div class="chat-msg-agent">
                <div class="chat-msg-agent-label">AutoAgent · {elapsed}s · {tool_count} tool call{"s" if tool_count!=1 else ""}</div>
                <div class="chat-msg-agent-content">{final_answer}</div>
            </div>
            """, unsafe_allow_html=True)

            save_query(user["id"], query_text, final_answer,
                       json.dumps([{"type":s["type"],"content":s.get("content","")} for s in steps]),
                       tool_count, elapsed)

        # Reset running state
        st.session_state.is_running = False
        # Rerun to clear the form - the form will be cleared automatically due to clear_on_submit=True
        st.rerun()

    elif submitted and st.session_state.is_running:
        st.warning("⏳ Agent is still running. Please wait...")

    elif submitted and not user_query.strip():
        st.warning("Please enter a question or task first.")


# ═══════════════════════════════════════════════════════════
# TAB 2: FILE UPLOAD
# ═══════════════════════════════════════════════════════════
with tab_files:
    from autoagent.file_handler import save_uploaded_file, delete_file, format_file_size, get_file_icon
    from autoagent.database import save_file_record, get_user_files, delete_file_record

    st.markdown("### 📁 File Upload")
    st.markdown(
        "<p style='color:#64748B;font-size:0.88rem;'>"
        "Upload files to use as context for the agent. "
        "Supports <b>PDF, TXT, CSV, JSON, Python, HTML, SQL</b> and more. Max 10MB."
        "</p>",
        unsafe_allow_html=True
    )

    if "last_uploaded_key" not in st.session_state:
        st.session_state.last_uploaded_key = None

    uploaded = st.file_uploader(
        "Choose a file",
        type=["txt","md","csv","json","xml","yaml","yml","py","js","ts",
              "html","css","sql","log","ini","cfg","toml","pdf"],
        help="PDF, text, code, and data files up to 10MB",
        key="file_uploader_widget"
    )

    if uploaded is not None:
        upload_key = f"{uploaded.name}_{uploaded.size}"
        if upload_key != st.session_state.last_uploaded_key:
            file_bytes = uploaded.read()
            path, err, size = save_uploaded_file(user["id"], file_bytes, uploaded.name)
            if err:
                st.error(f"❌ Upload failed: {err}")
            else:
                mime = uploaded.type or "application/octet-stream"
                save_file_record(user["id"], uploaded.name, path, size, mime)
                st.session_state.last_uploaded_key = upload_key
                st.success(f"✓ **{uploaded.name}** uploaded successfully ({format_file_size(size)})")

    st.markdown("---")
    st.markdown("#### Your Files")

    files = get_user_files(user["id"])
    if not files:
        st.markdown(
            "<div style='text-align:center;padding:2rem;color:#94A3B8;font-size:0.88rem;'>"
            "No files uploaded yet. Upload a file above to get started."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"<div style='font-size:0.8rem;color:#94A3B8;margin-bottom:0.75rem;'>{len(files)} file(s)</div>", unsafe_allow_html=True)
        for f in files:
            col_info, col_use, col_del = st.columns([5, 2, 1])
            with col_info:
                icon = get_file_icon(f["filename"])
                active_badge = ""
                if st.session_state.get("active_file_path") == f["file_path"]:
                    active_badge = "<span style='background:#FEF3C7;color:#92400E;font-size:0.68rem;font-weight:600;padding:0.15rem 0.5rem;border-radius:10px;margin-left:0.5rem;'>ACTIVE</span>"
                st.markdown(f"""
                <div class="file-card">
                    <div class="file-icon">{icon}</div>
                    <div style="min-width:0;">
                        <div class="file-name">{f['filename']}{active_badge}</div>
                        <div class="file-meta">{format_file_size(f['file_size'] or 0)} · {str(f['created_at'])[:16]}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_use:
                is_active = st.session_state.get("active_file_path") == f["file_path"]
                btn_label = "✓ Active" if is_active else "📎 Use in Agent"
                if st.button(btn_label, key=f"use_{f['id']}", use_container_width=True, disabled=is_active):
                    st.session_state.active_file_path = f["file_path"]
                    st.session_state.active_file_name = f["filename"]
                    st.success(f"📎 **{f['filename']}** set as agent context. Switch to the Agent tab.")
            with col_del:
                if st.button("🗑", key=f"del_{f['id']}", use_container_width=True):
                    if st.session_state.get("active_file_path") == f["file_path"]:
                        st.session_state.active_file_path = None
                        st.session_state.active_file_name = ""
                    fp = delete_file_record(f["id"], user["id"])
                    if fp:
                        delete_file(fp)
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 3: HISTORY
# ═══════════════════════════════════════════════════════════
with tab_history:
    from autoagent.database import get_user_history, get_all_history, delete_history_item

    st.markdown("### 📜 Query History")

    is_admin = user.get("role") == "admin"
    if is_admin:
        view_all = st.toggle("👁 View all users (Admin)", value=False)
        history = get_all_history(200) if view_all else get_user_history(user["id"], 50)
    else:
        history = get_user_history(user["id"], 50)

    if not history:
        st.markdown("<div style='text-align:center;padding:2rem;color:#94A3B8;'>No queries yet. Run the agent to see history here.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:0.82rem;color:#94A3B8;margin-bottom:1rem;'>{len(history)} queries found</div>", unsafe_allow_html=True)
        for item in history:
            with st.expander(f"🕐 {item['query'][:90]}{'…' if len(item['query'])>90 else ''}"):
                meta_parts = [f"⏱ {item.get('duration',0)}s", f"🛠 {item.get('tool_count',0)} tools", f"🗓 {str(item.get('created_at',''))[:16]}"]
                if is_admin and "username" in item:
                    meta_parts.insert(0, f"👤 {item['username']}")
                st.markdown(f"<div style='font-size:0.78rem;color:#94A3B8;margin-bottom:0.75rem;'>{' · '.join(meta_parts)}</div>", unsafe_allow_html=True)
                if item.get("answer"):
                    st.markdown(f"""<div class="answer-box" style="margin:0;">
                        <div class="answer-title">✅ Answer</div>
                        <div class="answer-text">{item['answer'][:1500]}{'…' if len(str(item['answer']))>1500 else ''}</div>
                    </div>""", unsafe_allow_html=True)
                c1, c2 = st.columns([6,1])
                with c2:
                    if st.button("🗑 Delete", key=f"hdel_{item['id']}", use_container_width=True):
                        delete_history_item(item["id"], user["id"])
                        st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 4: EXPORT
# ═══════════════════════════════════════════════════════════
with tab_export:
    from autoagent.export import export_to_csv, export_to_json, export_to_txt, get_export_filename
    from autoagent.database import get_user_history, get_stats

    st.markdown("### 💾 Export Your Data")

    history_for_export = get_user_history(user["id"], 500)
    count = len(history_for_export)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{count}</div><div class="stat-lbl">Your Queries</div></div>', unsafe_allow_html=True)
    with c2:
        total_tools = sum(h.get("tool_count",0) for h in history_for_export)
        st.markdown(f'<div class="stat-card"><div class="stat-num">{total_tools}</div><div class="stat-lbl">Tool Calls</div></div>', unsafe_allow_html=True)
    with c3:
        avg_d = round(sum(h.get("duration",0) for h in history_for_export) / max(count,1), 1)
        st.markdown(f'<div class="stat-card"><div class="stat-num">{avg_d}s</div><div class="stat-lbl">Avg Duration</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if count == 0:
        st.info("No query history to export yet. Run some queries first.")
    else:
        st.markdown(f"**{count} queries ready to export**")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""<div style="background:#FFF;border:1px solid #E8EBF0;border-radius:12px;padding:1.25rem;text-align:center;margin-bottom:0.75rem;">
                <div style="font-size:2rem;">📊</div>
                <div style="font-weight:600;font-size:0.9rem;color:#1E293B;">CSV Export</div>
                <div style="font-size:0.75rem;color:#94A3B8;margin:0.3rem 0 0.75rem;">Open in Excel / Google Sheets</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇ Download CSV", data=export_to_csv(history_for_export),
                file_name=get_export_filename("csv", user["username"]),
                mime="text/csv", use_container_width=True)

        with col2:
            st.markdown("""<div style="background:#FFF;border:1px solid #E8EBF0;border-radius:12px;padding:1.25rem;text-align:center;margin-bottom:0.75rem;">
                <div style="font-size:2rem;">🗂</div>
                <div style="font-weight:600;font-size:0.9rem;color:#1E293B;">JSON Export</div>
                <div style="font-size:0.75rem;color:#94A3B8;margin:0.3rem 0 0.75rem;">For developers & integrations</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇ Download JSON", data=export_to_json(history_for_export),
                file_name=get_export_filename("json", user["username"]),
                mime="application/json", use_container_width=True)

        with col3:
            st.markdown("""<div style="background:#FFF;border:1px solid #E8EBF0;border-radius:12px;padding:1.25rem;text-align:center;margin-bottom:0.75rem;">
                <div style="font-size:2rem;">📝</div>
                <div style="font-weight:600;font-size:0.9rem;color:#1E293B;">Text Export</div>
                <div style="font-size:0.75rem;color:#94A3B8;margin:0.3rem 0 0.75rem;">Readable plain text format</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇ Download TXT", data=export_to_txt(history_for_export),
                file_name=get_export_filename("txt", user["username"]),
                mime="text/plain", use_container_width=True)

    # Admin global stats
    if user.get("role") == "admin":
        st.markdown("---")
        st.markdown("#### 🛡 Admin — Platform Stats")
        stats = get_stats()
        sc1, sc2, sc3, sc4 = st.columns(4)
        for col, num, lbl in zip([sc1,sc2,sc3,sc4],
            [stats["total_users"], stats["total_queries"], stats["total_files"], f"{stats['avg_duration']}s"],
            ["Total Users", "Total Queries", "Files Uploaded", "Avg Response"]):
            with col:
                st.markdown(f'<div class="stat-card"><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        all_hist = get_all_history(500)
        if all_hist:
            st.download_button("⬇ Export ALL Users Data (CSV)",
                data=export_to_csv(all_hist),
                file_name=get_export_filename("csv","all_users"),
                mime="text/csv")

# Footer
st.markdown("""
<div style="margin-top:2rem;padding:1.25rem;background:#FFF;border-radius:12px;border:1px solid #E8EBF0;text-align:center;">
    <div style="font-size:0.78rem;color:#94A3B8;">
        <b style="color:#6366F1;">AutoAgent v2.0</b> · Multi-user · Secure · Groq · LLaMA 3.3 70B · Streamlit
    </div>
</div>
""", unsafe_allow_html=True)