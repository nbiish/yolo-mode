---
description: "Cancel active YOLO mode loop"
allowed-tools: ["Bash(test -f .claude/yolo-state.md:*)", "Bash(rm .claude/yolo-state.md)", "Read(.claude/yolo-state.md)"]
hide-from-slash-command-tool: "true"
---

# Cancel YOLO

To cancel the YOLO mode loop:

1. Check if `.claude/yolo-state.md` exists using Bash: `test -f .claude/yolo-state.md && echo "EXISTS" || echo "NOT_FOUND"`

2. **If NOT_FOUND**: Say "No active YOLO mode found."

3. **If EXISTS**:
   - Read `.claude/yolo-state.md` to get the current iteration number from the `iteration:` field
   - Remove the file using Bash: `rm .claude/yolo-state.md`
   - Report: "Cancelled YOLO mode (was at iteration N)" where N is the iteration value
