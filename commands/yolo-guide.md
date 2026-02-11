---
description: "Guide active YOLO session with new instructions"
argument-hint: "<instructions/feedback>"
allowed-tools: ["Bash(echo * >> .claude/yolo_feedback.md)", "Bash(echo * > .claude/yolo_feedback.md)", "Bash(mkdir -p .claude)", "Bash(test -f .claude/yolo-state.md:*)", "Bash(grep tts: .claude/yolo-state.md)"]
---

# Guide YOLO Mode

Inject new instructions or feedback into the active YOLO mode loop.

The provided text will be included in the prompt for the next autonomous iteration.

Run:
!test -f .claude/yolo-state.md && mkdir -p .claude && echo "$ARGUMENTS" >> .claude/yolo_feedback.md && echo "✅ Feedback queued. It will be included in the next YOLO iteration." && if grep -q "tts: true" .claude/yolo-state.md 2>/dev/null; then if command -v tts-cli &> /dev/null; then tts-cli --text "Feedback received: $ARGUMENTS" >/dev/null 2>&1 || true; fi; fi || echo "❌ No active YOLO session found."
