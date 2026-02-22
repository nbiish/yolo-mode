# Integration Summary: Mini-SWE-Agent (v0.2.0)

## Overview

This document summarizes the integration of Mini-SWE-Agent into YOLO Mode, completed on February 22, 2026.

## What Was Integrated

**Mini-SWE-Agent** is a minimal AI software engineering agent developed by Princeton & Stanford that:
- Scores >74% on SWE-bench verified benchmark
- Consists of only ~100 lines of Python
- Uses bash-only execution (no custom tools needed)
- Works with any model via LiteLLM
- Supports multiple deployment modes (local, Docker, Podman, Singularity)

## Changes Made

### New Files Created
1. **yolo_mode/agents/mini_swe_agent.py** - Python API wrapper
2. **commands/yolo-mini.md** - Slash command definition
3. **llms.txt/MINI_SWE_AGENT.md** - Integration documentation

### Files Modified
1. **yolo_mode/agents/registry.py** - Added mini agent config
2. **yolo_mode/agents/__init__.py** - Added exports
3. **yolo_mode/scripts/yolo_loop.py** - Added mini execution support
4. **llms.txt/ARCHITECTURE.md** - Added architecture documentation
5. **llms.txt/TODO.md** - Added v0.2.0 completed items
6. **README.md** - Updated version and features
7. **.gitignore** - Updated by ainish-coder
8. **AGENTS.md** - Updated by ainish-coder

## Usage

### As Part of YOLO Loop
```bash
/yolo "Build a REST API" --agent mini
```

### Standalone Mode
```
/yolo-mini "Write unit tests for utils.py"
```

### CLI
```bash
yolo-mode "Write a sudoku game" --agent mini
```

### Python API
```python
from yolo_mode.agents import MiniSweAgentRunner, run_mini_swe_agent

# Using the runner class
runner = MiniSweAgentRunner(model_name="gpt-4o")
result = runner.run("Write a function to calculate fibonacci")

# Using convenience function
result = run_mini_swe_agent("Create a Flask API", model="gpt-4o")
```

## Agent Configuration

```python
"mini": AgentConfig(
    name="Mini-SWE-Agent",
    cli_command="mini",
    osa_roles={OSARole.CODER, OSARole.QA},
    capabilities={
        AgentCapability.CODE_GENERATION,
        AgentCapability.TESTING,
        AgentCapability.VALIDATION,
    },
    priority=6,
    description="100-line AI agent for SWE tasks (>74% SWE-bench)",
)
```

## OSA Role Mapping

| Role | Suitability | Use Case |
|------|-------------|----------|
| Coder | ✅ Primary | Code generation, implementation |
| QA | ✅ Primary | Testing, verification |
| Orchestrator | ⚠️ Limited | Use Gemini instead |
| Architect | ⚠️ Limited | Use Claude instead |
| Security | ⚠️ Limited | Use Crush/OpenCode instead |

## Performance

| Metric | Value |
|--------|-------|
| SWE-bench Verified | >74% |
| Lines of Code | ~100 |
| Startup Time | ~1s |
| Memory Usage | ~100MB |

## Installation

Users need to install mini-swe-agent separately:

```bash
pip install mini-swe-agent
```

Or using uv:
```bash
pip install uv && uvx mini-swe-agent
```

## Resources

- **GitHub**: https://github.com/SWE-agent/mini-swe-agent
- **Website**: https://mini-swe-agent.com
- **Paper**: https://arxiv.org/abs/2405.15793

## Git Commit

```
commit fc20167
Author: nbiish
Date: Sun Feb 22 13:25:00 2026

    feat: integrate Mini-SWE-Agent as first-class agent (v0.2.0)
    
    - Add mini-swe-agent to agent registry with Coder/QA roles
    - Create MiniSweAgentRunner wrapper with Python API and CLI support
    - Add /yolo-mini slash command for standalone execution
    - Update yolo_loop.py to support mini agent execution
    - Add comprehensive documentation in llms.txt/MINI_SWE_AGENT.md
    - Update ARCHITECTURE.md with mini-swe-agent integration details
    - Update README.md with v0.2.0 features and usage examples
    - Update TODO.md with v0.2.0 completed items
```

## Next Steps (Future Improvements)

- [ ] Docker Sandbox Support for isolated execution
- [ ] Batch Inference for multiple tasks
- [ ] GitHub issue auto-solving integration
- [ ] Custom environment configurations

---

*Document created: February 22, 2026*
*YOLO Mode Version: 0.2.0*

