# OSA Framework Improvement Recommendations

**Date:** 2026-02-11
**Status:** Implementation Roadmap
**Priority:** High

---

## Executive Summary

Based on comprehensive research of academic papers and CLI agentic tools, this document outlines specific, actionable improvements to the OSA Framework. The recommendations are organized by priority and implementation complexity.

---

## Part 1: CLI Agent Integration (HIGH Priority)

### Current State
The YOLO Loop (`yolo_mode/scripts/yolo_loop.py`) has basic support for:
- claude (via `--dangerously-skip-permissions`)
- opencode (via environment variables)
- gemini (via `--yolo` flag)
- qwen (via `--yolo` flag)
- crush (via `run` subcommand)

### Issue: Inconsistent Agent Interfaces
Each agent has different invocation patterns:
```python
# Current implementation - scattered and inconsistent
if agent == "claude":
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--no-session-persistence"]
elif agent == "opencode":
    cmd = ["opencode", "run", prompt]
    env_vars["OPENCODE_YOLO"] = "true"
elif agent == "gemini":
    cmd = ["gemini", "--yolo", prompt]
elif agent == "qwen":
    cmd = ["qwen", "--yolo", prompt]
elif agent == "crush":
    cmd = ["crush", "run", prompt]
```

### Recommendation 1.1: Create Agent Registry Module

**File:** `yolo_mode/agents/__init__.py`

```python
"""
Agent Registry for YOLO Mode OSA Framework

Centralizes configuration and routing for all CLI-based agent tools.
"""

from .registry import AGENT_REGISTRY, get_agent_for_role, AgentConfig
from .role_detection import detect_role_and_agent
from .runner import run_agent

__all__ = [
    "AGENT_REGISTRY",
    "get_agent_for_role",
    "detect_role_and_agent",
    "run_agent",
    "AgentConfig",
]
```

**File:** `yolo_mode/agents/registry.py`

