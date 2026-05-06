# Current State

## Git Status
```
Run `git status` in the repo root to confirm current working tree state.
```

## Recent History
```
commit 64e8fe09c890c04ed44099efb60aa2bb273522d1 (HEAD -> main, origin/main, origin/HEAD)
Author: nbiish <nbiish@users.noreply.github.com>
Date:   Wed Feb 11 17:00:31 2026 -0500

    docs: improve YOLO mode command clarity and feedback TTS

commit c9debc039aebf67949841f0ba45951dec0ea113b
Author: nbiish <nbiish@users.noreply.github.com>
Date:   Wed Feb 11 12:24:32 2026 -0500

    feat(agents): add unified agent framework with contract-aware selection

commit 9ec94ebf19ca609eec8c0e99491ab4e7bec4f9a5
Author: nbiish <nbiish@users.noreply.github.com>
Date:   Tue Feb 10 22:01:29 2026 -0500

    feat: implement OSA framework with parallel execution in YOLO loop
```

## System Components
- **Core Loop:** `yolo_loop.py` (v0.2.0)
- **Agent Framework:** Unified, Contract-Aware
- **Roles:** OSA (Orchestrator, Security, Architect)
- **Plugin:** Claude Code Compatible
- **User Controls:** `/yolo-guide` (steer next iteration), `/yolo-stop` (stop loop completely)
- **Plugin Surface Area:**
  - **Skills (2):** `yolo`, `yolo-tts`
  - **Slash Commands (5 visible + 1 hidden):** `/yolo`, `/yolo-tts`, `/yolo-mini`, `/yolo-guide`, `/yolo-stop`, `/cancel-yolo` (hidden)

## Install & Test Checklist

### Claude Code Plugin (recommended)

1. Install Claude Code (once).
2. Open Claude Code in a repo you trust (ideally this repo).
3. Add marketplace + install plugin:
```
/plugin marketplace add nbiish/yolo-mode
/plugin install yolo-mode@yolo-marketplace
```
4. Apply changes without restarting:
```
/reload-plugins
```
5. Smoke test commands:
   - `/yolo "Define acceptance criteria and verification commands in YOLO_PLAN.md, then execute the first task."`
   - `/yolo-guide "Prefer small diffs and run the lightest correct verification."`
   - `/yolo-stop`
6. Verify state artifacts:
   - `YOLO_PLAN.md` created/updated
   - `.claude/yolo-state.md` created when running, removed after `/yolo-stop`

### CLI (standalone)

1. Ensure Python is installed and available on PATH.
2. Install in editable mode:
```
pip install -e .
```
3. Run:
```
yolo-mode "Define acceptance criteria and verification commands in YOLO_PLAN.md"
```
4. Optional agent selection:
```
yolo-mode "Audit for security issues in the repo" --agent opencode
```

## Troubleshooting Log

- 2026-05-05: Tool execution in this environment failed for basic shell commands (e.g. `date`) due to a missing sandbox wrapper (`trae-sandbox`). If you see similar errors locally, run commands directly in your shell or update/reinstall the runner environment.
- 2026-05-05: `python`/`python3` were not found in the current terminal environment during automated checks. Fix by installing Python and ensuring it is on PATH (or use your preferred Python manager) before using the CLI mode.
- 2026-05-05: User-confirmed local system time: Tue May  5 23:49:16 EDT 2026.
