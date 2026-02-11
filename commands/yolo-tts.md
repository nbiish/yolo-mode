---
description: "Start YOLO Mode with TTS feedback"
argument-hint: "<goal/prompt>"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh:*)"]
---

# YOLO Mode (TTS)

Initialize autonomous YOLO mode (TTS enabled) with goal: $ARGUMENTS

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.

Run the YOLO Mode autonomous loop:
!`${CLAUDE_PLUGIN_ROOT}/scripts/init_yolo.sh` $ARGUMENTS --tts

