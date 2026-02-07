# PRD: YOLO Mode

## Project Overview

- **Name:** YOLO Mode (`yolo-mode`)
- **Version:** 0.1.0
- **Description:** An autonomous agent loop plugin for Claude Code that implements the "Ralph Loop" pattern.
- **Purpose:** To transform Claude Code into a self-driving developer that can plan, execute, and verify complex tasks with minimal human intervention, utilizing fresh context windows for each task to maintain "context hygiene."
- **UX:** 
    - **Dual Mode:** Works as both a **Claude Code Plugin** (via slash commands) and a **Global CLI Tool**.
    - **Voice Feedback:** Optional Text-to-Speech (TTS) integration via `tts-cli`.

## Core Architecture: The Ralph Loop

The system follows a specific agentic pattern:

1.  **Planner:** Takes the initial prompt and generates a `YOLO_PLAN.md` file containing a checklist of tasks.
2.  **Executor Loop:**
    - Reads `YOLO_PLAN.md`.
    - Identifies the next pending task (`[ ]`).
    - Spawns a **fresh** Claude Code instance (subprocess) to execute *only* that task.
    - **Autonomous Mode:** Uses `--dangerously-skip-permissions` to bypass manual confirmation for tool use.
    - **Self-Correction:** The agent updates `YOLO_PLAN.md` to mark the task as done (`[x]`) upon success.
3.  **Completion & Feedback:**
    - When all tasks are done, the loop exits.
    - An interactive prompt asks the user for feedback or new tasks.
    - If feedback is provided, the plan is updated, and the loop resumes.

## Features

### 1. Autonomous Task Execution
- Breaks down complex goals into atomic steps.
- Executes steps sequentially.
- Automatically handles file creation, editing, and command execution.

### 2. Context Hygiene
- Each task runs in a new process (`claude -p "..."`).
- Prevents the context window from filling up with previous task history.
- Reduces hallucination and "brain fog" in long sessions.

### 3. Voice Feedback (TTS)
- Integration with `tts-cli` (Pocket TTS).
- Announces:
    - Mission Start
    - Plan Initialization
    - Task Execution (concise)
    - Task Completion
    - Mission Success/Failure
- **UX Design:** Uses blocking calls and delays to ensure audio doesn't overlap or overwhelm.

### 4. Interactive Feedback Loop
- At the end of a mission, the user is prompted: "Do you have any feedback or new tasks?"
- Allows for iterative refinement without restarting the context.

### 5. Dual Distribution
- **Plugin:** Installable into Claude Code (`/yolo-mode:yolo`).
- **CLI:** Installable via pip (`yolo-mode`).

## Technical Stack
- **Language:** Python 3
- **Dependencies:** `claude` (CLI), `tts-cli` (optional)
- **Distribution:** `setuptools` (setup.py)
