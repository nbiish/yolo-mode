# Architecture

## System Overview

YOLO Mode is a dual-mode autonomous agent system that can operate as either:
1. **Claude Code Plugin** - Integrated via slash commands (`/yolo`, `/yolo-tts`)
2. **Standalone CLI** - Direct Python execution

## Core Components

### 1. Ralph Loop Engine (`yolo_mode/scripts/yolo_loop.py`)

The heart of the system implementing the Plan-Execute-Verify cycle.

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
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│Read  │  │Spawn │
│Plan  │  │Agent │
└──┬───┘  └──┬───┘
   │         │
   └────┬────┘
        │
        ▼
┌─────────────────┐
│  Task Execution │ ──► Updates YOLO_PLAN.md
│  (Fresh Agent)  │     marks task [x]
└────────┬────────┘
         │
         ▼ (all done?)
┌─────────────────┐
│  Feedback Loop  │ ──► User can add
│  (Interactive)  │     new tasks
└─────────────────┘
```

### 2. Plugin System Integration

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

### 3. File Structure

```
yolo-mode/
│
├── .claude-plugin/           # Plugin metadata
│   ├── plugin.json          # Manifest (name, version, description)
│   └── marketplace.json     # Distribution config
│
├── commands/                 # Slash command definitions
│   ├── yolo.md              # /yolo command
│   └── yolo-tts.md          # /yolo-tts command
│
├── yolo_mode/               # Python package
│   ├── __init__.py
│   └── scripts/
│       └── yolo_loop.py     # Core implementation
│
├── llms.txt/                # AI documentation
│   ├── PRD.md              # Product requirements
│   ├── RULES.md            # Development standards
│   ├── TODO.md             # Roadmap & status
│   └── ARCHITECTURE.md     # This file
│
├── scripts/                 # Legacy/alt scripts
│   └── yolo_loop.py        # Duplicate for CLI
│
├── setup.py                 # CLI packaging
└── README.md                # User documentation
```

### 4. Data Flow

**Plan Creation Phase:**
1. User provides goal via `/yolo <goal>`
2. Claude Code reads `commands/yolo.md`
3. Executes Python script with arguments
4. Script spawns new Agent instance (Claude/OpenCode/etc) with planning prompt
5. Creates `YOLO_PLAN.md` with task checklist

**Execution Phase:**
1. Loop reads `YOLO_PLAN.md`
2. Finds next `- [ ]` task
3. Spawns fresh Agent instance
4. Agent executes task
5. Agent updates plan file to `- [x]`
6. Repeat until all tasks complete

**Feedback Phase:**
1. All tasks marked complete
2. Prompt user for feedback
3. If feedback provided:
   - Add new tasks to plan
   - Continue execution loop
4. If no feedback:
   - Exit cleanly

## Key Design Decisions

### Context Hygiene
- **Fresh Processes:** Each task spawns `claude -p`, `opencode run`, etc.
- **State Externalization:** All state in `YOLO_PLAN.md`, never in memory
- **Isolation:** Errors in one task don't cascade to others

### Autonomy Level
- **Permission Skipping:** 
  - Claude: `--dangerously-skip-permissions`
  - OpenCode: `OPENCODE_YOLO=true`
- **Self-Correction:** Agents mark their own tasks complete
- **Safety Limit:** 50 iteration max to prevent infinite loops

### TTS Integration
- **Optional:** Only activates with `--tts` flag
- **Blocking:** Prevents audio overlap
- **Concise:** Long text truncated to 100 chars
- **Clean:** Suppresses tts-cli output

## Security Model

```
┌─────────────────────────────────────┐
│        Trust Boundaries             │
├─────────────────────────────────────┤
│  User (Trusted)                     │
│    │                                │
│    ▼                                │
│  YOLO Mode (User's Code)            │
│    │                                │
│    ▼                                │
│  Sub-agent (Isolated Process)       │
│    │                                │
│    ▼                                │
│  File System / Shell (Sandboxed)    │
└─────────────────────────────────────┘
```

**Assumptions:**
- User has reviewed code before installation
- Running in version-controlled directory
- Can rollback via git if needed

## Extension Points

### Adding New Slash Commands
1. Create `commands/<name>.md`
2. Add YAML frontmatter with `description` and `argument-hint`
3. Use ``!`command` `` for shell execution
4. Reference `$ARGUMENTS` for user input

### Customizing TTS
Currently hardcoded to `tts-cli`. To change:
- Modify `speak()` function in `yolo_loop.py`
- Update subprocess command
- Adjust truncation limits

### Error Recovery
Current: Simple pass-through. To enhance:
- Add retry counter per task
- Implement exponential backoff
- Add human-in-the-loop for failures

## Performance Considerations

- **Process Overhead:** Each task spawns new Claude process (~1-2s startup)
- **I/O Bound:** Plan file read/write on each iteration
- **Network:** Each sub-agent may make API calls
- **TTS Latency:** Adds ~0.5-1s per announcement

## Testing Strategy

```
┌─────────────────────────────────────┐
│         Test Pyramid                │
├─────────────────────────────────────┤
│  Unit:                               │
│    - speak() with mock tts-cli       │
│    - clean_text_for_tts()           │
│    - Plan parsing regex             │
├─────────────────────────────────────┤
│  Integration:                        │
│    - Full loop with mock Claude      │
│    - YOLO_PLAN.md I/O               │
├─────────────────────────────────────┤
│  E2E:                                │
│    - /yolo in actual Claude Code     │
│    - CLI execution                  │
└─────────────────────────────────────┘
```

## Future Architecture

### v0.2.0 Ideas
- **Parallel Execution:** Run independent tasks concurrently
- **Checkpoint System:** Save/restore mission state
- **Web Integration:** Sub-agents with search capability
- **Config System:** JSON/YAML configuration file

### v1.0.0 Vision
- **Visual Dashboard:** Web UI for monitoring
- **Plugin Ecosystem:** Third-party skill integration
- **Multi-Agent:** Coordinator + worker agents
- **API Server:** HTTP interface for external tools
