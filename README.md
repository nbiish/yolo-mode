# YOLO Mode Plugin for Claude Code

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/nbiish/yolo-mode)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Transform Claude Code into a self-driving developer**

**YOLO Mode** implements the **Ralph Loop** pattern for autonomous agentic coding. It plans, executes, and verifies complex tasks with minimal human intervention while maintaining context hygiene through fresh context windows.

<div align="center">
  <hr width="50%">
  <h3>Support This Project</h3>
  <table style="border: none; border-collapse: collapse;">
    <tr style="border: none;">
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <h4>Stripe</h4>
        <img src="qr-stripe-donation.png" alt="Scan to donate" width="180"/>
        <p><a href="https://raw.githubusercontent.com/nbiish/license-for-all-works/8e9b73b269add9161dc04bbdd79f818c40fca14e/qr-stripe-donation.png">Donate via Stripe</a></p>
      </td>
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <a href="https://www.buymeacoffee.com/nbiish">
          <img src="buy-me-a-coffee.svg" alt="Buy me a coffee" />
        </a>
      </td>
    </tr>
  </table>
  <hr width="50%">
</div>

## ✨ Features

- **🤖 Autonomous Loop**: Takes a high-level prompt and runs until completion
- **🧠 Context Hygiene**: Fresh Claude instances per task prevent context saturation
- **📝 Smart Planning**: Auto-generates `YOLO_PLAN.md` to track progress
- **🔊 TTS Feedback**: Optional voice announcements via `tts-cli`
- **💬 Interactive**: Post-mission feedback loop for refinement
- **⚡ Zero-Trust/YOLO**: Uses `--dangerously-skip-permissions` for maximum autonomy
- **🎯 Dual Mode**: Works as Claude Code plugin OR standalone CLI
- **🚀 Mini-SWE-Agent**: Integrated support for the ~100-line AI agent (>74% SWE-bench)

## 🚀 Quick Start

### Option 1: Claude Code Plugin (Recommended)

In Claude Code, add the marketplace and install the plugin:

```
/plugin marketplace add nbiish/yolo-mode
/plugin install yolo-mode@yolo-marketplace
```

If you install/enable/disable plugins during a session, run:
```
/reload-plugins
```

**Use in Claude Code:**
```
/yolo "Refactor the authentication system"
/yolo "Audit security" --agent opencode
/yolo-tts "Build a React component library"  # With voice feedback
/yolo-guide "Focus on small diffs, add tests, and keep changes minimal"
/yolo-stop
```

**Plugin Surface Area (what should appear in Claude Code):**
- **Skills (2):** `yolo`, `yolo-tts`
- **Slash Commands (5 visible + 1 hidden):**
  - `/yolo <goal>` - Start YOLO loop
  - `/yolo-tts <goal>` - Start YOLO loop with TTS
  - `/yolo-mini <task>` - Run a single task via Mini-SWE-Agent
  - `/yolo-guide <feedback>` - Queue guidance for the next iteration
  - `/yolo-stop` - Stop the loop and clear state
  - `/cancel-yolo` - Hidden; resets iteration counter to 0

### Option 2: Global CLI Tool

```bash
# Install from source
git clone https://github.com/nbiish/yolo-mode.git
cd yolo-mode
pip install -e .

# Run anywhere
yolo-mode "Your goal here" --tts
yolo-mode "Your goal here" --agent opencode
```

## 📖 Usage Examples

### As Plugin (Inside Claude Code)
```
/yolo "Create a REST API with FastAPI"
/yolo-tts "Write unit tests for the utils module"
```

### As CLI
```bash
# Basic usage (defaults to Claude Code)
yolo-mode "Implement user authentication"

# With OpenCode
yolo-mode "Refactor database schema" --agent opencode

# With Google Gemini
yolo-mode "Generate documentation" --agent gemini

# With Mini-SWE-Agent (NEW in v0.2.0)
yolo-mode "Write a sudoku game" --agent mini
/yolo-mini "Create unit tests for utils.py"  # Slash command

# With voice feedback
yolo-mode "Build a dashboard" --tts

# Complex multi-step goal
yolo-mode "Set up a CI/CD pipeline with GitHub Actions, Docker, and AWS deployment"
```

## 🔧 Requirements

