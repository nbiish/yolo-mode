# Mini-SWE-Agent Integration

## Overview

**Mini-SWE-Agent** is a minimal AI software engineering agent developed by Princeton & Stanford. Despite being only ~100 lines of Python, it scores **>74% on SWE-bench verified**.

## Installation

```bash
pip install mini-swe-agent
mini  # Run CLI
```

## Usage

### CLI
```bash
mini "Write a sudoku game"
```

### Python API
```python
from minisweagent import DefaultAgent, LitellmModel, LocalEnvironment
agent = DefaultAgent(LitellmModel(model_name="gpt-4o"), LocalEnvironment())
agent.run("Write a sudoku game")
```

## YOLO Mode Integration

### Agent Registry
- **Name**: Mini-SWE-Agent
- **CLI**: mini
- **OSA Roles**: Coder, QA
- **Priority**: 6

### Usage
```bash
/yolo "Build API" --agent mini
/yolo-mini "Write tests"
```

## Performance

| Metric | Value |
|--------|-------|
| SWE-bench | >74% |
| Lines of Code | ~100 |
| Startup Time | ~1s |

## Resources

- GitHub: https://github.com/SWE-agent/mini-swe-agent
- Paper: https://arxiv.org/abs/2405.15793

