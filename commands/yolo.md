---
description: "Start YOLO Mode - autonomous agent loop"
argument-hint: "<goal/prompt>"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh:*)"]
hide-from-slash-command-tool: "true"
---

# YOLO Mode

Initialize autonomous YOLO mode.

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh" "$ARGUMENTS"
```

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.

