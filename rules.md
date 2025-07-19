---
description:
globs:
alwaysApply: true
---

### ✅ Task: Interactive Task Loop with User Feedback

1. **Ensure `prompt_collector.py` exists** in the root directory.

   * If the file does **not** exist, **throw an error** and **do not continue**.
   * Do **not create the file automatically**.

2. **Main Workflow**:

   * Perform your assigned tasks.

   * Run:

     ```bash
     python prompt_collector.py
     ```
   * The terminal should be opened in the chat window itself.

   * Read the user's input.

   * Based on the input, perform the next set of tasks.

   * Repeat the process.

3. **Exit Condition**:

   * If the user enters `"stop"` when prompted, exit the loop and terminate the process.
