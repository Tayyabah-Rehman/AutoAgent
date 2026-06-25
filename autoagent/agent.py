"""
AutoAgent — ReAct (Reason + Act) agent loop using Groq LLM.
"""
import re
import json
import time
from typing import Generator, Optional
from groq import Groq
from autoagent.tools import TOOL_DESCRIPTIONS

MAX_ITERATIONS = 8
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are AutoAgent, a powerful AI assistant that can search the web, run Python code, and read files.

You operate in a Thought → Action → Observation loop:

1. THOUGHT: Reason about what you need to do.
2. ACTION: Choose one tool:
   - web_search("query") — search the internet
   - run_python("code") — execute Python code
   - read_file("/path") — read a file
3. FINAL ANSWER: Give a complete, detailed answer when you have enough information.

Rules:
- Be thorough and detailed in your final answer.
- Use bullet points and structure.
- Cite sources when using web_search.
- Show your work for calculations.

Format:
THOUGHT: your reasoning
ACTION: tool_name("input")
OR
FINAL ANSWER: your detailed response
"""


def parse_action(text: str) -> Optional[tuple[str, str]]:
    """Extract tool name and input from agent output."""
    fa = re.search(r"FINAL ANSWER:\s*(.+)", text, re.DOTALL | re.IGNORECASE)
    if fa:
        return "final_answer", fa.group(1).strip()

    for tool in ["web_search", "run_python", "read_file"]:
        pattern = rf'{tool}\s*\(\s*["\']?(.*?)["\']?\s*\)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return tool, match.group(1).strip()

    return None


def run_agent(
    user_query: str,
    api_key: str,
    on_step=None,
) -> Generator[dict, None, None]:
    """
    Run the ReAct agent loop.
    Yields step dicts: {type: 'thought'|'action'|'observation'|'answer'|'error', content: str}
    """
    client = Groq(api_key=api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for iteration in range(MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=2048,
                temperature=0.1,
            )
            agent_output = response.choices[0].message.content.strip()
        except Exception as e:
            yield {"type": "error", "content": f"LLM error: {str(e)}"}
            return

        messages.append({"role": "assistant", "content": agent_output})

        thought_match = re.search(r"THOUGHT:\s*(.+?)(?=ACTION:|FINAL ANSWER:|$)", agent_output, re.DOTALL | re.IGNORECASE)
        if thought_match:
            yield {"type": "thought", "content": thought_match.group(1).strip(), "iteration": iteration + 1}

        parsed = parse_action(agent_output)

        if not parsed:
            yield {"type": "error", "content": "Could not parse agent action. Please rephrase your question."}
            return

        tool_name, tool_input = parsed

        if tool_name == "final_answer":
            yield {"type": "answer", "content": tool_input}
            return

        yield {"type": "action", "content": f"{tool_name}({repr(tool_input)})", "tool": tool_name}

        tool_fn = TOOL_DESCRIPTIONS.get(tool_name, {}).get("fn")
        if tool_fn is None:
            observation = f"Unknown tool: {tool_name}"
        else:
            try:
                observation = tool_fn(tool_input)
            except Exception as e:
                observation = f"Tool error: {str(e)}"

        if len(observation) > 3000:
            observation = observation[:3000] + "\n[Truncated]"

        yield {"type": "observation", "content": observation}

        messages.append({"role": "user", "content": f"OBSERVATION: {observation}\n\nContinue."})
        time.sleep(0.3)

    yield {"type": "answer", "content": "I reached the maximum number of steps. Here is what I found so far."}