# Architecture

## System Overview

YOLO Mode is a dual-mode autonomous agent system that can operate as either:
1. **Claude Code Plugin** - Integrated via slash commands (`/yolo`, `/yolo-tts`)
2. **Standalone CLI** - Direct Python execution

## Core Components

### 1. Ralph Loop Engine (`yolo_mode/scripts/yolo_loop.py`)

The heart of the system implementing the Plan-Execute-Verify cycle with parallel execution capabilities.

```
┌─────────────────┐
│  User Input     │
│  (Goal/Prompt)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Plan Creator   │ ──► Creates YOLO_PLAN.md
│  (Agent)        │     with task checklist
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Executor Loop  │
│  (while tasks)  │
└────────┬────────┘
         │
    ┌────┴───────────────────────────┐
    │                                │
    ▼                                ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Parallel Scheduler │    │  Unified Agent      │
│  (ThreadPool)       │    │  Framework          │
└────────┬────────────┘    └──────┬──────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐        ┌─────────────────┐
│  Task Execution │ ◄────► │  Agent Contract │
│  (Fresh Process)│        │  (Resource Mgr) │
└────────┬────────┘        └─────────────────┘
         │
         ▼ (all done?)
┌─────────────────┐
│  Feedback Loop  │ ──► User can add
│  (Interactive)  │     new tasks
└─────────────────┘
```

### 2. Unified Agent Framework (`yolo_mode/agents/`)

Handles abstraction over different LLM providers and CLI tools.

- **Registry:** Manages available agents (Claude, OpenCode, Gemini, Qwen).
- **Contracts:** Defines capabilities, costs, and constraints for each agent.
- **Role Detection:** Analyzes tasks to assign the most appropriate role (OSA).
- **Resource Aware:** Tracks usage against defined budgets.

### 3. OSA Role System

Tasks are dynamically assigned to specialized roles:

- **Orchestrator:** High-level planning and coordination.
- **Architect:** System design and structural decisions.
- **Coder:** Code generation and implementation.
- **Security:** Vulnerability scanning and safety checks.
- **QA:** Testing and verification.

### 4. Plugin System Integration

```
Claude Code Plugin Architecture
┌─────────────────────────────────────┐
│         Claude Code CLI             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Plugin Registry                │
│  (yolo-mode@yolo-marketplace)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Command Dispatcher             │
│  ┌──────────┐    ┌──────────────┐  │
│  │ /yolo    │    │ /yolo-tts    │  │
│  └────┬─────┘    └──────┬───────┘  │
└───────┼─────────────────┼──────────┘
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ commands/    │  │ commands/    │
│ yolo.md      │  │ yolo-tts.md  │
│ (frontmatter)│  │ (frontmatter)│
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌────────────────┐
       │ Python Script  │
       │ yolo_loop.py   │
       └────────────────┘
```

### 5. File Structure

```
yolo-mode/
│
├── .claude-plugin/           # Plugin metadata
│   ├── plugin.json          # Manifest (name, version, description)
│   └── marketplace.json     # Marketplace configuration
├── commands/                 # Slash command definitions
├── yolo_mode/               # Core Python package
│   ├── agents/              # Agent framework
│   └── scripts/             # Execution scripts
└── llms.txt/                # Context for AI models
```
