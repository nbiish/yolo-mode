# Rules

## Autonomous Operation (YOLO)

- **Permission Skipping:** The loop explicitly uses `--dangerously-skip-permissions`. This is a core feature, not a bug. It enables true autonomy.
- **Safety:** Because permissions are skipped, this tool should generally be used in sandboxed environments or git-initialized repositories where changes can be reverted.
- **Transparency:** All operations are logged to `YOLO_PLAN.md` for review.

## Context Hygiene

- **Fresh Instances:** Never reuse the same `claude` process for multiple tasks in the loop. Spawn a new one for each task.
- **State Persistence:** Use the file system (`YOLO_PLAN.md`) to persist state between agents. Do not rely on session history.
- **No Session Persistence:** Uses `--no-session-persistence` to ensure clean state.

## UX & TTS

- **Conciseness:** TTS messages must be short and to the point. Truncate long prompts (`text[:97] + "..."`).
- **Pacing:** Always add a delay (`time.sleep`) after speaking to allow the user to process the audio.
- **Clean Output:** Suppress stdout/stderr from `tts-cli` to keep the terminal logs clean for the user.
- **Blocking Calls:** TTS uses blocking subprocess calls to prevent audio overlap.

## Plugin Development

- **Command Structure:** Slash commands are defined as `.md` files in the `commands/` directory with YAML frontmatter.
- **Frontmatter Required:** Use `---` delimiters with `description` and `argument-hint` fields.
- **Shell Execution:** Use ``!`command` `` syntax in command files for shell execution.
- **Arguments:** Use `$ARGUMENTS` to capture user input.
- **No JSON Config:** Do NOT use `slash-commands.json` - Claude Code uses Markdown-based commands.

## Code Standards

- **Python:** Use standard library where possible to minimize dependencies.
- **Error Handling:** Silently handle TTS failures to avoid breaking the main loop.
- **Max Iterations:** Safety limit of 50 iterations to prevent infinite loops.
- **Plan Format:** Use `- [ ] task description` format for pending tasks, `- [x]` for completed.

## Release Checklist

- [x] Core loop implemented
- [x] Plugin manifest created
- [x] Marketplace configuration added
- [x] Slash commands working (`commands/*.md`)
- [x] CLI packaging configured
- [x] Documentation complete
- [ ] Version bumped in all files
- [ ] Git tagged
