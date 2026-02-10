---
description: "Start YOLO Mode with TTS feedback"
argument-hint: "<goal/prompt>"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/commands/run_yolo.sh:*)"]
hide-from-slash-command-tool: "true"
---

# YOLO Mode (TTS)

Initialize autonomous YOLO mode with TTS.

(Note: TTS support in native loop is pending implementation in stop-hook.sh)

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh" "$ARGUMENTS"
```

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.

