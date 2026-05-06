---
name: yolo
description: Enables YOLO Mode to iteratively plan, implement, verify, and converge on a completed coding outcome.
input:
  prompt:
    description: The task or goal for the autonomous loop.
    required: true
---

# YOLO Mode

To execute the YOLO mode loop, run the following command in the terminal:

```bash
yolo-mode "$prompt"
```

This tool will:
1. Initialize a task list based on your prompt.
2. Iterate on tasks as “experiments” (change → verify → keep/fix/revert), inspired by autoresearch-style loops.
3. Loop until the plan is complete and verification passes.

While it’s running (Claude Code plugin mode):
- Use `/yolo-guide "<feedback>"` to steer the next iteration.
- Use `/yolo-stop` to stop the autonomous loop completely.