```python
"""
Agent Registry - Central configuration for all supported CLI agents.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

class AgentCapability(Enum):
    """Core agent capabilities for task routing."""
    CODE_GENERATION = "code_generation"
    REFACTORING = "refactoring"
    TESTING = "testing"
    ARCHITECTURE_DESIGN = "architecture_design"
    PLANNING = "planning"
    ORCHESTRATION = "orchestration"
    SECURITY_AUDIT = "security_audit"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    CONTEXT_MANAGEMENT = "context_management"

class OSARole(Enum):
    """OSA Framework roles from .claude/OSA_FRAMEWORK.md"""
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    CODER = "coder"
    SECURITY = "security"
    QA = "qa"

@dataclass
class AgentConfig:
    """Configuration for a CLI agent."""
    name: str                          # Display name
    cli_command: str                    # Command to invoke
    yolo_flag: str = "--yolo"          # YOLO mode flag
    subcommand: Optional[str] = None     # Subcommand if needed
    prompt_position: str = "last"       # Where prompt goes: "last" or flag name
    model_flag: Optional[str] = None     # Flag for model selection
    preferred_models: List[str] = field(default_factory=list)
    osa_roles: Set[OSARole] = field(default_factory=set)
    capabilities: Set[AgentCapability] = field(default_factory=set)
    env_vars: Dict[str, str] = field(default_factory=dict)  # Required env vars
    priority: int = 99                 # Selection priority (lower = preferred)

# ============================================================================
# COMPLETE AGENT REGISTRY
# ============================================================================

AGENT_REGISTRY: Dict[str, AgentConfig] = {
    "qwen": AgentConfig(
        name="Qwen CLI",
        cli_command="qwen",
        yolo_flag="--yolo",
        model_flag="--model",
        preferred_models=["qwen3-coder-next", "qwen2.5-coder-32b"],
        osa_roles={OSARole.CODER, OSARole.QA},
        capabilities={
            AgentCapability.CODE_GENERATION,
            AgentCapability.REFACTORING,
            AgentCapability.TESTING,
            AgentCapability.DOCUMENTATION,
        },
        env_vars={"QWEN_YOLO": "true"},
        priority=1,  # Primary for coding
    ),

    "gemini": AgentConfig(
        name="Gemini CLI",
        cli_command="gemini",
        yolo_flag="--yolo",
        model_flag="--model",
        preferred_models=["gemini-2.5-flash", "gemini-2.5-pro"],
        osa_roles={OSARole.ORCHESTRATOR, OSARole.ARCHITECT},
        capabilities={
            AgentCapability.PLANNING,
            AgentCapability.ORCHESTRATION,
            AgentCapability.ARCHITECTURE_DESIGN,
            AgentCapability.CONTEXT_MANAGEMENT,
        },
        env_vars={"GEMINI_YOLO": "true"},
        priority=2,  # Primary for orchestration
    ),

    "crush": AgentConfig(
        name="Crush CLI",
        cli_command="crush",
        subcommand="run",
        yolo_flag="--yolo",
        preferred_models=[],
        osa_roles={OSARole.SECURITY, OSARole.QA},
        capabilities={
            AgentCapability.SECURITY_AUDIT,
            AgentCapability.CODE_REVIEW,
            AgentCapability.TESTING,
        },
        env_vars={"CRUSH_YOLO": "true"},
        priority=3,  # Primary for security
    ),

    "claude": AgentConfig(
        name="Claude Code",
        cli_command="claude",
        yolo_flag="--dangerously-skip-permissions",
        prompt_position="last",
        preferred_models=["claude-sonnet-4", "claude-opus-4"],
        osa_roles={OSARole.ARCHITECT, OSARole.QA},
        capabilities={
            AgentCapability.ARCHITECTURE_DESIGN,
            AgentCapability.CODE_REVIEW,
            AgentCapability.TESTING,
        },
        env_vars={},
        priority=4,  # Fallback for most roles
    ),

    "opencode": AgentConfig(
        name="OpenCode",
        cli_command="opencode",
        subcommand="run",
        yolo_flag="",  # Uses env vars instead
        preferred_models=[],
        osa_roles={OSARole.SECURITY},
        capabilities={
            AgentCapability.SECURITY_AUDIT,
            AgentCapability.CODE_REVIEW,
        },
        env_vars={
            "OPENCODE_YOLO": "true",
            "OPENCODE_DANGEROUSLY_SKIP_PERMISSIONS": "true"
        },
        priority=5,
    ),
}

def get_agent_for_role(role: OSARole, available: List[str] = None) -> str:
    """Get best agent for a role, respecting availability."""
    available = available or list(AGENT_REGISTRY.keys())

    # Filter agents that support this role
    candidates = [
        (name, config)
        for name, config in AGENT_REGISTRY.items()
        if name in available and role in config.osa_roles
    ]

    if not candidates:
        # Fallback to first available
        return available[0] if available else "claude"

    # Sort by priority
    candidates.sort(key=lambda x: x[1].priority)
    return candidates[0][0]
```

### Recommendation 1.2: Unified Agent Runner

**File:** `yolo_mode/agents/runner.py`

```python
"""
Unified Agent Runner - Consistent interface for all CLI agents.
"""

import subprocess
import os
from typing import Optional
from .registry import AGENT_REGISTRY

def run_agent(agent: str, prompt: str, verbose: bool = False) -> Optional[str]:
    """
    Run any registered agent with consistent interface.

    Args:
        agent: Agent name (must be in AGENT_REGISTRY)
        prompt: Task prompt
        verbose: Enable verbose logging

    Returns:
        Agent output, or None if failed
    """
    config = AGENT_REGISTRY.get(agent)

    if not config:
        print(f"⚠️ Unknown agent '{agent}', attempting direct invocation")
        return _run_direct(agent, prompt, verbose)

    # Build command based on config
    cmd = [config.cli_command]

    if config.subcommand:
        cmd.append(config.subcommand)

    if config.yolo_flag:
        cmd.append(config.yolo_flag)

    # Add prompt
    cmd.append(prompt)

    if verbose:
        print(f"🤖 Running {config.name}: {cmd}")

    # Prepare environment
    env = os.environ.copy()
    env.update(config.env_vars)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            if verbose:
                print(f"❌ {config.name} error: {result.stderr}")
            return None

        return result.stdout

    except FileNotFoundError:
        print(f"❌ Agent '{agent}' not found. Install with: package manager install {config.cli_command}")
        return None
    except subprocess.TimeoutExpired:
        print(f"⏱️ Agent '{agent}' timed out after 5 minutes")
        return None

def _run_direct(agent: str, prompt: str, verbose: bool) -> Optional[str]:
    """Fallback for unknown agents."""
    try:
        result = subprocess.run(
            [agent, prompt],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None
```

