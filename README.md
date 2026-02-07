# YOLO Mode Plugin for Claude Code

**YOLO Mode** is a Claude Code plugin that implements the **Ralph Loop** pattern for autonomous agentic coding. It transforms Claude Code into a self-driving developer that can plan, execute, and verify complex tasks with minimal human intervention.

## Features

*   **Autonomous Loop**: Takes a high-level prompt and runs until the job is done.
*   **Context Hygiene**: Spawns a fresh Claude Code instance for each task, preventing context window saturation.
*   **Planning**: Automatically generates a `YOLO_PLAN.md` (Product Requirements Document) to track progress.
*   **TTS Feedback**: Speaks out status updates (optional).
*   **Interactive**: Asks for feedback at the end of the mission.
*   **Zero-Trust/YOLO**: Runs with `--dangerously-skip-permissions` to maximize autonomy.

## Installation

### 1. Global CLI Tool (Recommended)
You can install `yolo-mode` as a global command-line tool. This allows you to run it from any directory.

```bash
cd /path/to/yolo-mode
pip install -e .
```

Now you can run:
```bash
yolo-mode "Your goal here" --tts
```

### 2. Claude Code Plugin (Development)
To use it within Claude Code as a plugin:

1.  Launch Claude Code pointing to this directory:
    ```bash
    claude --plugin-dir /path/to/yolo-mode
    ```

2.  Run the slash command (Note the namespace!):
    ```text
    /yolo-mode:yolo "Your goal"
    ```
    or for TTS:
    ```text
    /yolo-mode:yolo-tts "Your goal"
    ```

## Usage

### As a CLI
```bash
# Basic
yolo-mode "Refactor the login page"

# With Voice Feedback
yolo-mode "Refactor the login page" --tts
```

### Inside Claude Code
```text
/yolo-mode:yolo "Refactor the login page"
```

## Configuration

No special configuration is required, but ensure you have:
*   `python3` installed and available.
*   `claude` CLI installed and authenticated.
*   `tts-cli` installed for voice features.

## Safety Warning ⚠️

This plugin uses the `--dangerously-skip-permissions` flag for its sub-agents. This means the autonomous agents can read/write files and execute terminal commands **without asking for your permission** each time.

*   **Only use this in a sandboxed environment** or on a repository you have backed up.
*   Monitor the output if you want to abort the process (Ctrl+C).

## License

MIT
