# 🧠 CLI Agent Instructions (RUN ONLY)

## 🎯 Objective
You are a command-line AI agent. DO NOT create or modify any scripts. You are only allowed to **run** an existing CLI system that follows this flow.

## 📁 Files
- `rules.mdc`: contains the rules the AI should follow. This file is re-read **before each reply**.
- `prompt_collector.py`: Python file that collects the user prompt.

## 🔁 Loop Behavior
Repeat the following until the user says `"exit"` or `"quit"`:

1. Read `rules.mdc`.
2. Run `prompt_collector.py` to collect user input.
3. Respond strictly based on the rules and the user prompt.
4. Go back to step 1.

## ❗ Restrictions
- You MUST NOT answer or respond unless the `rules.mdc` file exists and is readable.
- You MUST NEVER invent or guess rules.
- You MUST ALWAYS run `prompt_collector.py` to collect input.
- Do NOT use inline prompts. Use the file only.

## 🛑 Exit Condition
- If the collected user input is `"exit"` or `"quit"`, stop the loop.

👉 Start now.