- **Python 3.8+**
- **Supported Agents:**
  - **Claude Code** (default) - `npm install -g @anthropic-ai/claude-code`
  - **OpenCode** - `brew install opencode`
  - **Gemini CLI**
  - **Qwen**
  - **Crush**
  - **Mini-SWE-Agent** - `pip install mini-swe-agent` (NEW in v0.2.0)
- **tts-cli** (optional) - For voice feedback

## 🧠 Recommended Models (Cost/Quality)

YOLO Mode assumes your preferred provider + default model are already configured for each CLI tool (Claude/Gemini/OpenCode/etc.). When you *can* select a model (via a CLI flag or provider config), prefer:

- **DeepSeek V4 Pro (ZenMux)**: `deepseek/deepseek-v4-pro` (flagship, tuned for agentic coding). Source: https://zenmux.ai/provider/deepseek
- **DeepSeek V4 Flash (OpenRouter)**: lower-cost DeepSeek V4 tier for high-throughput coding/agent workloads. Source: https://openrouter.ai/deepseek/deepseek-v4-flash

## ⚠️ Anti-Stall & Zero Interaction

To achieve **true autonomous operation** without permission prompts for every tool use, you MUST start Claude Code with the following flag:

```bash
claude --dangerously-skip-permissions
```

If you do not use this flag, the "YOLO Mode" loop will pause and wait for your approval whenever the agent tries to use a tool (Bash, File Edit, etc.), defeating the purpose of autonomous operation.

**Recommendations:**
- ✅ Use in version-controlled repositories
- ✅ Review `YOLO_PLAN.md` before execution
- ✅ Run in sandboxed/development environments
- ❌ Never use on production systems without review

## 🏗️ How It Works

```
User Goal
    ↓
[Planner] Creates YOLO_PLAN.md with task checklist
    ↓
[Executor Loop] While tasks remain:
    - Reads next pending task
    - Spawns fresh Claude instance
    - Executes task autonomously
    - Updates plan file
    ↓
[Feedback] Ask user for additional tasks
```

## 📁 Project Structure

```
yolo-mode/
├── .claude-plugin/      # Plugin metadata
├── commands/            # Slash command definitions
│   ├── yolo.md
│   └── yolo-tts.md
│   ├── yolo-mini.md
│   ├── yolo-guide.md
│   └── yolo-stop.md
├── yolo_mode/          # Python package
│   └── scripts/
│       └── yolo_loop.py
├── llms.txt/           # AI documentation
└── setup.py            # CLI packaging
```

## 📚 Documentation

- **[PRD](llms.txt/PRD.md)** - Product Requirements Document
- **[ARCHITECTURE](llms.txt/ARCHITECTURE.md)** - System design and data flow
- **[RULES](llms.txt/RULES.md)** - Development standards
- **[TODO](llms.txt/TODO.md)** - Roadmap and status
- **[MINI_SWE_AGENT](llms.txt/MINI_SWE_AGENT.md)** - Mini-SWE-Agent integration guide

## 🔄 Version History

- **v0.2.0** - Mini-SWE-Agent integration, `/yolo-mini` command, updated agent registry
- **v0.1.1** - Fixed slash commands, proper `commands/*.md` structure
- **v0.1.0** - Initial release with Ralph Loop pattern

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) file.


## Citation

```bibtex
@misc{yolo-mode2026,
  author/creator/steward = {ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians},
  title/description = {yolo-mode},
  type_of_work = {Indigenous digital creation/software incorporating traditional knowledge and cultural expressions},
  year = {2026},
  publisher/source/event = {GitHub repository under tribal sovereignty protections},
  howpublished = {\url{https://github.com/nbiish/yolo-mode}},
  note = {Authored and stewarded by ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Indigenous intellectual property, traditional knowledge systems (TK), traditional cultural expressions (TCEs), and associated data protected under tribal law, federal Indian law, treaty rights, Indigenous Data Sovereignty principles, and international indigenous rights frameworks including UNDRIP. All usage, benefit-sharing, and data governance are governed by the COMPREHENSIVE RESTRICTED USE LICENSE FOR INDIGENOUS CREATIONS WITH TRIBAL SOVEREIGNTY, DATA SOVEREIGNTY, AND WEALTH RECLAMATION PROTECTIONS.}
}
```

## Copyright

Copyright © 2026 ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), a descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band, and an enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Traditional Knowledge and Traditional Cultural Expressions. All rights reserved.
