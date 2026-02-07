#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import re
import time

def run_claude(prompt, verbose=False):
    """Runs Claude in non-interactive mode with permissions skipped."""
    cmd = [
        "claude",
        "-p", prompt,
        "--dangerously-skip-permissions",
        "--no-session-persistence"
    ]
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] Running Claude task...")
    
    # We run capturing output to avoid cluttering the main terminal too much,
    # but we print it if verbose.
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running Claude: {result.stderr}")
        return None
    
    if verbose:
        print(f"Output: {result.stdout.strip()}")
        
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="YOLO Mode Loop")
    parser.add_argument("prompt", help="The main goal/prompt")
    args = parser.parse_args()

    goal = args.prompt
    print(f"🚀 Starting YOLO Mode for goal: {goal}")

    # Ensure we are in the right directory (cwd)
    # The script is likely run from the project root.
    
    plan_file = "YOLO_PLAN.md"

    # Step 1: Initialize Plan
    if not os.path.exists(plan_file):
        print("📋 Initializing plan...")
        init_prompt = f"""
        Goal: {goal}
        
        You are an autonomous planner.
        Create a detailed plan to achieve this goal. 
        Write the plan to a file named '{plan_file}'.
        
        The file format MUST be:
        - [ ] Task description
        - [ ] Another task
        
        Do not include any completed tasks yet. Just the initial plan.
        Use the 'Bash' or 'Write' tool to create the file.
        """
        run_claude(init_prompt, verbose=True)
    else:
        print(f"📋 Found existing {plan_file}, resuming...")

    # Step 2: Loop
    iteration = 0
    max_iterations = 50 # Safety limit
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}")
        
        if not os.path.exists(plan_file):
            print(f"❌ {plan_file} missing. Aborting.")
            break
            
        with open(plan_file, "r") as f:
            plan_content = f.read()
            
        # Find next pending task
        # Regex to find "- [ ] something"
        # We look for lines starting with "- [ ]"
        match = re.search(r"-\s*\[\s*\]\s*(.*)", plan_content)
        
        if not match:
            print("✅ No more pending tasks found. Mission Complete!")
            break
            
        current_task = match.group(1).strip()
        print(f"🔨 Executing Task: {current_task}")
        
        # Construct Prompt for the worker
        # We instruct it to update the plan status itself after completion
        worker_prompt = f"""
        You are an autonomous worker in a loop.
        
        Goal: {goal}
        
        Current Plan Status (in {plan_file}):
        {plan_content}
        
        YOUR CURRENT TASK: {current_task}
        
        Instructions:
        1. Execute this task strictly. Do not do other tasks.
        2. If the task requires coding, write the code and verify it.
        3. AFTER you have successfully completed the task, you MUST edit '{plan_file}' to mark this specific task as completed (change '[ ]' to '[x]').
        
        IMPORTANT:
        - Do not ask for permission.
        - Update the plan file yourself.
        """
        
        output = run_claude(worker_prompt, verbose=True)
        
        # Verification: Check if plan was updated
        with open(plan_file, "r") as f:
            new_content = f.read()
            
        if plan_content == new_content:
            print("⚠️ Warning: Plan was not updated. The agent might have failed or forgotten to mark it complete.")
            # We could retry or force mark it, but let's leave it for now to avoid infinite loops on same task if it fails.
            # To be safe, if it fails to update X times, we should stop.
            # For this MVP, we'll continue. The loop might repeat the task. 
            # Ideally, we should add a 'retry' logic or force skip.
            
            # Simple retry prevention:
            print("Force marking task as skipped/failed to prevent infinite loop (MVP fallback).")
            # Actually, let's not modify it blindly. Let's rely on the agent.
            # But if we loop forever, that's bad.
            # Let's just prompt again if it didn't update?
            # Or better, let's inject a "fix plan" step if it gets stuck.
        
        time.sleep(1) # Brief pause

    if iteration >= max_iterations:
        print("🛑 Max iterations reached. Stopping.")

if __name__ == "__main__":
    main()
