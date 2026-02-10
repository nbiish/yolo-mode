#!/bin/bash

# YOLO Mode Stop Hook
# Drives the autonomous loop by checking YOLO_PLAN.md and feeding prompts back to Claude

set -euo pipefail

# 1. Check if we are in YOLO Mode
STATE_FILE=".claude/yolo-state.md"
PLAN_FILE="YOLO_PLAN.md"

if [[ ! -f "$STATE_FILE" ]]; then
  exit 0 # Not in YOLO mode, allow exit
fi

# Read status from frontmatter
STATUS=$(grep "^status:" "$STATE_FILE" | head -n 1 | awk '{print $2}')

if [[ "$STATUS" != "running" ]]; then
  exit 0 # YOLO mode finished or paused
fi

# Read other state variables
ITERATION=$(grep "^iteration:" "$STATE_FILE" | head -n 1 | awk '{print $2}')
MAX_ITERATIONS=$(grep "^max_iterations:" "$STATE_FILE" | head -n 1 | awk '{print $2}')
GOAL=$(grep "^goal:" "$STATE_FILE" | cut -d: -f2- | sed 's/^ "//;s/"$//')

# Check hydration
if [[ -z "$ITERATION" ]]; then ITERATION=0; fi
if [[ -z "$MAX_ITERATIONS" ]]; then MAX_ITERATIONS=50; fi

# Safety Check
if [[ "$ITERATION" -ge "$MAX_ITERATIONS" ]]; then
  echo "🛑 Max iterations ($MAX_ITERATIONS) reached."
  sed -i '' 's/^status: running/status: stopped/' "$STATE_FILE"
  exit 0
fi

# --- RALPH LOOP ROBUSTNESS CHECKS ---
# Read hook input (transcript path)
HOOK_INPUT=$(cat /dev/stdin)
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  # If we can't read the transcript, we can't safely drive the loop.
  # But technically we drive from YOLO_PLAN.md, so maybe we don't strictly need it?
  # Ralph Loop needs it to extract the last message for promises.
  # We might just log a warning and proceed, OR strictly fail.
  # Let's proceed but warn.
  echo "⚠️ Warning: Transcript not found at $TRANSCRIPT_PATH" >&2
fi
# ------------------------------------

# 2. Analyze Plan
NEXT_ACTION=""
SYSTEM_MSG=""

if [[ ! -f "$PLAN_FILE" ]]; then
  # Scenario A: No Plan -> Create One
  NEXT_ACTION="Create a detailed plan to achieve the goal: '$GOAL'. Write it to '$PLAN_FILE'. The file MUST use '- [ ] Task Name' format."
  SYSTEM_MSG="🔄 YOLO Mode (Iter $ITERATION) | Step 1: Initialize Plan"
else
  # Scenario B: Plan Exists -> Find Next Task
  # Look for first unchecked box "- [ ]"
  NEXT_TASK=$(grep -m 1 "^- \[ \]" "$PLAN_FILE" || true)

  if [[ -n "$NEXT_TASK" ]]; then
    # Found a pending task
    TASK_TEXT=$(echo "$NEXT_TASK" | sed 's/^- \[ \] //')
    NEXT_ACTION="Execute the next task from $PLAN_FILE: '$TASK_TEXT'. Perform all necessary actions (coding, testing, etc.). AFTER COMPLETION, edit $PLAN_FILE to mark this task as '[x]'. DO NOT ask the user for permission. DO NOT use AskUserQuestion. Make reasonable assumptions if needed."
    SYSTEM_MSG="🔄 YOLO Mode (Iter $ITERATION) | Role: OSA Orchestrator | Executing: $TASK_TEXT | Ref: yolo_mode/OSA.md"
  else
    # Scenario C: All Tasks Done -> Finish
    NEXT_ACTION="All tasks in $PLAN_FILE are marked completed. Verify the final result against the goal: '$GOAL'. If satisfactory, report success. If not, add new tasks to $PLAN_FILE. DO NOT ask the user for permission."
    SYSTEM_MSG="🔄 YOLO Mode (Iter $ITERATION) | Role: OSA Orchestrator | Verification Phase"
    
    # If we are verifying, we might want to stop after this if no new tasks added.
    # For now, let Claude decide to stop or add more tasks.
    # If Claude does nothing and tries to stop again, we need to handle that.
    # Actually, if Claude says "Done", we should probably let it exit.
    # But how do we know?
    # We can check if the LAST iteration was also "All Tasks Done".
    # For simplicity: execution continues unless Claude explicitly removes the state file or changes status.
  fi
fi

# 3. Update State (Increment Iteration)
NEXT_ITER=$((ITERATION + 1))
sed -i '' "s/^iteration: $ITERATION/iteration: $NEXT_ITER/" "$STATE_FILE"

# 4. Feed Prompt Back to Claude (Block Exit)
# We use `jq` to construct the JSON response required by the Stop hook
# Content is passed via stdin to avoid shell escaping issues

jq -n \
  --arg reason "$NEXT_ACTION" \
  --arg system "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $reason,
    "systemMessage": $system
  }'

exit 0
