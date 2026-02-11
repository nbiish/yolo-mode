"""
Manager Agent - OSA Orchestrator with 16-action space.

Based on: "Orchestrating Human-AI Teams: The Manager Agent
as a Unifying Research Challenge" (ACM DAI 2025)

Implements comprehensive workflow orchestration capabilities for autonomous
multi-agent systems with formal action space.
"""

import json
import os
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import OSA components
from .registry import AGENT_REGISTRY, OSARole, AgentConfig, get_agent_for_role


# ============================================================================
# MANAGER AGENT ACTION SPACE (16 actions from ACM DAI 2025)
# ============================================================================

class ManagerAction(Enum):
    """16 Manager Agent actions from ACM DAI 2025."""

    # Core workflow actions
    ASSIGN_TASK = "assign_task"
    CREATE_TASK = "create_task"
    REMOVE_TASK = "remove_task"
    SEND_MESSAGE = "send_message"

    # Information gathering
    NOOP = "noop"
    GET_WORKFLOW_STATUS = "get_workflow_status"
    GET_AVAILABLE_AGENTS = "get_available_agents"
    GET_PENDING_TASKS = "get_pending_tasks"

    # Task management
    REFINE_TASK = "refine_task"
    ADD_DEPENDENCY = "add_task_dependency"
    REMOVE_DEPENDENCY = "remove_task_dependency"
    INSPECT_TASK = "inspect_task"
    DECOMPOSE_TASK = "decompose_task"

    # Termination
    REQUEST_END = "request_end_workflow"
    FAILED_ACTION = "failed_action"
    ASSIGN_ALL = "assign_all_pending"


# ============================================================================
# WORKFLOW STATE REPRESENTATION
# ============================================================================

@dataclass
class Task:
    """Represents a task in the workflow."""
    id: str
    name: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    est_duration: float = 1.0  # Estimated hours


@dataclass
class WorkflowState:
    """State snapshot for Manager Agent decisions."""
    tasks: Dict[str, Task] = field(default_factory=dict)
    agents: Dict[str, AgentConfig] = field(default_factory=lambda: AGENT_REGISTRY.copy())
    message_log: List[Dict] = field(default_factory=list)
    action_history: List[Dict] = field(default_factory=list)
    completed_count: int = 0
    failed_count: int = 0
    start_time: float = field(default_factory=time.time)


# ============================================================================
# MANAGER AGENT IMPLEMENTATION
# ============================================================================

