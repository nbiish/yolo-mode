---
description: "Start YOLO Mode with TTS feedback"
argument-hint: "<goal/prompt>"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch", "Task"]
---

# YOLO Mode (TTS)

Initialize autonomous YOLO mode with TTS for goal: $ARGUMENTS

(Note: TTS support in native loop is pending implementation in stop-hook.sh)

The Ralph Loop hook will take over and autonomously execute tasks from `YOLO_PLAN.md`.