### Recommendation 1.3: Enhanced Role Detection

**File:** `yolo_mode/agents/role_detection.py`

```python
"""
Role Detection - Map tasks to OSA roles and optimal agents.
"""

from typing import Dict, List, Tuple
from .registry import OSARole, AGENT_REGISTRY, get_agent_for_role

# Extended role keywords from yolo_loop.py OSA_ROLES
ROLE_KEYWORDS = {
    OSARole.ORCHESTRATOR: [
        "plan", "orchestrate", "coordinate", "manage", "organize",
        "design workflow", "review plan", "breakdown", "decompose",
        "schedule", "coordinate tasks", "project management",
    ],
    OSARole.ARCHITECT: [
        "architecture", "schema", "design", "structure", "pattern",
        "interface", "api design", "database design", "system design",
        "design pattern", "module structure", "component design",
    ],
    OSARole.CODER: [
        "implement", "write", "code", "create", "build",
        "function", "class", "module", "script", "refactor",
        "add feature", "implement feature", "write code",
    ],
    OSARole.SECURITY: [
        "security", "audit", "validate", "sanitize", "authenticate",
        "authorize", "encrypt", "vulnerability", "secure",
        "zero trust", "input sanitization", "secret management",
    ],
    OSARole.QA: [
        "test", "verify", "check", "validate", "debug",
        "edge case", "coverage", "benchmark", "inspect",
        "unit test", "integration test", "test suite",
    ],
}

def detect_role(task_description: str) -> OSARole:
    """
    Detect the appropriate OSA role for a task.

    Args:
        task_description: The task text to analyze

    Returns:
        The detected OSA role
    """
    task_lower = task_description.lower()

    # Score each role by keyword matches
    role_scores = {}
    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > 0:
            role_scores[role] = score

    if role_scores:
        return max(role_scores, key=role_scores.get)

    return OSARole.CODER  # Default fallback

def detect_role_and_agent(
    task: str,
    available_agents: List[str] = None
) -> Tuple[OSARole, str]:
    """
    Detect both role and optimal agent for a task.

    Args:
        task: Task description
        available_agents: List of available agent names

    Returns:
        Tuple of (OSA role, agent name)
    """
    role = detect_role(task)
    agent = get_agent_for_role(role, available_agents)
    return role, agent
```

---

## Part 2: Contract Integration (HIGH Priority)

### Current State
The Agent Contracts framework (`yolo_mode/contracts.py`) is implemented but not integrated with the YOLO Loop.

### Issue: No Resource Awareness During Agent Selection

The YOLO Loop doesn't consider:
- Remaining token budgets
- Time constraints
- Agent cost profiles

### Recommendation 2.1: Resource-Aware Agent Selection

**Add to:** `yolo_mode/agents/resource_aware.py`

