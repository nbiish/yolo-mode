---
description: "Execute task with Mini-SWE-Agent"
argument-hint: "<task>"
allowed-tools: ["Bash"]
---

# Mini-SWE-Agent Execution

Run Mini-SWE-Agent with task: $ARGUMENTS

Mini-SWE-Agent is a ~100-line AI agent that scores >74% on SWE-bench verified.
It uses bash-only execution and works with any model via LiteLLM.

## Usage

```bash
mini "$ARGUMENTS"
```

## Python API

```python
from minisweagent import DefaultAgent, LitellmModel, LocalEnvironment

agent = DefaultAgent(
    LitellmModel(model_name="gpt-4o"),
    LocalEnvironment(),
)
agent.run("$ARGUMENTS")
```

## Examples

- /yolo-mini "Write a sudoku game"
- /yolo-mini "Fix the bug in src/auth.py"
- /yolo-mini "Create unit tests for utils.py"
