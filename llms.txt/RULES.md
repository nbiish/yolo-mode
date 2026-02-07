# Rules

## Autonomous Operation (YOLO)

- **Permission Skipping:** The loop explicitly uses `--dangerously-skip-permissions`. This is a core feature, not a bug. It enables true autonomy.
- **Safety:** Because permissions are skipped, this tool should generally be used in sandboxed environments or git-initialized repositories where changes can be reverted.

## Context Hygiene

- **Fresh Instances:** Never reuse the same `claude` process for multiple tasks in the loop. Spawn a new one for each task.
- **State Persistence:** Use the file system (`YOLO_PLAN.md`) to persist state between agents. Do not rely on session history.

## UX & TTS

- **Conciseness:** TTS messages must be short and to the point. Truncate long prompts (`text[:97] + "..."`).
- **Pacing:** Always add a delay (`time.sleep`) after speaking to allow the user to process the audio.
- **Clean Output:** Suppress stdout/stderr from `tts-cli` to keep the terminal logs clean for the user.
- **Namespacing:** When exposing skills to Claude Code, always use the `yolo-mode:` prefix if necessary to avoid conflicts, though the plugin system handles file-based namespacing.

## Development

- **Python:** Use standard library where possible to minimize dependencies.
- **Plugin Structure:** Follow the strict `.claude-plugin/` and `skills/` directory structure required by the Claude Code plugin system.
