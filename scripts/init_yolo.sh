#!/bin/bash
set -euo pipefail

# Initialize YOLO Mode State
# This script is called by /yolo-mode:yolo (commands/yolo.md)

# State file location
STATE_FILE=".claude/yolo-state.md"
PLAN_FILE="YOLO_PLAN.md"

# Ensure .claude directory exists
mkdir -p .claude

# Determine Plugin Root (where this script lives -> parent -> parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

# Goal argument (all arguments passed to script)
GOAL="${*:-}"
MAX_ITERATIONS=50

# Check for --forever flag in the arguments
if [[ "$GOAL" == *"--forever"* ]]; then
    MAX_ITERATIONS=1000
    GOAL=${GOAL//--forever/} # Remove flag from goal
    echo "♾️  Forever Mode Enabled (Max Iterations: $MAX_ITERATIONS)"
fi

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
goal: "$GOAL"
---
EOF

echo "🚀 YOLO Mode Initialized."
echo "Goal: $GOAL"
echo "State File: $STATE_FILE"
echo "⚠️  TIP: For TRUE zero-interaction, allow all tools or run: claude --dangerously-skip-permissions"

# Check if PLAN_FILE exists
# Check if PLAN_FILE exists, if not create it with OSA Guidance
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
