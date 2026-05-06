#!/usr/bin/env python3
"""
YOLO Mode Loop with Role-Based Agent Orchestration

Implements the OSA (Orchestrated System of Agents) Framework with:
- Role-based task routing (Orchestrator, Architect, Coder, Security, QA)
- Specialized prompts per persona
- Intelligent task-to-role detection
- Parallel task execution with dependency detection
- Contract-aware agent selection (NEW)
- Resource budget enforcement (NEW)
"""
import argparse
import subprocess
import os
import sys
import re
import time
import threading
import shlex
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Tuple, Set
from dataclasses import dataclass, field

# Import new agents module
try:
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from yolo_mode.agents import (
        AGENT_REGISTRY,
        detect_role_and_agent,
        run_agent as run_agent_new,
        OSARole,
        ResourceAwareSelector,
        build_contract_aware_prompt,
    )
    from yolo_mode.contracts import AgentContract, ContractMode, ContractFactory, ResourceDimension
    NEW_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: New agents module not available: {e}")
    print("   Falling back to legacy agent handling...")
    NEW_AGENTS_AVAILABLE = False


# ============================================================================
# OSA FRAMEWORK - ROLE DEFINITIONS
# ============================================================================

class RolePersona:
    """Defines a role persona with keywords and specialized prompts."""

    def __init__(self, name: str, keywords: List[str], system_prompt: str, agent_preference: str = None):
        self.name = name
        self.keywords = [kw.lower() for kw in keywords]
        self.system_prompt = system_prompt
        self.agent_preference = agent_preference  # Preferred agent for this role


# OSA Framework Role Personas based on .claude/OSA_FRAMEWORK.md
OSA_ROLES: Dict[str, RolePersona] = {
    "orchestrator": RolePersona(
        name="Orchestrator",
        keywords=["plan", "orchestrate", "coordinate", "manage", "organize", "design workflow", "review plan"],
        system_prompt="""You are the ORCHESTRATOR role in the OSA Framework.

Your responsibilities:
- Planning and task decomposition
- Progress tracking and coordination
- Ensuring tasks are properly ordered
- Managing dependencies between tasks

Approach: Think systematically, break down complex goals into clear steps.""",
        agent_preference="gemini"  # Good at orchestration per .osa/OSA.md
    ),

    "architect": RolePersona(
        name="Architect",
        keywords=["architecture", "schema", "design", "structure", "pattern", "interface", "api design", "database design"],
        system_prompt="""You are the ARCHITECT role in the OSA Framework.

Your responsibilities:
- System design and architecture
- Finding and applying patterns
- Defining structures and interfaces
- Ensuring scalability and maintainability

Approach: Think in terms of SOLID principles, DRY, KISS, YAGNI.
Consider the bigger picture and long-term implications.""",
        agent_preference="claude"
    ),

    "coder": RolePersona(
        name="Coder",
        keywords=["implement", "write", "code", "create", "build", "function", "class", "module", "script"],
        system_prompt="""You are the CODER role in the OSA Framework.

Your responsibilities:
- Implementation of designed solutions
- Writing clean, maintainable code
- Following coding standards (SOLID, DRY, KISS)
- Making focused, minimal changes

Approach: Write production-ready code that matches existing style.
Prioritize clarity and correctness over cleverness.""",
        agent_preference="qwen"  # Fast code generation per .osa/OSA.md
    ),

    "security": RolePersona(
        name="Security",
        keywords=["security", "audit", "validate", "sanitize", "authenticate", "authorize", "encrypt", "vulnerability", "secure"],
        system_prompt="""You are the SECURITY role in the OSA Framework.

Your responsibilities:
- Zero Trust validation of all inputs
- Ensuring proper authentication/authorization
- Identifying security vulnerabilities
- Secret management and encryption

Approach: Verify everything. Sanitize all inputs.
Apply principle of least privilege. Consider OWASP Top 10.""",
        agent_preference="opencode"  # Schema validation, security per .osa/OSA.md
    ),

    "qa": RolePersona(
        name="QA",
        keywords=["test", "verify", "check", "validate", "debug", "edge case", "coverage", "benchmark", "inspect"],
        system_prompt="""You are the QA role in the OSA Framework.

Your responsibilities:
- Verification of completed work
- Testing and edge-case analysis
- Quality assurance and validation
- Finding bugs and issues

Approach: Be thorough and methodical.
Test edge cases. Verify assumptions. Document any issues found.""",
        agent_preference="claude"
    ),
}