```python
"""
Resource-Aware Agent Selection

Integrates Agent Contracts with agent selection for optimal
resource utilization and cost management.
"""

from typing import Dict, List
from .registry import AGENT_REGISTRY, OSARole, AgentConfig
from ..contracts import AgentContract, ResourceDimension, ContractMode

# Agent performance profiles (based on research)
AGENT_PROFILES = {
    "qwen": {"speed": "fast", "cost": "low", "quality": "high"},
    "gemini": {"speed": "medium", "cost": "medium", "quality": "very_high"},
    "crush": {"speed": "medium", "cost": "low", "quality": "high"},
    "claude": {"speed": "medium", "cost": "high", "quality": "very_high"},
    "opencode": {"speed": "medium", "cost": "low", "quality": "high"},
}

def select_agent_by_contract(
    task: str,
    available_agents: List[str],
    contract: AgentContract
) -> str:
    """
    Select agent based on contract state and task requirements.

    Selection Logic:
    - High token utilization (>80%) → Prefer efficient agents (qwen)
    - Low time remaining (<30s) → Prefer fast agents (qwen)
    - Low utilization → Prefer quality agents (claude, gemini)
    - Default → Role-based selection

    Args:
        task: Task description
        available_agents: Available agent names
        contract: Active contract

    Returns:
        Selected agent name
    """
    status = contract.get_status()
    max_util = status["max_utilization"]
    time_remaining = status["time_remaining"]

    # Urgent mode: speed matters
    if contract.mode == ContractMode.URGENT or time_remaining < 30:
        speed_agents = ["qwen", "claude", "crush", "gemini"]
        for agent in speed_agents:
            if agent in available_agents:
                return agent

    # High utilization: efficiency matters
    if max_util > 0.8:
        efficient_agents = ["qwen", "crush", "opencode"]
        for agent in efficient_agents:
            if agent in available_agents:
                return agent

    # Low utilization: quality matters
    if max_util < 0.5:
        quality_agents = ["claude", "gemini"]
        for agent in quality_agents:
            if agent in available_agents:
                return agent

    # Default: role-based selection
    from .role_detection import detect_role_and_agent
    _, agent = detect_role_and_agent(task, available_agents)
    return agent

def build_contract_aware_prompt(
    base_prompt: str,
    agent: str,
    contract: AgentContract
) -> str:
    """
    Inject contract and agent context into prompts.

    Args:
        base_prompt: Original prompt
        agent: Agent being used
        contract: Active contract

    Returns:
        Enhanced prompt with context
    """
    from ..contracts import build_budget_aware_prompt

    config = AGENT_REGISTRY.get(agent)
    if not config:
        return base_prompt

    # Add budget awareness
    budget_prompt = build_budget_aware_prompt(base_prompt, contract)

    # Add agent-specific instructions
    agent_context = f"""

## AGENT CONTEXT
You are running as: {config.name}
Your primary strengths: {', '.join(c.value for c in config.capabilities)}
"""

    return budget_prompt + agent_context
```

### Recommendation 2.2: Integrate Contracts into YOLO Loop

**Modify:** `yolo_mode/scripts/yolo_loop.py`

```python
# Add imports at top
from yolo_mode.contracts import AgentContract, ContractMode, ContractFactory
from yolo_mode.agents.registry import AGENT_REGISTRY, OSARole
from yolo_mode.agents.role_detection import detect_role_and_agent
from yolo_mode.agents.resource_aware import select_agent_by_contract, build_contract_aware_prompt

def main():
    parser = argparse.ArgumentParser(description="YOLO Mode Loop")
    parser.add_argument("prompt", nargs="+", help="The main goal/prompt")
    parser.add_argument("--tts", action="store_true", help="Enable TTS")
    parser.add_argument("--agent", default="claude", help="Default CLI agent")
    parser.add_argument("--contract-mode", choices=["urgent", "economical", "balanced"],
                      default="balanced", help="Contract mode")
    args = parser.parse_args()

    goal = " ".join(args.prompt)
    agent = args.agent

    # Create contract based on mode
    contract_mode = ContractMode(args.contract_mode.upper())
    contract = ContractFactory.default(mode=contract_mode)
    contract.activate()

    print(f"🚀 YOLO Mode with {agent} | Contract: {contract_mode.value.upper()}")

    # Main loop with contract awareness
    while iteration < max_iterations:
        # Check contract status
        can_proceed, reason = contract.can_proceed()
        if not can_proceed:
            print(f"🛑 Contract violation: {reason}")
            break

        # Get task
        current_task = get_next_task(plan_file)

        # Resource-aware agent selection
        detected_role, role_agent = detect_role_and_agent(current_task, [agent])

        # Override with contract-aware selection if budget is tight
        if contract.get_max_utilization() > 0.7:
            role_agent = select_agent_by_contract(current_task, [agent], contract)
            if role_agent != agent:
                print(f"   🔄 Contract override: {role_agent} (resource-aware)")

        # Build contract-aware prompt
        worker_prompt = build_contract_aware_prompt(
            base_prompt=build_role_based_prompt(...),
            agent=role_agent,
            contract=contract
        )

        # Execute
        output = run_agent(role_agent, worker_prompt)

        # Track resource usage (simplified)
        if output:
            estimated_tokens = len(output.split()) * 1.3  # Rough estimate
            contract.consume_resource(ResourceDimension.TOKENS, estimated_tokens)

        contract.consume_resource(ResourceDimension.ITERATIONS, 1)

        # ... rest of loop
```

