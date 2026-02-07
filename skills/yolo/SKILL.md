---
name: yolo
description: Enables YOLO mode to autonomously work on a task until completion.
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
2. Spawn autonomous agents to complete the tasks.
3. Loop until all tasks are verified and completed.
4. Ask for feedback or new tasks upon completion.
