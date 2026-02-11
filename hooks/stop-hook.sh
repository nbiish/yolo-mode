#!/bin/bash

# YOLO Mode Stop Hook
# Prevents session exit when a YOLO loop is active
# Feeds Claude's output back as input to continue the loop (Ralph Loop Pattern)

set -euo pipefail

# Read hook input from stdin (advanced stop hook API)
HOOK_INPUT=$(cat)

# Check if yolo-loop is active
STATE_FILE=".claude/yolo-state.md"
PLAN_FILE="YOLO_PLAN.md"

if [[ ! -f "$STATE_FILE" ]]; then
  # No active loop - allow exit
  exit 0
fi

# Parse markdown frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
GOAL=$(echo "$FRONTMATTER" | grep '^goal:' | sed 's/goal: *//' | sed 's/^"\(.*\)"$/\1/')
TTS_ENABLED=$(echo "$FRONTMATTER" | grep '^tts:' | sed 's/tts: *//')

# Validate numeric fields
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "⚠️  YOLO loop: State file corrupted (iteration invalid)" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Helper function for TTS
speak() {
  local text="$1"
  if [[ "$TTS_ENABLED" == "true" ]]; then
     if command -v tts-cli &> /dev/null; then
        # Run in background to not block too much, or blocking? User wanted blocking in original requirements.
        # But for a hook, blocking might delay the next prompt.
        # Let's keep it simple and blocking for now to ensure audio finishes.
        # Truncate if too long
        if [[ ${#text} -gt 150 ]]; then
            text="${text:0:147}..."
        fi
        tts-cli --text "$text" >/dev/null 2>&1 || true
     fi
  fi
}

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "🛑 YOLO loop: Max iterations ($MAX_ITERATIONS) reached."
  speak "Maximum iterations reached. Stopping."
  rm "$STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "⚠️  YOLO loop: Transcript file not found" >&2
  rm "$STATE_FILE"
  exit 0
fi

# Check if tasks are complete by reading the plan file
# If all tasks are marked [x], we can stop (or ask for user feedback)
if [[ -f "$PLAN_FILE" ]]; then
    PENDING_TASKS=$(grep -c "\- \[ \]" "$PLAN_FILE" || true)
    if [[ "$PENDING_TASKS" -eq 0 ]]; then
        echo "✅ YOLO loop: All tasks in $PLAN_FILE are complete!"
        speak "All tasks completed. Mission accomplished."
        rm "$STATE_FILE"
        exit 0
    fi
fi

# Not complete - continue loop
NEXT_ITERATION=$((ITERATION + 1))

# Update iteration in state file
TEMP_FILE="${STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$STATE_FILE"

# Speak status
speak "Iteration $NEXT_ITERATION. Checking plan."

# Check for user feedback
USER_FEEDBACK_FILE=".claude/yolo_feedback.md"
USER_FEEDBACK_TEXT=""

if [[ -f "$USER_FEEDBACK_FILE" ]]; then
  USER_FEEDBACK_TEXT=$(cat "$USER_FEEDBACK_FILE")
  echo "📥 YOLO loop: Received user feedback."
  speak "User feedback received."
  # Clear the feedback file so it's not repeated
  rm "$USER_FEEDBACK_FILE"
fi

# Construct the prompt to feed back
# We remind the agent of the goal and to check the plan
FEEDBACK_PROMPT="
🔄 YOLO Iteration $NEXT_ITERATION
Goal: $GOAL

Please check '$PLAN_FILE' for the next pending task (- [ ]).
1. Execute the next task.
2. Mark it as [x] in the plan when done.
3. If you are stuck, update the plan with new findings.
"

# Inject user feedback if present
if [[ -n "$USER_FEEDBACK_TEXT" ]]; then
  FEEDBACK_PROMPT="$FEEDBACK_PROMPT

🚨 **USER INTERVENTION / FEEDBACK:**
$USER_FEEDBACK_TEXT
"
fi

SYSTEM_MSG="🔄 YOLO Mode Active | Iteration $NEXT_ITERATION/$MAX_ITERATIONS | Auto-driving..."

# Output JSON to block the stop and feed prompt back
jq -n \
  --arg prompt "$FEEDBACK_PROMPT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
