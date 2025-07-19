# 🧠 Prompt Limiter - CLI Agent System

A utility that provides structured prompt collection and rule-based AI agent workflows. This project is designed to be integrated into other projects (not used as a standalone repository) to enable automated prompt-based workflows with GitHub Copilot Agents and similar tools.

## Purpose

This project provides a utility (`prompt_collector.py`) to capture and structure user prompts based on custom rules. It's designed to be used in other projects (e.g., with GitHub Copilot Agents) to automate or guide prompt-based workflows.

## ⚠️ Important Rule

**Before any task execution, you must always run:**

```bash
python prompt_collector.py
```

This ensures that:

- All prompts are properly collected and structured
- Rules defined in `.github/rules/rules.mdc` are followed
- The workflow maintains consistency across all interactions
- User input is captured according to the defined constraints

## 🤖 AI Agent Integration

### For Cursor and Tool-Supporting AI Agents

- **`rules.mdc` MUST be used in every request** to any AI agent that supports tools
- This file contains the behavioral rules and constraints that guide agent responses
- Without loading `rules.mdc`, the agent won't follow the proper workflow

### For GitHub Copilot Agents

- **`prompt.md` file is used to force Copilot to run `prompt_collector.py` in every iteration**
- This file contains instructions that automatically trigger the prompt collection workflow
- It ensures consistent behavior across all Copilot interactions in the project

### Integration Strategy

```
AI Agent Request → Load rules.mdc → Run prompt_collector.py → Follow workflow → Respond
```

## File Usage

This is **not** a standalone project. Instead, users should:

- Copy `prompt_collector.py` into the **root** of their own project
- Place the rules file at `.github/rules/rules.mdc`
- Place the AI agent instructions at `.github/prompt/prompt.md` (for Copilot)

## Requirements

- Python 3 installed
- All required Python packages should be extracted from `prompt_collector.py` and listed in a `requirements.txt` or inside the README

### Essential Dependencies

```bash
pip install textual pyperclip
```

## How to Use

1. Copy the files as described in the **File Usage** section
2. Install dependencies:
   ```bash
   pip install textual pyperclip
   ```
3. **Always start by running the prompt collector:**
   ```bash
   python prompt_collector.py
   ```
4. Follow the interactive workflow as defined by your rules

## Project Structure

```
your-project/
  prompt_collector.py          # Main utility - ALWAYS RUN THIS FIRST
  .github/
      rules/
          rules.mdc            # Workflow rules
      prompt/
          prompt.md            # AI agent instructions
```

## How It Works

- `rules.mdc`: Contains the logic and constraints for how the prompts should be interpreted. **AI agents with tool support must load this file in every request.**
- `prompt.md`: Used by GitHub Copilot to automatically trigger `prompt_collector.py` in every iteration, ensuring consistent workflow.
- `prompt_collector.py`: **This script must be run before every task** to collect and structure prompts as per the defined rules

## Available Interfaces

### Terminal Interface (Default)

- **Best for**: Developers and power users
- **Features**: Full-screen editor, keyboard shortcuts
- **Command**: `python prompt_collector.py --interface terminal`

**Keyboard Shortcuts:**

- `Ctrl+S` - Send text
- `Ctrl+A` - Select all
- `Ctrl+C` - Copy text
- `Ctrl+V` - Paste text
- `Escape` - Cancel

### GUI Interface

- **Best for**: Visual interface preference, Arabic/RTL text
- **Features**: Buttons, mouse interaction, automatic RTL detection
- **Command**: `python prompt_collector.py --interface gui`

## Configuration Options

```bash
# Set default interface permanently
python prompt_collector.py --set-default terminal
python prompt_collector.py --set-default gui

# Show available interfaces
python prompt_collector.py --show-interfaces

# Use specific interface for one session
python prompt_collector.py --interface gui
```

## Multilingual Support

The system automatically detects Arabic text and applies appropriate formatting:

- Automatic Arabic/RTL detection
- Unicode support for Arabic characters
- Right-to-left text direction in GUI mode

## Workflow Rules

1. **Always execute `prompt_collector.py` first** - This is mandatory for every task
2. **AI agents must load `rules.mdc`** before responding to any request
3. **Copilot must use `prompt.md`** to trigger prompt collection automatically
4. Follow the interactive prompts as they appear
5. Respect the constraints defined in `rules.mdc`
6. Use the collected prompts to guide subsequent AI agent interactions

## AI Agent Best Practices

- **Cursor Users**: Always ensure your AI agent loads `.github/rules/rules.mdc` before processing any request
- **Copilot Users**: The `prompt.md` file should automatically trigger the workflow - ensure it's properly placed
- **Custom Agents**: Implement tool support to read `rules.mdc` and execute `prompt_collector.py`

## Notes

- This setup is flexible—you can modify the rule and prompt files as needed for your use case
- It's ideal for use with AI agents or developers who want to structure their prompts consistently
- **Remember**: The workflow always begins with running `prompt_collector.py`
- **Critical**: AI agents must respect and load the rule files to maintain workflow integrity
- **Important**: The `prompt.md` file is essential for Copilot to function correctly in this setup
- **Always ensure** that the rules and prompts are up-to-date to reflect your project's needs

---