---

## Part 3: Enhanced Parallel Execution (MEDIUM Priority)

### Current State
Parallel execution exists in `yolo_mode/scripts/yolo_loop.py` via `ParallelExecutor` class.

### Issue: No Contract-Aware Batching

Parallel execution doesn't consider:
- Per-task resource allocation
- Contract conservation laws
- Agent specialization for batch optimization

### Recommendation 3.1: Contract-Aware Parallel Executor

**Add to:** `yolo_mode/agents/parallel_executor.py`

```python
"""
Contract-Aware Parallel Executor

Enhanced parallel execution with resource-aware task batching
and conservation law enforcement.
"""

from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..contracts import AgentContract, ConservationEnforcer

class ContractAwareExecutor:
    """
    Executes tasks in parallel while respecting contract constraints.
    """

    def __init__(self, contract: AgentContract, max_workers: int = 3):
        self.contract = contract
        self.max_workers = max_workers
        self.conservation = ConservationEnforcer(contract)
        self.completed_tasks: Set[str] = set()

    def plan_batch_execution(self, tasks: List) -> List[List]:
        """
        Plan execution batches respecting conservation laws.

        Args:
            tasks: List of pending tasks

        Returns:
            List of batches, where each batch can run in parallel
        """
        batches = []
        current_batch = []
        current_allocation = self.conservation.allocate_child_budget()

        for task in tasks:
            # Estimate task resource needs
            estimated = self._estimate_task_resources(task)

            # Check if fits in current batch
            if self._fits_in_batch(estimated, current_allocation):
                current_batch.append(task)
                current_allocation = self._reserve_resources(current_allocation, estimated)
            else:
                # Start new batch
                if current_batch:
                    batches.append(current_batch)
                current_batch = [task]
                current_allocation = self.conservation.allocate_child_budget()

        if current_batch:
            batches.append(current_batch)

        return batches

    def _estimate_task_resources(self, task) -> Dict:
        """Estimate resource needs for a task."""
        # Simple heuristic based on task complexity
        words = len(task.description.split())
        return {
            "tokens": words * 50,  # Rough estimate
            "time": min(words * 0.5, 120),  # Cap at 2 minutes
        }

    def _fits_in_batch(self, estimate: Dict, allocation: Dict) -> bool:
        """Check if task fits in remaining batch allocation."""
        # Simplified check
        return True  # TODO: Implement proper budget checking
```

---

## Part 4: Manager Agent Actions (MEDIUM Priority)

### Current State
OSA orchestrator role exists but has limited action space.

### Issue: Limited Orchestration Capabilities

Based on ACM DAI 2025 research, Manager Agent needs 16 specific actions. Current implementation has limited workflow management.

### Recommendation 4.1: Manager Agent Action Space

**Add to:** `yolo_mode/agents/manager.py`

