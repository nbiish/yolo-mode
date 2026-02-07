#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import re
import time

def speak(text, enabled=False):
    """Speaks the text using tts-cli if enabled, with a BLOCKING pause to prevent overlap."""
    if enabled:
        try:
            # Shorten very long texts for TTS
            if len(text) > 100:
                text = text[:97] + "..."
            
            # Suppress output from tts-cli to avoid cluttering logs
            subprocess.run(["tts-cli", "--text", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            # Add a small buffer after the command finishes to separate thoughts
            time.sleep(0.5) 
        except Exception as e:
            # Silently fail or log to stderr if absolutely needed, but keep main output clean
            pass

def run_agent(agent, prompt, verbose=False):
    """Runs the specified agent in autonomous mode."""
    
    cmd = []
    
    if agent == "claude":
        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--no-session-persistence"
        ]
    elif agent == "opencode":
        # Opencode requires environment variable for YOLO mode in some versions
        # CLI flags like --yolo or --dangerously-skip-permissions are not always available
        cmd = ["opencode", "run", prompt]
        env_vars = os.environ.copy()
        env_vars["OPENCODE_YOLO"] = "true"
        env_vars["OPENCODE_DANGEROUSLY_SKIP_PERMISSIONS"] = "true"
    elif agent == "gemini":
        cmd = ["gemini", "--yolo", prompt]
    elif agent == "qwen":
        cmd = ["qwen", "--yolo", prompt]
    elif agent == "crush":
        cmd = ["crush", "run", prompt]
    else:
        # Fallback for generic tools that might support the prompt as last arg
        # or we could error out. For now, assume a simple pass-through if unknown,
        # but better to warn.
        print(f"⚠️ Unknown agent '{agent}', defaulting to claude-style invocation")
        cmd = [agent, prompt]

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] Running {agent} task...")
    
    # We run capturing output to avoid cluttering the main terminal too much,
    # but we print it if verbose.
    try:
        # Pass env_vars if they exist, otherwise default to os.environ
        run_env = locals().get('env_vars', None)
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=run_env)
        
        if result.returncode != 0:
            print(f"Error running {agent}: {result.stderr}")
            return None
        
        if verbose:
            print(f"Output: {result.stdout.strip()}")
            
        return result.stdout
    except FileNotFoundError:
        print(f"❌ Agent '{agent}' not found in PATH.")
        return None

def clean_text_for_tts(text):
    """Removes markdown and other noise for clearer speech."""
    return text.replace('`', '').replace('*', '').replace('#', '').strip()

def main():
    parser = argparse.ArgumentParser(description="YOLO Mode Loop")
    parser.add_argument("prompt", nargs="+", help="The main goal/prompt")
    parser.add_argument("--tts", action="store_true", help="Enable TTS output via tts-cli")
    parser.add_argument("--agent", default="claude", help="The CLI agent to use (claude, opencode, gemini, etc.)")
    args = parser.parse_args()

    goal = " ".join(args.prompt)
    use_tts = args.tts
    agent = args.agent
    plan_file = "YOLO_PLAN.md"
    
    print(f"🚀 Starting YOLO Mode with {agent} for goal: {goal}")
    if use_tts:
        clean_goal = clean_text_for_tts(goal)
        speak(f"Starting YOLO Mode with {agent} for: {clean_goal}", True)
        time.sleep(1) # Extra pause after start

    # Ensure we are in the right directory (cwd)
    # The script is likely run from the project root.
    
    while True: # Main loop for feedback
        # Step 1: Initialize Plan
        if not os.path.exists(plan_file):
            print("📋 Initializing plan...")
            if use_tts:
                speak("Initializing plan.", True)
                
            init_prompt = f"""
            Goal: {goal}
            
            You are an autonomous planner using {agent}.
            Create a detailed plan to achieve this goal. 
            Write the plan to a file named '{plan_file}'.
            
            The file format MUST be:
            - [ ] Task description
            - [ ] Another task
            
            Do not include any completed tasks yet. Just the initial plan.
            Use the available tools (Bash, Write, etc.) to create the file.
            """
            run_agent(agent, init_prompt, verbose=True)
        else:
            print(f"📋 Found existing {plan_file}, resuming...")
            if use_tts:
                speak("Resuming existing plan.", True)

        # Step 2: Loop
        iteration = 0
        max_iterations = 50 # Safety limit
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}")
            
            if not os.path.exists(plan_file):
                print(f"❌ {plan_file} missing. Aborting.")
                if use_tts:
                    speak("Error. Plan file is missing.", True)
                break
                
            with open(plan_file, "r") as f:
                plan_content = f.read()
                
            # Find next pending task
            # Regex to find "- [ ] something"
            # We look for lines starting with "- [ ]"
            match = re.search(r"-\s*\[\s*\]\s*(.*)", plan_content)
            
            if not match:
                print("✅ No more pending tasks found. Mission Complete!")
                if use_tts:
                    speak("All tasks completed. Mission accomplished.", True)
                break
                
            current_task = match.group(1).strip()
            print(f"🔨 Executing Task: {current_task}")
            if use_tts:
                clean_task = clean_text_for_tts(current_task)
                speak(f"Executing: {clean_task}", True)
            
            # Construct Prompt for the worker
            # We instruct it to update the plan status itself after completion
            worker_prompt = f"""
            You are an autonomous worker in a loop using {agent}.
            
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
            
            output = run_agent(agent, worker_prompt, verbose=True)
            
            if output is None:
                 if use_tts:
                     speak(f"Error executing task: {clean_task}", True)
            
            # Verification: Check if plan was updated
            with open(plan_file, "r") as f:
                new_content = f.read()
                
            if plan_content != new_content:
                # Plan changed, assume success
                if use_tts:
                    speak(f"Completed task: {clean_task}", True)
            else:
                print("⚠️ Warning: Plan was not updated.")
                if use_tts:
                    speak("Warning: Plan not updated.", True)
                
                # Simple retry prevention logic could go here
            
            time.sleep(1) # Brief pause

        if iteration >= max_iterations:
            print("🛑 Max iterations reached. Stopping.")
            if use_tts:
                speak("Maximum iterations reached. Stopping.", True)
        
        # Interactive Feedback Loop
        print("\n--- Mission Complete ---")
        if use_tts:
             speak("Do you have any feedback or additional tasks?", True)
             
        try:
            user_input = input("❓ Do you have any feedback or new tasks? (Press Enter to exit): ").strip()
        except EOFError:
            break
            
        if not user_input:
            print("👋 Exiting YOLO Mode.")
            if use_tts:
                speak("Exiting YOLO Mode. Goodbye.", True)
            break
            
        print(f"📝 Updating plan with new feedback: {user_input}")
        if use_tts:
            speak("Updating plan with new feedback.", True)
            
        # Append new task/feedback to plan
        update_prompt = f"""
        The user has provided feedback/new tasks after the previous plan completion.
        
        Previous Goal: {goal}
        User Feedback: {user_input}
        
        Please update '{plan_file}' to include new tasks based on this feedback.
        Append them as new checklist items "- [ ] Task".
        Do NOT remove completed tasks.
        """
        run_agent(agent, update_prompt, verbose=True)
        # Loop continues...

if __name__ == "__main__":
    main()
