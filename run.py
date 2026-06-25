"""
AutoAgent Launcher
Run this file to start AutoAgent: python run.py
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    # ── Load .env file ──────────────────────────────────────
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded .env from: {env_path}")
    else:
        print("⚠️ No .env file found. Create one from .env.example")
        print("   or enter your API key in the sidebar.")

    print("=" * 50)
    print("  ⚡ AutoAgent — AI Agent")
    print("=" * 50)
    print()

    # ── Check API key ──────────────────────────────────────
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        print("⚠️ No valid GROQ_API_KEY found in .env")
        print("   You can enter your key in the sidebar when the app opens.")
        print()
    else:
        # Show masked key
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "✓ loaded"
        print(f"✅ Groq API Key: {masked}")
        print()

    print("🚀 Starting AutoAgent on http://localhost:8501")
    print("   Press Ctrl+C to stop.")
    print()

    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ])

if __name__ == "__main__":
    main()
