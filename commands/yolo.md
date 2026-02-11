---
description: "Start YOLO Mode - autonomous agent loop"
argument-hint: "<goal/prompt>"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh:*)"]
---

# YOLO Mode

Initialize autonomous YOLO mode with goal: $ARGUMENTS

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.

Run the YOLO Mode autonomous loop:
!`${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh` $ARGUMENTS

