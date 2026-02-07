---
name: yolo-tts
description: Enables YOLO mode with Text-to-Speech feedback via tts-cli.
input:
  prompt:
    description: The task or goal for the autonomous loop.
    required: true
---

# YOLO Mode (TTS Enabled)

To execute the YOLO mode loop with spoken feedback, run the following command:

```bash
yolo-mode "$prompt" --tts
```

This tool will:
1. Initialize a task list based on your prompt.
2. Speak out status updates using `tts-cli`.
3. Spawn autonomous agents to complete the tasks.
4. Loop until all tasks are verified and completed.
5. Ask for feedback or new tasks upon completion (with spoken prompts).
