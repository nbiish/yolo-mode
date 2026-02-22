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
agent = DefaultAgent(LitellmModel(model_name="minimax/minimax-m2.5"), LocalEnvironment())
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

## Model Selection (2026 Recommendations)

### Best Value (Cost-Effective)
| Model | Provider | Cost/M tokens | Use Case |
|-------|----------|---------------|----------|
| **MiniMax M2.5** | MiniMax | $0.03 | Best overall value |
| **Kimi K2.5** | Moonshot AI | $0.04 | Long context tasks |
| **GLM-4.5** | Zhipu AI | $0.05 | Chinese/English bilingual |
| **Qwen2.5-Coder-32B** | Alibaba | $0.08 | Code-specialized |

### Premium Performance
| Model | Provider | Cost/M tokens | Use Case |
|-------|----------|---------------|----------|
| **GPT-4.1** | OpenAI | $0.40 | Complex reasoning |
| **Claude Sonnet 4.5** | Anthropic | $0.30 | Code quality |
| **Gemini 2.5 Pro** | Google | $0.25 | Multimodal tasks |

### Budget Options
| Model | Provider | Cost/M tokens | Use Case |
|-------|----------|---------------|----------|
| **Llama 3.2 90B** | Meta (via OpenRouter) | $0.10 | General tasks |
| **DeepSeek-V3** | DeepSeek | $0.02 | Ultra-budget |

## Performance

| Metric | Value |
|--------|-------|
| SWE-bench | >74% |
| Lines of Code | ~100 |
| Startup Time | ~1s |

## Recommended Setup (2026)

For best cost-performance ratio:
```python
# Default: MiniMax M2.5 (best value)
agent = DefaultAgent(
    LitellmModel(model_name="minimax/minimax-m2.5"),
    LocalEnvironment()
)

# Complex tasks: GPT-4.1
agent = DefaultAgent(
    LitellmModel(model_name="gpt-4.1"),
    LocalEnvironment()
)

# Budget: DeepSeek-V3
agent = DefaultAgent(
    LitellmModel(model_name="deepseek/deepseek-chat"),
    LocalEnvironment()
)
```

## Resources

- GitHub: https://github.com/SWE-agent/mini-swe-agent
- Paper: https://arxiv.org/abs/2405.15793
- LiteLLM Providers: https://docs.litellm.ai/docs/providers