# ============================================================================
# PARALLEL EXECUTION SYSTEM - SWARM PATTERN
# ============================================================================

@dataclass
class Task:
    """Represents a task with its metadata."""
    description: str
    completed: bool = False
    dependencies: Set[str] = field(default_factory=set)
    index: int = 0


@dataclass
class TaskResult:
    """Result of a task execution."""
    task: Task
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    role_used: str = ""
    agent_used: str = ""


class ParallelExecutor:
    """
    Executes tasks in parallel using ThreadPoolExecutor.

    Implements the swarm pattern from .osa/OSA.md:
    - Detects independent tasks that can run in parallel
    - Uses ThreadPoolExecutor for concurrent agent execution
    - Respects task dependencies
    - Thread-safe plan file updates
    """

    def __init__(self, max_workers: int = 3):
        """
        Initialize the parallel executor.

        Args:
            max_workers: Maximum number of concurrent agent tasks
        """
        self.max_workers = max_workers
        self.plan_lock = threading.Lock()  # For thread-safe file updates

    def parse_plan_tasks(self, plan_content: str) -> List[Task]:
        """
        Parse tasks from plan file content.

        Args:
            plan_content: The markdown plan content

        Returns:
            List of Task objects with dependencies
        """
        tasks = []
        lines = plan_content.split('\n')

        for idx, line in enumerate(lines):
            # Match "- [ ] Task description" or "- [x] Task description"
            match = re.match(r'^-\s*\[([ x])\]\s*(.+)', line)
            if match:
                status_char, description = match.groups()
                is_completed = status_char == 'x'

                task = Task(
                    description=description.strip(),
                    completed=is_completed,
                    index=idx
                )

                # Detect dependencies based on keywords
                task.dependencies = self._detect_dependencies(description, idx)

                if not is_completed:
                    tasks.append(task)

        return tasks

    def _detect_dependencies(self, task_description: str, task_index: int) -> Set[str]:
        """
        Detect if a task depends on previous tasks based on keywords.

        Args:
            task_description: The task text to analyze
            task_index: The task's position in the list

        Returns:
            Set of dependency indicators (empty for independent tasks)
        """
        desc_lower = task_description.lower()

        # Keywords indicating dependency on previous tasks
        dependency_keywords = [
            "after", "once", "when", "then", "next",
            "following", "based on", "using previous",
            "update", "modify", "extend", "refactor"
        ]

        # If description contains dependency keywords, mark as dependent
        for kw in dependency_keywords:
            if kw in desc_lower:
                return {"previous"}

        # Tasks starting with numbers implicitly depend on prior numbered steps
        if re.match(r'^\d+\.', task_description):
            return {"sequential"}

        return set()

    def find_executable_batch(self, tasks: List[Task], completed: Set[str]) -> List[Task]:
        """
        Find tasks that can be executed in parallel (no unmet dependencies).

        Args:
            tasks: List of pending tasks
            completed: Set of completed task descriptions

        Returns:
            List of tasks ready to execute
        """
        executable = []

        for task in tasks:
            # Check if all dependencies are satisfied
            can_execute = True

            if "previous" in task.dependencies or "sequential" in task.dependencies:
                # These tasks need at least one prior task completed
                if not completed:
                    can_execute = False

            if can_execute:
                executable.append(task)

        return executable

    def execute_task_parallel(
        self,
        task: Task,
        goal: str,
        plan_file: str,
        plan_content: str,
        default_agent: str,
        use_tts: bool = False
    ) -> TaskResult:
        """
        Execute a single task (meant to be run in a thread).

        Args:
            task: The task to execute
            goal: Overall goal
            plan_file: Path to plan file
            plan_content: Current plan content
            default_agent: Default agent to use
            use_tts: Whether TTS is enabled

        Returns:
            TaskResult with execution outcome
        """
        detected_role = detect_role(task.description)
        role_agent = get_agent_for_role(detected_role, default_agent)

        print(f"   🧵 [Thread-{threading.current_thread().name}] {task.description[:50]}...")
        print(f"      🎭 Role: {detected_role.value.upper()} | 🤖 Agent: {role_agent}")

        worker_prompt = build_role_based_prompt(
            role=detected_role,
            task=task.description,
            goal=goal,
            plan_content=plan_content,
            plan_file=plan_file
        )

        try:
            output = run_agent(role_agent, worker_prompt, verbose=False)

            success = output is not None

            # Thread-safe plan update
            if success:
                self._mark_task_completed(task.description, plan_file)

            return TaskResult(
                task=task,
                success=success,
                output=output,
                role_used=detected_role,
                agent_used=role_agent
            )

        except Exception as e:
            return TaskResult(
                task=task,
                success=False,
                error=str(e),
                role_used=detected_role,
                agent_used=role_agent
            )

    def _mark_task_completed(self, task_description: str, plan_file: str):
        """
        Thread-safe update of plan file to mark task as complete.

        Args:
            task_description: The task to mark complete
            plan_file: Path to plan file
        """
        with self.plan_lock:
            try:
                with open(plan_file, 'r') as f:
                    content = f.read()

                # Escape special regex characters in task description
                escaped_desc = re.escape(task_description)

                # Replace "- [ ] task" with "- [x] task"
                new_content = re.sub(
                    rf'- \[ \]\s*{escaped_desc}',
                    f'- [x] {task_description}',
                    content
                )

                if new_content != content:
                    with open(plan_file, 'w') as f:
                        f.write(new_content)
                    print(f"      ✅ Marked complete: {task_description[:40]}...")

            except Exception as e:
                print(f"      ⚠️ Failed to update plan: {e}")

    def execute_plan_parallel(
        self,
        plan_content: str,
        goal: str,
        plan_file: str,
        default_agent: str,
        use_tts: bool = False
    ) -> List[TaskResult]:
        """
        Execute all pending tasks with parallelization where possible.

        Args:
            plan_content: Current plan file content
            goal: Overall goal
            plan_file: Path to plan file
            default_agent: Default agent from CLI
            use_tts: Whether TTS is enabled

        Returns:
            List of TaskResult objects
        """
        tasks = self.parse_plan_tasks(plan_content)

        if not tasks:
            print("✅ No pending tasks to execute.")
            return []

        print(f"\n🔄 PARALLEL EXECUTION MODE")
        print(f"   Pending tasks: {len(tasks)}")
        print(f"   Max workers: {self.max_workers}")
        print(f"   Strategy: Execute independent tasks concurrently")

        all_results = []
        completed_tasks = set()

        while tasks:
            # Find tasks that can run in parallel
            executable_batch = self.find_executable_batch(tasks, completed_tasks)

            if not executable_batch:
                # No tasks can execute (likely dependency deadlock)
                print("⚠️ No executable tasks found. Possible dependency deadlock.")
                break

            # Limit batch size to max_workers
            batch = executable_batch[:self.max_workers]

            print(f"\n⚡ Executing batch of {len(batch)} task(s) in parallel...")

            # Execute batch in parallel
            with ThreadPoolExecutor(max_workers=len(batch)) as executor:
                futures = {
                    executor.submit(
                        self.execute_task_parallel,
                        task, goal, plan_file, plan_content, default_agent, use_tts
                    ): task
                    for task in batch
                }

                for future in as_completed(futures):
                    result = future.result()
                    all_results.append(result)

                    if result.success:
                        completed_tasks.add(result.task.description)

            # Remove completed tasks from pending list
            tasks = [t for t in tasks if t.description not in completed_tasks]

            # Reload plan content for next batch
            if tasks:
                try:
                    with open(plan_file, 'r') as f:
                        plan_content = f.read()
                except:
                    pass

        return all_results


