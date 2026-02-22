# Architecture

## System Overview

YOLO Mode is a dual-mode autonomous agent system that can operate as either:
1. **Claude Code Plugin** - Integrated via slash commands (`/yolo`, `/yolo-tts`, `/yolo-mini`)
2. **Standalone CLI** - Direct Python execution
3. **Mini-SWE-Agent** - Integrated via Python API or `mini` CLI

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

- **Registry:** Manages available agents (Claude, OpenCode, Gemini, Qwen, **Mini-SWE-Agent**).
- **Contracts:** Defines capabilities, costs, and constraints for each agent.
- **Role Detection:** Analyzes tasks to assign the most appropriate role (OSA).
- **Resource Aware:** Tracks usage against defined budgets.

**Registered Agents (v0.2.0):**
| Agent | Primary Role | Capabilities |
|-------|--------------|--------------|
| Qwen | Coder | Code generation, refactoring, documentation |
| Gemini | Orchestrator | Planning, context management, multimodal |
| Crush | Security | Security audits, validation |
| Claude Code | Architect | Architecture design, code review |
| OpenCode | Security | Schema validation, security reviews |
| **Mini-SWE-Agent** | **Coder/QA** | **Bash-only SWE tasks, GitHub issues** |

### 2.5 Mini-SWE-Agent Integration (`yolo_mode/agents/mini_swe_agent.py`)

Mini-SWE-Agent is a ~100-line AI agent from Princeton/Stanford that scores >74% on SWE-bench verified.

**Key Features:**
- **Bash-Only:** No custom tools other than bash; works with any model
- **Linear History:** Simple message accumulation for debugging
- **Sandbox-Friendly:** Supports Docker, Podman, Singularity, Bubblewrap
- **Model Agnostic:** Works with all models via LiteLLM

**Integration Architecture:**
```
┌─────────────────────────┐
│  YOLO Mode Loop         │
│  (yolo_loop.py)         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  MiniSweAgentRunner     │
│  (mini_swe_agent.py)    │
│  - DefaultAgent         │
│  - LitellmModel         │
│  - LocalEnvironment     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Bash Execution         │
│  (subprocess.run)       │
└─────────────────────────┘
```

**Usage Patterns:**
```python
# Python API
from yolo_mode.agents import MiniSweAgentRunner

runner = MiniSweAgentRunner(model_name="gpt-4o")
result = runner.run("Write a sudoku game")

# CLI
mini "Write a sudoku game"
```

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
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ /yolo    │  │ /yolo-tts    │  │ /yolo-mini │ │
│  └────┬─────┘  └──────┬───────┘  └─────┬──────┘ │
└───────┼────────────────┼────────────────┼────────┘
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ commands/    │ │ commands/    │ │ commands/    │
│ yolo.md      │ │ yolo-tts.md  │ │ yolo-mini.md │
│ (frontmatter)│ │ (frontmatter)│ │ (frontmatter)│
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
               ┌────────────────┐
               │ Python Script  │
               │ yolo_loop.py   │
               │ + mini-swe-   │
               │   agent.py     │
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
│   ├── yolo.md              # Main YOLO mode command
│   ├── yolo-tts.md          # YOLO mode with TTS feedback
│   └── yolo-mini.md         # Mini-SWE-Agent execution
├── yolo_mode/               # Core Python package
│   ├── agents/              # Agent framework
│   │   ├── __init__.py
│   │   ├── registry.py      # Agent registry and selection
│   │   ├── runner.py        # Agent execution
│   │   ├── role_detection.py # Task-to-role mapping
│   │   ├── resource_aware.py # Contract-aware selection
│   │   └── mini_swe_agent.py # Mini-SWE-Agent integration
│   ├── scripts/             # Execution scripts
│   │   └── yolo_loop.py     # Main YOLO loop (OSA + Parallel)
│   └── contracts/           # Resource contracts
├── llms.txt/                # Context for AI models
│   ├── ARCHITECTURE.md      # This file
│   ├── PRD.md               # Product requirements
│   ├── RULES.md             # Development standards
│   ├── TODO.md              # Roadmap
│   ├── CURRENT_STATE.md     # Current system state
│   └── MINI_SWE_AGENT.md    # Mini-SWE-Agent documentation
└── setup.py                 # CLI packaging
```