```python
"""
Manager Agent - OSA Orchestrator with full action space.

Based on: "Orchestrating Human-AI Teams: The Manager Agent
as a Unifying Research Challenge" (ACM DAI 2025)
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

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

@dataclass
class WorkflowState:
    """State snapshot for Manager Agent decisions."""
    tasks: List[Dict]  # All tasks with status
    agents: Dict[str, Dict]  # Available agents with capabilities
    dependencies: Dict[str, List[str]]  # Task dependency graph
    constraints: Dict  # Resource/time constraints
    progress: Dict  # Completion metrics

class OSAManagerAgent:
    """
    OSA Orchestrator with full Manager Agent action space.

    Implements workflow management as defined in ACM DAI 2025.
    """

    def __init__(self, goal: str, state_file: str):
        self.goal = goal
        self.state_file = state_file
        self.actions = self._define_actions()
        self.state = self._load_state()

    def _define_actions(self) -> Dict[ManagerAction, Callable]:
        """Define all 16 Manager Agent actions."""
        return {
            ManagerAction.ASSIGN_TASK: self._assign_task,
            ManagerAction.CREATE_TASK: self._create_task,
            ManagerAction.REMOVE_TASK: self._remove_task,
            ManagerAction.SEND_MESSAGE: self._send_message,
            ManagerAction.NOOP: self._noop,
            ManagerAction.GET_WORKFLOW_STATUS: self._get_workflow_status,
            ManagerAction.GET_AVAILABLE_AGENTS: self._get_available_agents,
            ManagerAction.GET_PENDING_TASKS: self._get_pending_tasks,
            ManagerAction.REFINE_TASK: self._refine_task,
            ManagerAction.ADD_DEPENDENCY: self._add_dependency,
            ManagerAction.REMOVE_DEPENDENCY: self._remove_dependency,
            ManagerAction.INSPECT_TASK: self._inspect_task,
            ManagerAction.DECOMPOSE_TASK: self._decompose_task,
            ManagerAction.REQUEST_END: self._request_end,
            ManagerAction.FAILED_ACTION: self._failed_action,
            ManagerAction.ASSIGN_ALL: self._assign_all,
        }

    def orchestrate(self) -> bool:
        """
        Main orchestration loop.

        Returns:
            True if workflow completed successfully
        """
        while not self._is_complete():
            # Get current state
            status = self.actions[ManagerAction.GET_WORKFLOW_STATUS]()

            # Select action (could use LLM for selection)
            action = self._select_action(status)

            # Execute action
            result = self.actions[action](status)

            # Update state
            self._update_state(result)

        return self._finalize_workflow()

    def _assign_task(self, task_id: str, agent_id: str) -> bool:
        """Route task to capacity/skill-matched agent."""
        # Implementation
        pass

    def _create_task(self, name: str, description: str, est_hrs: float = 1.0) -> str:
        """Add new work item to workflow."""
        # Implementation
        pass

    def _get_workflow_status(self) -> WorkflowState:
        """Snapshot workflow health (task histogram, ready set)."""
        # Implementation
        pass

    # ... other action implementations
```

---

## Part 5: State File Improvements (LOW Priority)

### Current State
State is stored in `.claude/yolo-state.md` with basic iteration count.

### Issue: Limited State Information

State file doesn't track:
- Contract status
- Resource utilization
- Agent usage statistics
- Task completion metrics

### Recommendation 5.1: Enhanced State File Format

**New format:** `.claude/yolo-state.yaml`

```yaml
# YOLO Mode State File
# Auto-generated - do not edit manually

metadata:
  version: "2.0"
  created_at: "2026-02-11T10:00:00Z"
  last_updated: "2026-02-11T10:30:00Z"

goal:
  original: "help me research CLI agent integration"
  current_status: "in_progress"

session:
  iteration: 15
  max_iterations: 50
  start_time: "2026-02-11T10:00:00Z"

contract:
  mode: balanced
  state: active
  status:
    max_utilization: 0.45
    time_remaining: 180
    is_expired: false
    is_violated: false

resources:
  tokens:
    budget: 100000
    consumed: 45000
    utilization: 0.45
  iterations:
    budget: 10
    consumed: 3
    utilization: 0.30
  time:
    budget: 300
    remaining: 180
    utilization: 0.40

agents:
  qwen:
    tasks_assigned: 8
    tasks_completed: 7
    success_rate: 0.875
  gemini:
    tasks_assigned: 3
    tasks_completed: 3
    success_rate: 1.0
  crush:
    tasks_assigned: 2
    tasks_completed: 2
    success_rate: 1.0

tasks:
  total: 15
  completed: 12
  pending: 3
  failed: 0

workflow:
  current_phase: "execution"
  next_actions:
    - execute remaining tasks
    - verify completion
    - generate report
```

---

## Part 6: Testing & Validation (MEDIUM Priority)

### Recommendation 6.1: Agent Integration Tests

**File:** `tests/test_agents/test_integration.py`