def detect_role(task_description: str) -> str:
    """
    Detect the appropriate OSA role for a given task.

    Args:
        task_description: The task text to analyze

    Returns:
        The role name (one of: orchestrator, architect, coder, security, qa)
    """
    task_lower = task_description.lower()

    # Count keyword matches for each role
    role_scores = {}
    for role_name, role in OSA_ROLES.items():
        score = sum(1 for kw in role.keywords if kw in task_lower)
        if score > 0:
            role_scores[role_name] = score

    # Return role with highest score, or default to 'coder'
    if role_scores:
        return max(role_scores, key=role_scores.get)

    # Default fallback for generic tasks
    return "coder"


def get_agent_for_role(role: str, default_agent: str) -> str:
    """
    Get the preferred agent for a given role.

    Args:
        role: The OSA role name
        default_agent: The default agent from command line

    Returns:
        The agent name to use
    """
    role_obj = OSA_ROLES.get(role)
    if role_obj and role_obj.agent_preference:
        return role_obj.agent_preference
    return default_agent


def build_role_based_prompt(role: str, task: str, goal: str, plan_content: str, plan_file: str) -> str:
    """
    Build a specialized prompt based on the detected role.

    Args:
        role: The OSA role name
        task: The current task description
        goal: The overall goal
        plan_content: Current plan file content
        plan_file: Path to the plan file

    Returns:
        A specialized prompt for the role
    """
    role_obj = OSA_ROLES.get(role, OSA_ROLES["coder"])

    prompt = f"""# OSA Framework - {role_obj.name.upper()} Role

{role_obj.system_prompt}

## Context
Overall Goal: {goal}

## Current Plan Status
```
{plan_content[:2000]}  # Truncate to avoid token overflow
```

## YOUR CURRENT TASK
{task}

## Instructions
1. Execute this task using your {role_obj.name} expertise
2. Follow the {role_obj.name} guidelines specified above
3. Do NOT edit '{plan_file}' unless the task explicitly requires updating it.
4. Do NOT mark tasks as complete in '{plan_file}'. The orchestrator will verify and mark completion.
5. If you make code changes, ensure they are verified by the project's verification commands (tests/lints/build).
6. Do NOT ask for permission. Make reasonable assumptions if needed.

## Reference
See .claude/OSA_FRAMEWORK.md for OSA Framework details.
"""

    return prompt


