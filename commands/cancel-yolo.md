---
description: "Restart YOLO loop iteration (reset to 0)"
allowed-tools: ["Bash(test -f .claude/yolo-state.md:*)", "Bash(sed -i '' 's/^iteration: .*/iteration: 0/' .claude/yolo-state.md)", "Read(.claude/yolo-state.md)", "Bash(grep tts: .claude/yolo-state.md)", "mcp__local-tts__speak"]
hide-from-slash-command-tool: "true"
---

# Cancel YOLO

To restart the YOLO mode loop (reset iteration counter to 0):

1. Check if `.claude/yolo-state.md` exists using Bash: `test -f .claude/yolo-state.md && echo "EXISTS" || echo "NOT_FOUND"`

2. **If NOT_FOUND**: Say "No active YOLO mode found."

3. **If EXISTS**:
   - Read `.claude/yolo-state.md` to get the current iteration number from the `iteration:` field
   - Check if TTS is enabled: `grep -q "tts: true" .claude/yolo-state.md && echo "TTS_ENABLED" || echo "TTS_DISABLED"`
   - Reset the iteration counter to 0 using Bash: `sed -i '' 's/^iteration: .*/iteration: 0/' .claude/yolo-state.md`
   - Report: "Restarted YOLO mode loop (was at iteration N, now reset to 0)" where N is the iteration value
   - If TTS was enabled, use `mcp__local-tts__speak` to announce: "YOLO mode restarted. Iteration reset to zero."