```python
"""
Tests for CLI agent integration.
"""

import pytest
from yolo_mode.agents.registry import AGENT_REGISTRY, get_agent_for_role, OSARole
from yolo_mode.agents.role_detection import detect_role_and_agent
from yolo_mode.agents.runner import run_agent

class TestAgentRegistry:
    """Test agent registry configuration."""

    def test_all_agents_have_configs(self):
        """All agents should have complete configurations."""
        for name, config in AGENT_REGISTRY.items():
            assert config.name
            assert config.cli_command
            assert config.yolo_flag
            assert len(config.osa_roles) > 0

    def test_get_agent_for_role(self):
        """Test role-based agent selection."""
        coder_agent = get_agent_for_role(OSARole.CODER)
        assert coder_agent in ["qwen", "claude"]

        orchestrator_agent = get_agent_for_role(OSARole.ORCHESTRATOR)
        assert orchestrator_agent in ["gemini", "claude"]

class TestRoleDetection:
    """Test task-to-role mapping."""

    def test_coder_detection(self):
        """Coding tasks should map to coder role."""
        role, agent = detect_role_and_agent("implement a user class")
        assert role == OSARole.CODER

    def test_orchestrator_detection(self):
        """Planning tasks should map to orchestrator role."""
        role, agent = detect_role_and_agent("plan the implementation")
        assert role == OSARole.ORCHESTRATOR

class TestContractIntegration:
    """Test contract-aware agent selection."""

    def test_high_utilization_selects_efficient(self):
        """High utilization should select efficient agents."""
        # Test implementation
        pass
```

---

## Implementation Priority Summary

| Priority | Feature | Effort | Impact | Files |
|----------|----------|--------|--------|-------|
| **HIGH** | Agent Registry Module | Medium | High | `yolo_mode/agents/` |
| **HIGH** | Unified Agent Runner | Low | High | `yolo_mode/agents/runner.py` |
| **HIGH** | Contract-Aware Selection | Medium | High | `yolo_mode/agents/resource_aware.py` |
| **MEDIUM** | Manager Agent Actions | High | Medium | `yolo_mode/agents/manager.py` |
| **MEDIUM** | Enhanced Parallel Executor | Medium | Medium | `yolo_mode/agents/parallel_executor.py` |
| **LOW** | State File Format | Low | Low | `.claude/yolo-state.yaml` |
| **MEDIUM** | Testing Suite | Medium | Medium | `tests/test_agents/` |

---

## Quick Start Implementation Guide

### Step 1: Create Agent Module (Day 1-2)

```bash
mkdir -p yolo_mode/agents
touch yolo_mode/agents/__init__.py
touch yolo_mode/agents/registry.py
touch yolo_mode/agents/runner.py
touch yolo_mode/agents/role_detection.py
```

### Step 2: Implement Registry (Day 2-3)

Copy the `AGENT_REGISTRY` from Recommendation 1.1 into `registry.py`.

### Step 3: Update YOLO Loop (Day 3-4)

Modify `yolo_mode/scripts/yolo_loop.py` to use the new agent system:

```python
# Replace existing run_agent with:
from yolo_mode.agents.runner import run_agent

# Replace role detection with:
from yolo_mode.agents.role_detection import detect_role_and_agent
```

### Step 4: Test Integration (Day 4-5)

```bash
# Test each agent
python -m yolo_mode.agents.runner qwen "write hello world"
python -m yolo_mode.agents.runner gemini "plan a project"
python -m yolo_mode.agents.runner crush "audit this code"

# Test full YOLO loop
python -m yolo_mode.scripts.yolo_loop "implement a REST API" --agent qwen
```

---

## Conclusion

The OSA Framework can be significantly improved through:

1. **CLI Agent Integration** - Unified registry and runner for Qwen, Gemini, Crush, and others
2. **Contract Integration** - Resource-aware agent selection based on remaining budget
3. **Enhanced Orchestration** - Full Manager Agent action space from ACM DAI 2025
4. **Better State Management** - YAML-based state with comprehensive tracking

The modular design allows incremental implementation, with the agent registry providing immediate value while more advanced features like contract-aware selection and Manager Agent actions can be added progressively.

---

*Prepared by YOLO Mode autonomous research agent*
*Date: 2026-02-11*