def _slice_section(markdown: str, header_pattern: str) -> str:
    lines = markdown.splitlines()
    header_re = re.compile(header_pattern, re.IGNORECASE)
    start_idx = None
    for i, line in enumerate(lines):
        if header_re.match(line.strip()):
            start_idx = i + 1
            break
    if start_idx is None:
        return ""
    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        if re.match(r"^\s*#{1,6}\s+\S+", lines[j]):
            end_idx = j
            break
    return "\n".join(lines[start_idx:end_idx]).strip()


def _extract_bash_code_fences(markdown: str) -> List[str]:
    cmds: List[str] = []
    in_fence = False
    fence_lang = ""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
            else:
                in_fence = False
                fence_lang = ""
            continue
        if in_fence and (fence_lang in ("", "bash", "sh", "shell", "zsh", "fish")):
            if stripped:
                cmds.append(stripped)
    return cmds


def _extract_inline_command_bullets(markdown: str) -> List[str]:
    cmds: List[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith(("-", "*")):
            continue
        m = re.search(r"(verify|verification|run)\s*:\s*`([^`]+)`", stripped, re.IGNORECASE)
        if m:
            cmds.append(m.group(2).strip())
            continue
        m = re.search(r"(verify|verification|run)\s*:\s*(.+)$", stripped, re.IGNORECASE)
        if m:
            candidate = m.group(2).strip()
            if candidate.startswith("`") and candidate.endswith("`") and len(candidate) >= 2:
                candidate = candidate[1:-1].strip()
            if candidate:
                cmds.append(candidate)
    return cmds


def _is_safe_verification_command(cmd: str) -> bool:
    forbidden = [";", "|", "&", ">", "<", "\n", "\r"]
    if any(ch in cmd for ch in forbidden):
        return False
    lowered = cmd.strip().lower()
    if not lowered:
        return False
    if lowered.startswith(("sudo ", "rm ", "rm\t", "chmod ", "chown ", "curl ", "wget ")):
        return False
    if " -c " in f" {lowered} " and lowered.startswith(("bash", "sh", "zsh")):
        return False
    return True


def _normalize_commands(cmds: List[str]) -> List[str]:
    normalized: List[str] = []
    seen: Set[str] = set()
    for cmd in cmds:
        c = cmd.strip()
        if not c:
            continue
        if not _is_safe_verification_command(c):
            continue
        if c not in seen:
            normalized.append(c)
            seen.add(c)
    return normalized


def extract_verification_commands(plan_content: str) -> List[str]:
    acceptance = _slice_section(plan_content, r"^\s*#{1,6}\s+Acceptance\s*$")
    if not acceptance:
        acceptance = _slice_section(plan_content, r"^\s*#{1,6}\s+Acceptance\s+Criteria\s*$")
    if not acceptance:
        return []
    cmds = []
    cmds.extend(_extract_bash_code_fences(acceptance))
    cmds.extend(_extract_inline_command_bullets(acceptance))
    return _normalize_commands(cmds)


def detect_default_verification_commands(repo_root: str) -> List[str]:
    root = Path(repo_root)
    cmds: List[str] = []
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        if (root / "tests").exists():
            cmds.append("python -m pytest -q")
            cmds.append("python -m unittest discover -q")
        cmds.append("python -m compileall yolo_mode")
    if (root / "package.json").exists():
        cmds.append("npm test")
    if (root / "go.mod").exists():
        cmds.append("go test ./...")
    if (root / "Cargo.toml").exists():
        cmds.append("cargo test")
    return _normalize_commands(cmds)


def _command_is_runnable(cmd: str) -> bool:
    try:
        parts = shlex.split(cmd)
    except ValueError:
        return False
    if not parts:
        return False
    exe = parts[0]
    return shutil.which(exe) is not None


def run_verification(commands: List[str], timeout_s: int = 900) -> Tuple[bool, str]:
    runnable = [c for c in commands if _command_is_runnable(c)]
    if not runnable:
        return False, "No runnable verification command found (Acceptance section missing or tools not on PATH)."
    last_output = ""
    for cmd in runnable:
        try:
            parts = shlex.split(cmd)
            result = subprocess.run(parts, capture_output=True, text=True, timeout=timeout_s)
            last_output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
            if result.returncode != 0:
                tail = "\n".join(last_output.splitlines()[-50:])
                return False, f"Verification failed: `{cmd}`\n{tail}".strip()
        except subprocess.TimeoutExpired:
            return False, f"Verification timed out after {timeout_s}s: `{cmd}`"
        except Exception as e:
            return False, f"Verification error for `{cmd}`: {e}"
    return True, f"Verification passed: {', '.join(f'`{c}`' for c in runnable)}"


def _git_available() -> bool:
    return shutil.which("git") is not None


def _run_git(args: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _git_porcelain(cwd: str) -> Optional[str]:
    res = _run_git(["status", "--porcelain"], cwd=cwd)
    if res.returncode != 0:
        return None
    return res.stdout.strip()


def _git_head(cwd: str) -> Optional[str]:
    res = _run_git(["rev-parse", "HEAD"], cwd=cwd)
    if res.returncode != 0:
        return None
    return res.stdout.strip()


def _git_untracked(cwd: str) -> Set[str]:
    res = _run_git(["ls-files", "--others", "--exclude-standard"], cwd=cwd)
    if res.returncode != 0:
        return set()
    paths = set()
    for line in res.stdout.splitlines():
        p = line.strip()
        if p:
            paths.add(p)
    return paths


def _safe_remove_paths(repo_root: str, rel_paths: Set[str]) -> None:
    root = Path(repo_root).resolve()
    for rel in rel_paths:
        if rel.startswith(("/", "\\")) or ".." in Path(rel).parts:
            continue
        target = (root / rel).resolve()
        if root not in target.parents and target != root:
            continue
        if target.is_file() or target.is_symlink():
            try:
                target.unlink()
            except Exception:
                pass
        elif target.is_dir():
            try:
                shutil.rmtree(target)
            except Exception:
                pass


def snapshot_repo_state(repo_root: str) -> Optional[Dict[str, object]]:
    if not _git_available():
        return None
    if not (Path(repo_root) / ".git").exists():
        return None
    porcelain = _git_porcelain(repo_root)
    head = _git_head(repo_root)
    if porcelain is None or head is None:
        return None
    if porcelain:
        return None
    return {
        "head": head,
        "untracked": _git_untracked(repo_root),
        "porcelain": porcelain,
    }


def rollback_repo_state(repo_root: str, snapshot: Dict[str, object]) -> bool:
    head = snapshot.get("head")
    if not isinstance(head, str) or not head:
        return False
    res = _run_git(["reset", "--hard", head], cwd=repo_root)
    if res.returncode != 0:
        return False
    before_untracked = snapshot.get("untracked", set())
    if isinstance(before_untracked, set):
        after_untracked = _git_untracked(repo_root)
        new_untracked = after_untracked - before_untracked
        _safe_remove_paths(repo_root, new_untracked)
    porcelain_after = _git_porcelain(repo_root)
    return porcelain_after == ""


def mark_task_completed(plan_file: str, task_description: str) -> bool:
    try:
        with open(plan_file, "r") as f:
            content = f.read()
        escaped_desc = re.escape(task_description)
        new_content = re.sub(
            rf"-\s*\[\s*\]\s*{escaped_desc}",
            f"- [x] {task_description}",
            content,
            count=1,
        )
        if new_content == content:
            return False
        with open(plan_file, "w") as f:
            f.write(new_content)
        return True
    except Exception:
        return False


def speak(text, enabled=False):
    """Speaks the text using a configurable TTS command if enabled, with a BLOCKING pause to prevent overlap."""
    if enabled:
        try:
            tts_command = os.environ.get("YOLO_TTS_COMMAND", "tts-cli").strip() or "tts-cli"
            # Shorten very long texts for TTS
            if len(text) > 100:
                text = text[:97] + "..."

            subprocess.run(
                [tts_command, "--text", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            # Add a small buffer after the command finishes to separate thoughts
            time.sleep(0.5)
        except Exception as e:
            # Silently fail or log to stderr if absolutely needed, but keep main output clean
            pass

def run_agent_legacy(agent, prompt, verbose=False):
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
    elif agent == "mini":
        # Mini-SWE-Agent - always runs in autonomous mode
        cmd = ["mini", prompt]
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

def run_agent(agent, prompt, verbose=False):
    if NEW_AGENTS_AVAILABLE:
        return run_agent_new(agent, prompt, verbose=verbose)
    return run_agent_legacy(agent, prompt, verbose=verbose)

def clean_text_for_tts(text):
    """Removes markdown and other noise for clearer speech."""
    return text.replace('`', '').replace('*', '').replace('#', '').strip()

def main():
    parser = argparse.ArgumentParser(description="YOLO Mode Loop")
    parser.add_argument("prompt", nargs="+", help="The main goal/prompt")
    parser.add_argument("--tts", action="store_true", help="Enable TTS output (default command: tts-cli; override with YOLO_TTS_COMMAND)")
    parser.add_argument("--agent", default="claude", help="The CLI agent to use (claude, opencode, gemini, qwen, crush, mini, etc.)")
    parser.add_argument("--contract-mode", choices=["urgent", "economical", "balanced"], default="balanced",
                        help="Contract mode for resource management (default: balanced)")
    args = parser.parse_args()

    goal = " ".join(args.prompt)
    use_tts = args.tts
    agent = args.agent
    contract_mode_str = args.contract_mode
    plan_file = "YOLO_PLAN.md"

    # Create contract if new agents available
    contract = None
    resource_selector = None
    if NEW_AGENTS_AVAILABLE:
        # Use lowercase string value for ContractMode (enum values are lowercase)
        contract_mode = ContractMode(contract_mode_str.lower())
        contract = ContractFactory.default(mode=contract_mode)
        contract.activate()
        resource_selector = ResourceAwareSelector(contract)
        print(f"🚀 Starting YOLO Mode | Contract: {contract_mode_str.upper()} | Default Agent: {agent}")
    else:
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
            
            The file format MUST include:
            - An Acceptance section with completion criteria and verification commands
            - A Todo section with checklist items in this exact format:
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
            repo_root = os.getcwd()
            verification_cmds = extract_verification_commands(plan_content)
            if not verification_cmds:
                verification_cmds = detect_default_verification_commands(repo_root)

            # ============================================================================
            # ROLE-BASED TASK ROUTING (OSA Framework)
            # ============================================================================

            # Check contract status if available
            if contract:
                can_proceed, reason = contract.can_proceed()
                if not can_proceed:
                    print(f"🛑 Contract violation: {reason}")
                    if use_tts:
                        speak(f"Contract violation: {reason}", True)
                    break

            # Detect appropriate role for this task based on keywords
            if NEW_AGENTS_AVAILABLE:
                detected_role, role_agent = detect_role_and_agent(current_task, [agent])
                reasoning = f"Role: {detected_role.value}"

                # Apply resource-aware selection if contract is active
                if resource_selector and contract:
                    role_agent, selector_reasoning = resource_selector.select_agent(current_task, [agent], detected_role)
                    reasoning = selector_reasoning

                print(f"🔨 Executing Task: {current_task}")
                print(f"   🎭 Detected Role: {detected_role.value.upper()}")
                if role_agent != agent:
                    print(f"   🤖 Agent: {role_agent}")
                print(f"   📊 {reasoning}")

                # Build contract-aware prompt
                base_prompt = build_role_based_prompt(
                    role=detected_role,
                    task=current_task,
                    goal=goal,
                    plan_content=plan_content,
                    plan_file=plan_file
                )
                worker_prompt = build_contract_aware_prompt(base_prompt, role_agent, contract)
            else:
                # Legacy behavior
                detected_role = detect_role(current_task)
                role_agent = get_agent_for_role(detected_role, agent)

                print(f"🔨 Executing Task: {current_task}")
                print(f"   🎭 Detected Role: {detected_role.value.upper()}")
                if role_agent != agent:
                    print(f"   🤖 Agent Selection: {role_agent} (role-preferred)")

                worker_prompt = build_role_based_prompt(
                    role=detected_role,
                    task=current_task,
                    goal=goal,
                    plan_content=plan_content,
                    plan_file=plan_file
                )

            if use_tts:
                clean_task = clean_text_for_tts(current_task)
                speak(f"Executing: {clean_task}", True)

            allow_plan_edits = "YOLO_PLAN.md" in current_task or "yolo_plan.md" in current_task
            max_attempts_per_task = 3
            task_completed = False
            failure_summary = ""

            for attempt in range(1, max_attempts_per_task + 1):
                if contract:
                    can_proceed, reason = contract.can_proceed()
                    if not can_proceed:
                        print(f"🛑 Contract constraint: {reason}")
                        if use_tts:
                            speak(f"Contract constraint reached: {reason}", True)
                        break

                if attempt > 1:
                    print(f"   🔁 Retry {attempt}/{max_attempts_per_task}")

                snapshot = snapshot_repo_state(repo_root)
                if snapshot is None and _git_available() and (Path(repo_root) / ".git").exists():
                    porcelain = _git_porcelain(repo_root)
                    if porcelain:
                        print("   ⚠️ Repo is dirty; rollback-on-failure disabled for this attempt.")

                attempt_prompt = worker_prompt
                if attempt > 1 and failure_summary:
                    attempt_prompt = (
                        worker_prompt
                        + "\n\n## Previous Attempt Failure\n"
                        + failure_summary
                        + "\n\nFix the issue, keep changes minimal, and ensure verification passes."
                    )

                output = run_agent(role_agent, attempt_prompt, verbose=True)

                if contract and output:
                    estimated_tokens = len(str(output)) // 4
                    contract.consume_resource(ResourceDimension.TOKENS, estimated_tokens)
                    contract.consume_resource(ResourceDimension.ITERATIONS, 1)

                    status = contract.get_status()
                    max_util = status["max_utilization"]
                    if max_util > 0.8:
                        print(f"   📊 High utilization: {max_util*100:.0f}%")
                        if use_tts:
                            speak(f"Resource usage at {max_util*100:.0f} percent", True)

                if output is None:
                    failure_summary = "Agent execution failed (no output)."
                    print(f"   ❌ {failure_summary}")
                    if snapshot:
                        rollback_repo_state(repo_root, snapshot)
                    continue

                if not allow_plan_edits:
                    try:
                        with open(plan_file, "r") as f:
                            plan_after = f.read()
                        if plan_after != plan_content:
                            with open(plan_file, "w") as f:
                                f.write(plan_content)
                    except Exception:
                        pass

                ok, verify_summary = run_verification(verification_cmds, timeout_s=900)
                if ok:
                    if mark_task_completed(plan_file, current_task):
                        print(f"   ✅ Verified + marked complete: {current_task}")
                    else:
                        print("   ⚠️ Verification passed but task could not be marked complete in the plan.")
                    if use_tts:
                        speak(f"Completed: {clean_task}", True)
                    task_completed = True
                    break

                failure_summary = verify_summary
                print(f"   ❌ {verify_summary}")
                if snapshot:
                    rolled_back = rollback_repo_state(repo_root, snapshot)
                    if not rolled_back:
                        print("   ⚠️ Rollback attempted but repo state could not be fully restored.")
                time.sleep(1)

            if not task_completed:
                print("🛑 Task failed verification after retries; leaving it pending.")
                if use_tts:
                    speak("Task failed verification and remains pending.", True)
                break

            time.sleep(1)

        if iteration >= max_iterations:
            print("🛑 Max iterations reached. Stopping.")
            if use_tts:
                speak("Maximum iterations reached. Stopping.", True)
        
        # Interactive Feedback Loop
        print("\n--- Mission Complete ---")

        # Print final contract status
        if contract:
            status = contract.get_status()
            print(f"\n📊 Contract Status Report:")
            print(f"   State: {status['state'].upper()}")
            print(f"   Max Utilization: {status['max_utilization']*100:.1f}%")
            print(f"   Time Remaining: {status['time_remaining']:.0f}s")
            for resource, consumed in status['consumption'].items():
                budget = status['budgets'].get(resource, float('inf'))
                if budget != float('inf'):
                    util = status['utilization'].get(resource, 0)
                    print(f"   {resource.upper()}: {consumed:.0f}/{budget:.0f} ({util*100:.1f}%)")

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
