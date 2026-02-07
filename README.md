# YOLO Mode Plugin for Claude Code

**YOLO Mode** is a Claude Code plugin that implements the **Ralph Loop** pattern for autonomous agentic coding. It transforms Claude Code into a self-driving developer that can plan, execute, and verify complex tasks with minimal human intervention.

## Features

*   **Autonomous Loop**: Takes a high-level prompt and runs until the job is done.
*   **Context Hygiene**: Spawns a fresh Claude Code instance for each task, preventing context window saturation and "brain fog."
*   **Planning**: Automatically generates a `YOLO_PLAN.md` (Product Requirements Document) to track progress.
*   **Self-Correction**: Agents verify their own work and update the plan status.
*   **Zero-Trust/YOLO**: Runs with `--dangerously-skip-permissions` to maximize autonomy (use with caution!).

## Installation

### From Marketplace (Coming Soon)
```bash
/plugin install yolo-mode
```

### Local Development
To test or use this plugin locally:

1.  Clone the repository:
    ```bash
    git clone https://github.com/username/yolo-mode.git
    cd yolo-mode
    ```

2.  Run Claude Code with the plugin directory:
    ```bash
    claude --plugin-dir .
    ```

## Usage

Once the plugin is loaded, use the `/yolo` slash command followed by your objective:

```text
/yolo "Refactor the login component to use React Hooks and add unit tests"
```

### What Happens Next?
1.  **Planning Phase**: The system creates `YOLO_PLAN.md` with a checklist of tasks.
2.  **Execution Loop**:
    *   The system picks the first pending task.
    *   It launches a sub-agent to execute *just that task*.
    *   The agent modifies code, runs tests, and updates `YOLO_PLAN.md`.
3.  **Completion**: When all tasks are checked (`[x]`), the loop exits.

## Configuration

No special configuration is required, but ensure you have:
*   `python3` installed and available in your path.
*   `claude` CLI installed and authenticated.

## Safety Warning ⚠️

This plugin uses the `--dangerously-skip-permissions` flag for its sub-agents. This means the autonomous agents can read/write files and execute terminal commands **without asking for your permission** each time.

*   **Only use this in a sandboxed environment** or on a repository you have backed up.
*   Monitor the `scripts/yolo_loop.py` output if you want to abort the process (Ctrl+C).

## License

MIT