class OSAManagerAgent:
    """
    OSA Orchestrator with full Manager Agent action space.

    Implements workflow management as defined in ACM DAI 2025.

    The Manager Agent can:
    - Route tasks to appropriate agents based on skills
    - Monitor workflow progress and health
    - Decompose complex tasks into subtasks
    - Manage dependencies between tasks
    - Coordinate multi-agent collaboration
    """

    def __init__(self, goal: str, state_file: Optional[str] = None):
        """
        Initialize Manager Agent.

        Args:
            goal: The overall mission goal
            state_file: Optional file to persist workflow state
        """
        self.goal = goal
        self.state_file = state_file or ".claude/manager-state.json"
        self.state = self._load_state()
        self.actions = self._define_actions()

    def _define_actions(self) -> Dict[ManagerAction, Callable]:
        """Define all 16 Manager Agent actions."""
        return {
            # Core workflow
            ManagerAction.ASSIGN_TASK: self._assign_task,
            ManagerAction.CREATE_TASK: self._create_task,
            ManagerAction.REMOVE_TASK: self._remove_task,
            ManagerAction.SEND_MESSAGE: self._send_message,

            # Info gathering
            ManagerAction.NOOP: self._noop,
            ManagerAction.GET_WORKFLOW_STATUS: self._get_workflow_status,
            ManagerAction.GET_AVAILABLE_AGENTS: self._get_available_agents,
            ManagerAction.GET_PENDING_TASKS: self._get_pending_tasks,

            # Task management
            ManagerAction.REFINE_TASK: self._refine_task,
            ManagerAction.ADD_DEPENDENCY: self._add_dependency,
            ManagerAction.REMOVE_DEPENDENCY: self._remove_dependency,
            ManagerAction.INSPECT_TASK: self._inspect_task,
            ManagerAction.DECOMPOSE_TASK: self._decompose_task,

            # Termination
            ManagerAction.REQUEST_END: self._request_end,
            ManagerAction.FAILED_ACTION: self._failed_action,
            ManagerAction.ASSIGN_ALL: self._assign_all,
        }

    # ========================================================================
    # CORE WORKFLOW ACTIONS
    # ========================================================================

    def _assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Route task to capacity/skill-matched agent.

        Args:
            task_id: ID of task to assign
            agent_id: ID of agent to assign to

        Returns:
            True if assignment successful
        """
        if task_id not in self.state.tasks:
            self._log_action(ManagerAction.ASSIGN_TASK, {"error": f"Task {task_id} not found"})
            return False

        if agent_id not in self.state.agents:
            self._log_action(ManagerAction.ASSIGN_TASK, {"error": f"Agent {agent_id} not available"})
            return False

        task = self.state.tasks[task_id]
        task.assigned_to = agent_id
        task.status = "in_progress"

        self._log_action(ManagerAction.ASSIGN_TASK, {
            "task_id": task_id,
            "agent_id": agent_id,
            "task_name": task.name
        })

        self._save_state()
        return True

    def _create_task(
        self,
        name: str,
        description: str,
        est_hrs: float = 1.0,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Add new work item to workflow.

        Args:
            name: Task name
            description: Task description
            est_hrs: Estimated duration in hours
            dependencies: Optional list of prerequisite task IDs

        Returns:
            ID of created task
        """
        task_id = f"task_{len(self.state.tasks) + 1}_{int(time.time())}"

        task = Task(
            id=task_id,
            name=name,
            description=description,
            status="pending",
            dependencies=dependencies or [],
            est_duration=est_hrs
        )

        self.state.tasks[task_id] = task

        self._log_action(ManagerAction.CREATE_TASK, {
            "task_id": task_id,
            "name": name,
            "description": description[:100]
        })

        self._save_state()
        return task_id

    def _remove_task(self, task_id: str) -> bool:
        """
        Prune out-of-scope/duplicate task.

        Args:
            task_id: ID of task to remove

        Returns:
            True if removal successful
        """
        if task_id not in self.state.tasks:
            return False

        task = self.state.tasks[task_id]

        # Remove from any dependent tasks
        for other_id, other_task in self.state.tasks.items():
            if task_id in other_task.dependencies:
                other_task.dependencies.remove(task_id)

        del self.state.tasks[task_id]

        self._log_action(ManagerAction.REMOVE_TASK, {
            "task_id": task_id,
            "name": task.name
        })

        self._save_state()
        return True

    def _send_message(self, content: str, receiver_id: Optional[str] = None) -> bool:
        """
        Coordinate, solicit tradeoffs between agents.

        Args:
            content: Message content
            receiver_id: Optional specific agent recipient

        Returns:
            True if message sent
        """
        message = {
            "content": content,
            "from": "manager",
            "to": receiver_id or "all",
            "timestamp": time.time()
        }

        self.state.message_log.append(message)

        self._log_action(ManagerAction.SEND_MESSAGE, {
            "content": content[:100],
            "to": receiver_id
        })

        self._save_state()
        return True

    # ========================================================================
    # INFORMATION GATHERING ACTIONS
    # ========================================================================

    def _noop(self) -> Dict:
        """Observe without changing state."""
        return {
            "action": "noop",
            "timestamp": time.time(),
            "state": "unchanged"
        }

    def _get_workflow_status(self) -> Dict:
        """
        Snapshot workflow health (task histogram, ready set).

        Returns:
            Dictionary with workflow statistics
        """
        status = {
            "total_tasks": len(self.state.tasks),
            "pending": sum(1 for t in self.state.tasks.values() if t.status == "pending"),
            "in_progress": sum(1 for t in self.state.tasks.values() if t.status == "in_progress"),
            "completed": sum(1 for t in self.state.tasks.values() if t.status == "completed"),
            "failed": sum(1 for t in self.state.tasks.values() if t.status == "failed"),
            "unassigned": sum(1 for t in self.state.tasks.values() if t.assigned_to is None),
            "completion_rate": self.state.completed_count / max(1, len(self.state.tasks)),
            "elapsed_time": time.time() - self.state.start_time
        }

        return status

    def _get_available_agents(self) -> Dict[str, Dict]:
        """
        Inspect idle/available agents with capabilities.

        Returns:
            Dictionary of agent configurations
        """
        agents_info = {}
        for agent_id, config in self.state.agents.items():
            agents_info[agent_id] = {
                "name": config.name,
                "capabilities": [c.value for c in config.capabilities],
                "osa_roles": [r.value for r in config.osa_roles],
                "priority": config.priority
            }

        return agents_info

    def _get_pending_tasks(self) -> List[Dict]:
        """
        Triage backlog with preview.

        Returns:
            List of pending task details
        """
        pending = []
        for task_id, task in self.state.tasks.items():
            if task.status == "pending":
                pending.append({
                    "id": task_id,
                    "name": task.name,
                    "description": task.description,
                    "dependencies": task.dependencies,
                    "est_duration": task.est_duration,
                    "can_start": all(
                        self.state.tasks.get(d, Task(id="", name="")).status == "completed"
                        for d in task.dependencies
                    )
                })

        # Sort by dependencies (tasks with fewer deps first)
        pending.sort(key=lambda t: len(t["dependencies"]))

        return pending

    # ========================================================================
    # TASK MANAGEMENT ACTIONS
    # ========================================================================

    def _refine_task(self, task_id: str, new_instructions: str) -> bool:
        """
        Tighten scope and clarity of task.

        Args:
            task_id: ID of task to refine
            new_instructions: New task instructions

        Returns:
            True if refinement successful
        """
        if task_id not in self.state.tasks:
            return False

        task = self.state.tasks[task_id]
        task.description = new_instructions

        self._log_action(ManagerAction.REFINE_TASK, {
            "task_id": task_id,
            "new_instructions": new_instructions[:100]
        })

        self._save_state()
        return True

    def _add_dependency(self, prereq_id: str, dep_id: str) -> bool:
        """
        Enforce sequencing between tasks.

        Args:
            prereq_id: Prerequisite task ID
            dep_id: Dependent task ID

        Returns:
            True if dependency added
        """
        if prereq_id not in self.state.tasks or dep_id not in self.state.tasks:
            return False

        if dep_id not in self.state.tasks[dep_id].dependencies:
            self.state.tasks[dep_id].dependencies.append(prereq_id)

        self._log_action(ManagerAction.ADD_DEPENDENCY, {
            "prereq": prereq_id,
            "dependent": dep_id
        })

        self._save_state()
        return True

    def _remove_dependency(self, prereq_id: str, dep_id: str) -> bool:
        """
        Remove obsolete dependency between tasks.

        Args:
            prereq_id: Prerequisite task ID
            dep_id: Dependent task ID

        Returns:
            True if dependency removed
        """
        if dep_id not in self.state.tasks:
            return False

        task = self.state.tasks[dep_id]
        if prereq_id in task.dependencies:
            task.dependencies.remove(prereq_id)

        self._log_action(ManagerAction.REMOVE_DEPENDENCY, {
            "prereq": prereq_id,
            "dependent": dep_id
        })

        self._save_state()
        return True

    def _inspect_task(self, task_id: str) -> Optional[Dict]:
        """
        Read-only deep dive into task details.

        Args:
            task_id: ID of task to inspect

        Returns:
            Detailed task information or None
        """
        if task_id not in self.state.tasks:
            return None

        task = self.state.tasks[task_id]

        # Get dependent info
        dependent_tasks = [
            tid for tid, t in self.state.tasks.items()
            if task_id in t.dependencies
        ]

        return {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "dependencies": task.dependencies,
            "dependents": dependent_tasks,
            "est_duration": task.est_duration,
            "created_at": task.created_at,
            "can_start": all(
                self.state.tasks.get(d, Task(id="", name="")).status == "completed"
                for d in task.dependencies
            )
        }

    def _decompose_task(self, task_id: str, max_subtasks: int = 4) -> List[str]:
        """
        Split complex task into subtasks using AI.

        Args:
            task_id: ID of task to decompose
            max_subtasks: Maximum number of subtasks to create

        Returns:
            List of new subtask IDs
        """
        if task_id not in self.state.tasks:
            return []

        parent_task = self.state.tasks[task_id]

        # Create subtasks based on parent description
        subtask_descriptions = self._generate_subtasks(parent_task.description, max_subtasks)

        subtask_ids = []
        for i, desc in enumerate(subtask_descriptions, 1):
            subtask_id = self._create_task(
                name=f"{parent_task.name} - Part {i}",
                description=desc,
                est_hrs=parent_task.est_duration / len(subtask_descriptions),
                dependencies=[task_id]
            )
            subtask_ids.append(subtask_id)

        # Update parent to depend on subtasks
        parent_task.dependencies = subtask_ids

        self._log_action(ManagerAction.DECOMPOSE_TASK, {
            "parent_id": task_id,
            "subtask_count": len(subtask_ids),
            "subtask_ids": subtask_ids
        })

        self._save_state()
        return subtask_ids

    def _generate_subtasks(self, description: str, max_count: int) -> List[str]:
        """
        Generate subtask descriptions from parent task.

        This is a simple heuristic-based decomposition.
        For production, this would use an LLM.
        """
        # Simple decomposition patterns
        subtasks = []

        # Research tasks
        if any(word in description.lower() for word in ["research", "investigate", "analyze", "study"]):
            subtasks = [
                f"Gather requirements for: {description[:50]}",
                f"Identify key sources for: {description[:50]}",
                f"Synthesize findings for: {description[:50]}"
            ]

        # Implementation tasks
        elif any(word in description.lower() for word in ["implement", "create", "build", "add"]):
            subtasks = [
                f"Design structure for: {description[:50]}",
                f"Implement core functionality: {description[:50]}",
                f"Add error handling: {description[:50]}",
                f"Test implementation: {description[:50]}"
            ]

        # Default generic decomposition
        else:
            words = description.split()
            chunks = [words[i:i+3] for i in range(0, len(words), 3)]
            subtasks = [f"Subtask: {' '.join(chunk)[:100]}" for chunk in chunks[:max_count]]

        return subtasks[:max_count]

    # ========================================================================
    # TERMINATION ACTIONS
    # ========================================================================

    def _request_end(self, reason: str) -> bool:
        """
        Signal workflow termination.

        Args:
            reason: Reason for ending workflow

        Returns:
            True if termination signal sent
        """
        self._log_action(ManagerAction.REQUEST_END, {
            "reason": reason,
            "timestamp": time.time(),
            "completed": self.state.completed_count,
            "failed": self.state.failed_count
        })

        # Mark all pending tasks as cancelled
        for task in self.state.tasks.values():
            if task.status == "pending":
                task.status = "cancelled"

        self._save_state()
        return True

    def _failed_action(self, action: ManagerAction, metadata: Dict) -> bool:
        """
        Record provider/system failure.

        Args:
            action: The action that failed
            metadata: Failure details

        Returns:
            True if failure logged
        """
        self.state.failed_count += 1

        self._log_action(ManagerAction.FAILED_ACTION, {
            "failed_action": action.value,
            "metadata": metadata,
            "timestamp": time.time()
        })

        self._save_state()
        return True

    def _assign_all(self, agent_ids: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Fast triage for demos - assign all pending tasks.

        Args:
            agent_ids: Optional list of agents to use (default: all available)

        Returns:
            Dictionary mapping agent_id to list of task_ids
        """
        available_agents = agent_ids or list(self.state.agents.keys())
        pending_tasks = self._get_pending_tasks()

        assignment = {agent_id: [] for agent_id in available_agents}

        for i, task_info in enumerate(pending_tasks):
            if not task_info["can_start"]:
                continue

            # Round-robin assignment
            agent_id = available_agents[i % len(available_agents)]
            assignment[agent_id].append(task_info["id"])
            self._assign_task(task_info["id"], agent_id)

        self._log_action(ManagerAction.ASSIGN_ALL, {
            "assigned_count": sum(len(tasks) for tasks in assignment.values()),
            "assignment": {k: len(v) for k, v in assignment.items()}
        })

        return assignment

    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================

    def _load_state(self) -> WorkflowState:
        """Load workflow state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)

                # Reconstruct Task objects from dict
                tasks = {}
                for tid, tdict in data.get("tasks", {}).items():
                    tasks[tid] = Task(**tdict)

                return WorkflowState(
                    tasks=tasks,
                    agents=data.get("agents", AGENT_REGISTRY.copy()),
                    message_log=data.get("message_log", []),
                    action_history=data.get("action_history", []),
                    completed_count=data.get("completed_count", 0),
                    failed_count=data.get("failed_count", 0),
                    start_time=data.get("start_time", time.time())
                )
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")

        return WorkflowState()

    def _save_state(self):
        """Persist workflow state to file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.state_file)), exist_ok=True)

        data = {
            "tasks": {
                tid: {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "status": t.status,
                    "assigned_to": t.assigned_to,
                    "dependencies": t.dependencies,
                    "created_at": t.created_at,
                    "est_duration": t.est_duration
                }
                for tid, t in self.state.tasks.items()
            },
            "agents": {aid: {
                "name": a.name,
                "cli_command": a.cli_command,
                "yolo_flag": a.yolo_flag
            } for aid, a in self.state.agents.items()},
            "message_log": self.state.message_log,
            "action_history": self.state.action_history,
            "completed_count": self.state.completed_count,
            "failed_count": self.state.failed_count,
            "start_time": self.state.start_time
        }

        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_action(self, action: ManagerAction, details: Dict):
        """Log action to history."""
        log_entry = {
            "action": action.value,
            "timestamp": time.time(),
            "details": details
        }
        self.state.action_history.append(log_entry)

        # Keep history manageable
        if len(self.state.action_history) > 1000:
            self.state.action_history = self.state.action_history[-500:]

    def _is_complete(self) -> bool:
        """Check if workflow is complete."""
        # Complete if no pending tasks and no in-progress tasks
        pending = sum(1 for t in self.state.tasks.values() if t.status in ["pending", "in_progress"])
        return pending == 0

    def _finalize_workflow(self) -> bool:
        """Finalize workflow and return completion status."""
        self._save_state()
        return True

    # ========================================================================
    # PUBLIC ORCHESTRATION API
    # ========================================================================

    def orchestrate(self, max_actions: int = 100) -> bool:
        """
        Main orchestration loop.

        Args:
            max_actions: Maximum actions to take before stopping

        Returns:
            True if workflow completed successfully
        """
        print(f"\n🎼 OSA Manager Agent starting orchestration")
        print(f"   Goal: {self.goal[:80]}...")
        print(f"   State file: {self.state_file}")
        print(f"   Available agents: {', '.join(self.state.agents.keys())}")

        actions_taken = 0

        while not self._is_complete() and actions_taken < max_actions:
            # Get current status
            status = self.actions[ManagerAction.GET_WORKFLOW_STATUS]()

            # Select appropriate action (in production, this would use an LLM)
            action = self._select_action(status)

            # Execute action
            print(f"\n🎬 Action {actions_taken + 1}: {action.value}")
            result = self.actions[action](status)

            actions_taken += 1

            # Brief pause between actions
            time.sleep(0.1)

        print(f"\n✅ Orchestration complete")
        print(f"   Actions taken: {actions_taken}")
        print(f"   Tasks completed: {status['completed']}")
        print(f"   Tasks failed: {status['failed']}")

        return self._finalize_workflow()

    def _select_action(self, status: Dict) -> ManagerAction:
        """
        Select next action based on current state.

        In production, this would use an LLM to select actions.
        For now, use simple heuristics.
        """
        pending_count = status["pending"]

        if pending_count > 0:
            # Have pending tasks - assign them
            ready_tasks = [t for t in self.state.tasks.values()
                          if t.status == "pending" and
                          all(self.state.tasks.get(d, Task(id="", name="")).status == "completed"
                              for d in t.dependencies)]

            if ready_tasks:
                # Assign a ready task
                task = ready_tasks[0]

                # Select appropriate agent based on task content
                agent_id = self._select_agent_for_task(task)
                return ManagerAction.ASSIGN_TASK

        return ManagerAction.GET_WORKFLOW_STATUS

    def _select_agent_for_task(self, task: Task) -> str:
        """Select appropriate agent for a task based on content."""
        desc_lower = task.description.lower()

        # Use role detection from registry
        from .role_detection import detect_role
        role = detect_role(task.description)
        return get_agent_for_role(role, list(self.state.agents.keys()))


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_manager(goal: str, state_file: Optional[str] = None) -> OSAManagerAgent:
    """
    Factory function to create Manager Agent instance.

    Args:
        goal: The overall mission goal
        state_file: Optional state file path

    Returns:
        Configured Manager Agent instance
    """
    return OSAManagerAgent(goal=goal, state_file=state_file)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Demo: Create manager and orchestrate a simple workflow
    print("=== OSA Manager Agent Demo ===\n")

    manager = create_manager(
        goal="Demonstrate Manager Agent capabilities",
        state_file=".claude/demo-manager-state.json"
    )

    # Create some example tasks
    task1 = manager._create_task(
        name="Research CLI agents",
        description="Research Qwen, Gemini, and Crush CLI tools for integration",
        est_hrs=2.0
    )

    task2 = manager._create_task(
        name="Implement agent registry",
        description="Create unified registry for all CLI agents",
        est_hrs=3.0,
        dependencies=[task1]
    )

    task3 = manager._create_task(
        name="Write documentation",
        description="Document the integration process",
        est_hrs=1.0,
        dependencies=[task2]
    )

    # Show workflow status
    status = manager.actions[ManagerAction.GET_WORKFLOW_STATUS]()
    print(f"\n📊 Initial Status:")
    print(f"   Total tasks: {status['total_tasks']}")
    print(f"   Pending: {status['pending']}")
    print(f"   In progress: {status['in_progress']}")

    # Show available agents
    agents = manager.actions[ManagerAction.GET_AVAILABLE_AGENTS]()
    print(f"\n🤖 Available Agents:")
    for agent_id, info in agents.items():
        print(f"   {agent_id}: {info['name']}")
        print(f"      Capabilities: {', '.join(info['capabilities'][:3])}...")

    # Show pending tasks
    pending = manager.actions[ManagerAction.GET_PENDING_TASKS]()
    print(f"\n📋 Pending Tasks:")
    for task in pending:
        ready = "✓" if task["can_start"] else "✗"
        print(f"   [{ready}] {task['name']}")
        print(f"      Dependencies: {len(task['dependencies'])}")

    print("\n✅ Manager Agent demo complete!")
