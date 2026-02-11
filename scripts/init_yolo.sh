#!/bin/bash
set -euo pipefail

# Initialize YOLO Mode State
# This script is called by /yolo-mode:yolo (commands/yolo.md)

# State file location
STATE_FILE=".claude/yolo-state.md"
PLAN_FILE="YOLO_PLAN.md"
USER_FEEDBACK_FILE=".claude/yolo_feedback.md"

# Ensure .claude directory exists
mkdir -p .claude

# Clear stale feedback
if [[ -f "$USER_FEEDBACK_FILE" ]]; then
    rm "$USER_FEEDBACK_FILE"
fi

# Determine Plugin Root (where this script lives -> parent -> parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
GOAL=""
TTS_ENABLED="false"
MAX_ITERATIONS=50

# Loop through arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tts)
      TTS_ENABLED="true"
      shift # past argument
      ;;
    --forever)
      MAX_ITERATIONS=1000
      shift # past argument
      ;;
    *)
      if [[ -z "$GOAL" ]]; then
        GOAL="$1"
      else
        GOAL="$GOAL $1"
      fi
      shift # past argument
      ;;
  esac
done

# Copy OSA Framework to local .claude directory for reference
mkdir -p ".claude"
cp "$PLUGIN_ROOT/yolo_mode/OSA.md" ".claude/OSA_FRAMEWORK.md"
echo "📚 OSA Framework loaded to .claude/OSA_FRAMEWORK.md"

# Initialize state file
cat > "$STATE_FILE" <<EOF
---
status: running
iteration: 0
max_iterations: $MAX_ITERATIONS
tts: $TTS_ENABLED
goal: "$GOAL"
---
EOF

echo "🚀 YOLO Mode Initialized."
echo "Goal: $GOAL"
if [[ "$TTS_ENABLED" == "true" ]]; then
    echo "🔊 TTS Enabled"
    # Announce start if TTS is enabled
    if command -v tts-cli &> /dev/null; then
        tts-cli --text "YOLO Mode Initialized. Goal: $GOAL" >/dev/null 2>&1 || true
    fi
fi
echo "State File: $STATE_FILE"
echo "⚠️  TIP: YOLO Mode works best with all tools allowed. Run with: claude --dangerously-skip-permissions"

# Check if PLAN_FILE exists
if [ ! -f "$PLAN_FILE" ]; then
    cat > "$PLAN_FILE" <<EOF
# YOLO Plan
Goal: $GOAL

## Guidance
**Reference:** \`.claude/OSA_FRAMEWORK.md\` (Read this to understand your Agentic Team roles)

## Todo
- [ ] Analyze the goal and create a detailed plan using OSA patterns
EOF
    echo "📋 Created initial plan: $PLAN_FILE"
else
    echo "📋 Found existing plan: $PLAN_FILE"
fi

echo "The Ralph Loop hook will now take over control."
