---
description: "Start YOLO Mode in forever mode (continuous autonomous loop)"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh:*)"]
hide-from-slash-command-tool: "true"
---

# YOLO Mode (Forever)

Initialize autonomous YOLO mode in **Forever Mode**.
Max iterations set to 1000.
The loop will continue autonomously.

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh" "$ARGUMENTS" --forever
```

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.
