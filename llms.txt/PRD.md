# PRD: YOLO Mode

## Project Overview

- **Name:** YOLO Mode (`yolo-mode`)
- **Version:** 0.1.9
- **Description:** An autonomous agent loop plugin for Claude Code that implements the "Ralph Loop" pattern.
- **Purpose:** To transform Claude Code into a self-driving developer that can plan, execute, and verify complex tasks with minimal human intervention, utilizing fresh context windows for each task to maintain "context hygiene."
- **UX:** 
    - **Dual Mode:** Works as both a **Claude Code Plugin** (via slash commands) and a **Global CLI Tool**.
    - **Multi-Agent Support:** Supports Claude Code, OpenCode, Gemini, Qwen, and Crush.
    - **Unified Agent Framework:** Contract-aware agent selection based on task requirements and budget.
    - **OSA Architecture:** Role-based task execution (Orchestrator, Architect, Coder, Security, QA).
    - **Voice Feedback:** Optional Text-to-Speech (TTS) integration via `tts-cli` or `local-tts-mcp`.

## Core Architecture: The Ralph Loop

The system follows a specific agentic pattern:

1.  **Planner:** Takes the initial prompt and generates a `YOLO_PLAN.md` file containing a checklist of tasks.
2.  **Executor Loop:**
    - Reads `YOLO_PLAN.md`.
    - Identifies the next pending task (`[ ]`).
    - **Role Detection:** Assigns an OSA role (e.g., Architect, Coder) to the task.
    - **Agent Selection:** Selects the best agent (Claude, Qwen, etc.) based on contracts.
    - **Parallel Execution:** Can execute independent tasks in parallel.
    - Spawns a **fresh** agent instance (subprocess) to execute *only* that task.
    - **Autonomous Mode:** 
        - **Claude:** Uses `--dangerously-skip-permissions`
        - **OpenCode:** Uses env vars `OPENCODE_YOLO=true`
        - **Gemini/Qwen:** Uses `--yolo`
    - **Self-Correction:** The agent updates `YOLO_PLAN.md` to mark the task as done (`[x]`) upon success.
3.  **Completion & Feedback:**
    - When all tasks are done, the loop exits.
    - An interactive prompt asks the user for feedback or new tasks.
    - If feedback is provided, the plan is updated, and the loop resumes.

## Features

### 1. Autonomous Task Execution
- Breaks down complex goals into atomic steps.
- Executes steps sequentially or in parallel.
- Automatically handles file creation, editing, and command execution.

### 2. Context Hygiene
- Each task runs in a new process (`claude -p "..."` or `opencode run "..."`).
- Prevents the context window from filling up with previous task history.
- Reduces hallucination and "brain fog" in long sessions.

### 3. Unified Agent Framework (v0.1.9)
- **Contract-Aware:** Selects agents based on capabilities and cost contracts.
- **Multi-Provider:** seamless switching between Claude, Gemini, Qwen, and OpenCode.
- **Resource Management:** Tracks token usage and budget across the session.

### 4. OSA Role System (v0.1.9)
- **Orchestrator:** Manages the overall plan and dependencies.
- **Architect:** Designs system structures and interfaces.
- **Coder:** Implements code changes.
- **Security:** Reviews code for vulnerabilities.
- **QA:** Validates implementation and runs tests.

### 5. Parallel Execution (v0.1.9)
- Uses `ThreadPoolExecutor` to run non-dependent tasks simultaneously.
- significantly speeds up multi-file edits or independent component creation.

### 6. Voice Feedback (TTS)
- Integration with `tts-cli` (Pocket TTS).
- Announces:
    - Mission Start
    - Plan Initialization
    - Task Execution (concise)
    - Task Completion
    - Mission Success/Failure
- **UX Design:** Uses blocking calls and delays to ensure audio doesn't overlap or overwhelm.

### 7. Interactive Feedback Loop
- At the end of a mission, the user is prompted: "Do you have any feedback or new tasks?"
- Allows for iterative refinement without restarting the context.

### 8. Dual Distribution
- **Plugin:** Installable into Claude Code via marketplace (`/yolo`, `/yolo-tts`).
- **CLI:** Installable via pip (`yolo-mode`).

### 9. Slash Commands
- `/yolo <goal>` - Start YOLO Mode with the specified goal
- `/yolo-tts <goal>` - Start YOLO Mode with TTS enabled
- `/restart-yolo` - Restart the current YOLO session and reset iteration count
- **Arguments:** Supports `--agent <name>` flag (e.g., `/yolo "Build app" --agent opencode`)

## Plugin Structure

```
yolo-mode/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest
│   └── marketplace.json     # Marketplace configuration
├── commands/
│   ├── yolo.md              # /yolo slash command
│   ├── yolo-tts.md          # /yolo-tts slash command
│   └── restart-yolo.md      # /restart-yolo slash command
├── yolo_mode/
│   ├── __init__.py
│   ├── agents/              # Unified Agent Framework
│   └── scripts/
│       └── yolo_loop.py     # Core loop implementation
├── setup.py                 # CLI packaging
├── README.md
└── llms.txt/                # AI documentation
    ├── PRD.md
    ├── RULES.md
    ├── TODO.md
    ├── ARCHITECTURE.md
    └── CURRENT_STATE.md
```

## Technical Stack
- **Language:** Python 3
- **Dependencies:** `claude` (CLI) OR `opencode` (CLI), `tts-cli` (optional)
- **Distribution:** `setuptools` (setup.py)
- **Plugin System:** Claude Code Plugin API (v2)

## Installation Methods

### As Claude Code Plugin (Recommended)
```bash
claude plugin marketplace add nbiish/yolo-mode
claude plugin install yolo-mode@yolo-marketplace
```
