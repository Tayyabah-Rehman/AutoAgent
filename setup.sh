#!/bin/bash
echo "========================================"
echo "  AutoAgent Setup"
echo "========================================"
echo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo
echo "Setup complete!"
echo
echo "NEXT STEPS:"
echo "1. Open .env and add your GROQ_API_KEY"
echo "   Get a free key at: https://console.groq.com"
echo
echo "2. Run the app:"
echo "   python run.py"
