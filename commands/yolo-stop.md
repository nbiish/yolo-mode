---
description: "Stop YOLO Mode completely (disable the autonomous loop)"
allowed-tools: ["Bash"]
---

# Stop YOLO Mode

Stop the active YOLO mode loop by removing its state file.

Run:
!if test -f .claude/yolo-state.md; then TTS_ENABLED="$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' .claude/yolo-state.md | grep '^tts:' | sed 's/tts: *//')"; rm -f .claude/yolo-state.md .claude/yolo_feedback.md; echo "🛑 YOLO Mode stopped. (State cleared)"; if [ "${TTS_ENABLED:-false}" = "true" ] && command -v tts-cli >/dev/null 2>&1; then tts-cli --text "YOLO mode stopped." >/dev/null 2>&1 || true; fi; else echo "❌ No active YOLO session found."; fi
