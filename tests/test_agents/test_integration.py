"""
Tests for CLI Agent Integration

Tests the agent registry, runner, role detection, and contract integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Import OSA components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from yolo_mode.agents.registry import (
    AGENT_REGISTRY,
    get_agent_for_role,
    OSARole,
    AgentCapability,
    AgentConfig
)
from yolo_mode.agents.role_detection import (
    detect_role,
    detect_role_and_agent,
    detect_capability
)
from yolo_mode.agents.runner import run_agent
from yolo_mode.agents.resource_aware import (
    ResourceAwareSelector,
    build_contract_aware_prompt,
    optimize_agent_batch
)
from yolo_mode.agents.manager import (
    OSAManagerAgent,
    ManagerAction,
    create_manager,
    Task,
    WorkflowState
)
from yolo_mode.agents.parallel_executor import (
    ContractAwareExecutor,
    create_executor,
    TaskResult
)
from yolo_mode.contracts import (
    ContractMode,
    ContractFactory,
    AgentContract
)


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================

class TestAgentRegistry:
    """Test agent registry configuration."""

    def test_all_agents_have_configs(self):
        """All agents should have complete configurations."""
        for name, config in AGENT_REGISTRY.items():
            assert config.name, f"{name} should have a name"
            assert config.cli_command, f"{name} should have a cli_command"
            assert config.yolo_flag, f"{name} should have a yolo_flag"
            assert len(config.osa_roles) > 0, f"{name} should have OSA roles"
            assert len(config.capabilities) > 0, f"{name} should have capabilities"

    def test_expected_agents_exist(self):
        """Expected agents should be in registry."""
        expected_agents = ["qwen", "gemini", "crush", "claude", "opencode"]
        for agent in expected_agents:
            assert agent in AGENT_REGISTRY, f"{agent} should be in registry"

    def test_qwen_config(self):
        """Qwen CLI should have correct configuration."""
        config = AGENT_REGISTRY.get("qwen")
        assert config.name == "Qwen CLI"
        assert config.yolo_flag == "--yolo"
        assert config.model_flag == "--model"
        assert "qwen3-coder-next" in config.preferred_models

    def test_gemini_config(self):
        """Gemini CLI should have correct configuration."""
        config = AGENT_REGISTRY.get("gemini")
        assert config.name == "Gemini CLI"
        assert config.yolo_flag == "--yolo"
        assert OSARole.ORCHESTRATOR in config.osa_roles
        assert OSARole.ARCHITECT in config.osa_roles

    def test_crush_config(self):
        """Crush CLI should have correct configuration."""
        config = AGENT_REGISTRY.get("crush")
        assert config.name == "Crush CLI"
        assert config.yolo_flag == "-y"
        assert OSARole.SECURITY in config.osa_roles
        assert OSARole.QA in config.osa_roles


# ============================================================================
# ROLE DETECTION TESTS
# ============================================================================

class TestRoleDetection:
    """Test task-to-role mapping."""

    def test_coder_keywords(self):
        """Coding tasks should map to Coder role."""
        coder_tasks = [
            "implement a function",
            "create a class",
            "write code for",
            "add method to",
            "refactor the code"
        ]

        for task in coder_tasks:
            role = detect_role(task)
            assert role == OSARole.CODER, f"Task '{task}' should map to CODER, got {role}"

    def test_orchestrator_keywords(self):
        """Planning tasks should map to Orchestrator role."""
        orchestrator_tasks = [
            "plan the implementation",
            "coordinate the workflow",
            "manage the tasks",
            "organize the project",
            "design the architecture"
        ]

        for task in orchestrator_tasks:
            role = detect_role(task)
            assert role == OSARole.ORCHESTRATOR, f"Task '{task}' should map to ORCHESTRATOR, got {role}"

    def test_architect_keywords(self):
        """Architecture tasks should map to Architect role."""
        architect_tasks = [
            "design the database schema",
            "create the API structure",
            "define the interface",
            "architecture design",
            "schema definition"
        ]

        for task in architect_tasks:
            role = detect_role(task)
            assert role == OSARole.ARCHITECT, f"Task '{task}' should map to ARCHITECT, got {role}"

    def test_security_keywords(self):
        """Security tasks should map to Security role."""
        security_tasks = [
            "audit for security issues",
            "check for vulnerabilities",
            "security review",
            "penetration testing",
            "validate permissions"
        ]

        for task in security_tasks:
            role = detect_role(task)
            assert role == OSARole.SECURITY, f"Task '{task}' should map to SECURITY, got {role}"

    def test_qa_keywords(self):
        """QA tasks should map to QA role."""
        qa_tasks = [
            "write tests for",
            "test the implementation",
            "verify functionality",
            "quality assurance",
            "run test suite"
        ]

        for task in qa_tasks:
            role = detect_role(task)
            assert role == OSARole.QA, f"Task '{task}' should map to QA, got {role}"

    def test_role_and_agent_detection(self):
        """Test combined role and agent detection."""
        test_cases = [
            ("implement authentication", "coder", ["qwen", "claude"]),
            ("plan the architecture", "orchestrator", ["gemini", "claude"]),
            ("security audit", "security", ["crush", "opencode"]),
        ]

        for task, expected_role, valid_agents in test_cases:
            role, agent = detect_role_and_agent(task)
            assert role.value == expected_role, f"Task '{task}' should detect role {expected_role}"
            assert agent in valid_agents, f"Agent '{agent}' should be in {valid_agents}"


# ============================================================================
# RESOURCE-AWARE SELECTION TESTS
# ============================================================================

class TestResourceAwareSelection:
    """Test contract-aware agent selection."""

    def test_selector_initialization(self):
        """Selector should initialize correctly."""
        contract = ContractFactory.default()
        contract.activate()

        selector = ResourceAwareSelector(contract)
        assert selector.contract == contract
        assert len(selector.selection_history) == 0

    def test_low_utilization_selects_quality(self):
        """Low utilization should prefer quality agents."""
        contract = ContractFactory.default()
        contract.activate()

        # Simulate low utilization (30%)
        from yolo_mode.contracts import ResourceDimension
        contract.consume_resource(ResourceDimension.TOKENS, 30000)  # 30%

        selector = ResourceAwareSelector(contract)
        available = ["qwen", "claude", "gemini"]

        # Add a task that would trigger low utilization path
        agent, reasoning = selector.select_agent("implement feature", available)
        # Should prefer quality (claude or gemini) at low utilization
        assert agent in ["claude", "gemini"], f"Low utilization should select quality agent, got {agent}"

    def test_high_utilization_selects_efficient(self):
        """High utilization should prefer efficient agents."""
        contract = ContractFactory.default()
        contract.activate()

        # Simulate high utilization (85%)
        from yolo_mode.contracts import ResourceDimension
        contract.consume_resource(ResourceDimension.TOKENS, 85000)  # 85%

        selector = ResourceAwareSelector(contract)
        available = ["qwen", "claude", "gemini"]

        agent, reasoning = selector.select_agent("implement feature", available)
        # Should prefer efficiency (qwen)
        assert agent == "qwen", f"High utilization should select efficient agent, got {agent}"

    def test_urgent_mode_selects_fast(self):
        """Urgent mode should prefer fast agents."""
        contract = ContractFactory.default(mode=ContractMode.URGENT)
        contract.activate()

        selector = ResourceAwareSelector(contract)
        available = ["qwen", "claude", "gemini"]

        agent, reasoning = selector.select_agent("implement feature", available)
        # Urgent mode should prefer speed (qwen)
        assert agent == "qwen", f"Urgent mode should select fast agent, got {agent}"


# ============================================================================
# MANAGER AGENT TESTS
# ============================================================================

class TestManagerAgent:
    """Test Manager Agent with 16-action space."""

    def test_manager_initialization(self):
        """Manager should initialize correctly."""
        manager = create_manager("Test goal")

        assert manager.goal == "Test goal"
        assert len(manager.actions) == 16, "Manager should have 16 actions"
        assert ManagerAction.ASSIGN_TASK in manager.actions

    def test_all_actions_defined(self):
        """All 16 ManagerAction enum values should be defined."""
        expected_actions = {
            ManagerAction.ASSIGN_TASK,
            ManagerAction.CREATE_TASK,
            ManagerAction.REMOVE_TASK,
            ManagerAction.SEND_MESSAGE,
            ManagerAction.NOOP,
            ManagerAction.GET_WORKFLOW_STATUS,
            ManagerAction.GET_AVAILABLE_AGENTS,
            ManagerAction.GET_PENDING_TASKS,
            ManagerAction.REFINE_TASK,
            ManagerAction.ADD_DEPENDENCY,
            ManagerAction.REMOVE_DEPENDENCY,
            ManagerAction.INSPECT_TASK,
            ManagerAction.DECOMPOSE_TASK,
            ManagerAction.REQUEST_END,
            ManagerAction.FAILED_ACTION,
            ManagerAction.ASSIGN_ALL
        }

        assert len(expected_actions) == 16, "Should have exactly 16 actions"

    def test_task_creation(self):
        """Manager should be able to create tasks."""
        manager = create_manager("Test goal")

        task_id = manager._create_task(
            name="Test task",
            description="A test task description",
            est_hrs=2.0
        )

        assert task_id in manager.state.tasks
        assert manager.state.tasks[task_id].name == "Test task"

    def test_task_assignment(self):
        """Manager should be able to assign tasks to agents."""
        manager = create_manager("Test goal")

        task_id = manager._create_task("Test task", "Description", 1.0)
        success = manager._assign_task(task_id, "qwen")

        assert success, "Task assignment should succeed"
        assert manager.state.tasks[task_id].assigned_to == "qwen"

    def test_workflow_status(self):
        """Manager should provide workflow status."""
        manager = create_manager("Test goal")

        # Create some tasks
        manager._create_task("Task 1", "Description 1")
        manager._create_task("Task 2", "Description 2")
        manager._create_task("Task 3", "Description 3")

        status = manager.actions[ManagerAction.GET_WORKFLOW_STATUS]()

        assert status["total_tasks"] == 3
        assert "pending" in status
        assert "in_progress" in status

    def test_pending_tasks_filtering(self):
        """Pending tasks should be filterable by dependencies."""
        manager = create_manager("Test goal")

        # Create tasks with dependencies
        task1 = manager._create_task("Task 1", "Description 1")
        task2 = manager._create_task("Task 2", "Description 2")
        manager._add_dependency(task1, task2)

        pending = manager.actions[ManagerAction.GET_PENDING_TASKS]()

        # Task 2 should depend on task 1
        assert len(pending) == 2
        # Task 2 (depends on task 1) should not be ready
        task2_info = next((t for t in pending if t["id"] == task2), None)
        assert task2_info["can_start"] == False


# ============================================================================
# PARALLEL EXECUTOR TESTS
# ============================================================================

class TestParallelExecutor:
    """Test contract-aware parallel execution."""

    def test_executor_initialization(self):
        """Executor should initialize correctly."""
        contract = ContractFactory.default()
        executor = create_executor(contract=contract, max_workers=3)

        assert executor.contract == contract
        assert executor.max_workers == 3
        assert executor.conservation is not None

    def test_simple_parallel_execution(self):
        """Executor should run tasks in parallel without contract."""
        executor = create_executor(contract=None, max_workers=2)

        tasks = ["Task 1", "Task 2"]
        results = executor.execute_batch(tasks)

        assert len(results) == 2
        assert all(isinstance(r, TaskResult) for r in results)

    def test_contract_aware_batching(self):
        """Executor should batch tasks by contract constraints."""
        contract = ContractFactory.default()
        contract.activate()

        executor = create_executor(contract=contract, max_workers=2)

        # Create multiple tasks
        tasks = [f"Task {i}" for i in range(10)]
        results = executor.execute_batch(tasks)

        assert len(results) == 10
        # Check that results have contract tracking
        for result in results:
            assert isinstance(result, TaskResult)

    def test_resource_consumption_tracking(self):
        """Executor should track resource consumption."""
        contract = ContractFactory.default()
        contract.activate()

        executor = create_executor(contract=contract, max_workers=1)

        results = executor.execute_batch(["Test task"])

        # Contract should reflect consumption
        status = contract.get_status()
        assert status["consumption"].get("iterations", 0) > 0


# ============================================================================
# CONTRACT TESTS
# ============================================================================

class TestAgentContracts:
    """Test Agent Contracts framework."""

    def test_contract_modes(self):
        """All contract modes should be available."""
        assert ContractMode.URGENT.value == "urgent"
        assert ContractMode.ECONOMICAL.value == "economical"
        assert ContractMode.BALANCED.value == "balanced"

    def test_contract_factory_default(self):
        """Factory should create contracts with correct defaults."""
        contract = ContractFactory.default(mode=ContractMode.BALANCED)
        contract.activate()

        status = contract.get_status()
        assert status["mode"] == "balanced"
        assert status["state"] == "active"

    def test_balanced_mode_constraints(self):
        """Balanced mode should have correct constraints."""
        contract = ContractFactory.default(mode=ContractMode.BALANCED)
        contract.activate()

        from yolo_mode.contracts import ResourceDimension
        token_budget = contract.R.get_budget(ResourceDimension.TOKENS)
        iter_budget = contract.R.get_budget(ResourceDimension.ITERATIONS)
        duration = contract.T.duration

        assert token_budget == 100000
        assert iter_budget == 10
        assert duration == 90.0

    def test_urgent_mode_constraints(self):
        """Urgent mode should have tighter constraints."""
        contract = ContractFactory.default(mode=ContractMode.URGENT)
        contract.activate()

        from yolo_mode.contracts import ResourceDimension
        token_budget = contract.R.get_budget(ResourceDimension.TOKENS)
        iter_budget = contract.R.get_budget(ResourceDimension.ITERATIONS)
        duration = contract.T.duration

        assert token_budget == 50000
        assert iter_budget == 3
        assert duration == 30.0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAgentIntegration:
    """Integration tests for full agent workflow."""

    def test_full_agent_workflow(self):
        """Test complete workflow from task selection to execution."""
        # This test would require actual CLI tools installed
        # For now, test the selection logic

        task = "Implement a user authentication system"

        # Detect role
        role = detect_role(task)
        assert role == OSARole.CODER

        # Get agent for role
        agent = get_agent_for_role(role, ["qwen", "claude", "gemini"])
        assert agent in ["qwen", "claude"]

        # Get agent config
        config = AGENT_REGISTRY.get(agent)
        assert config is not None

    def test_contract_aware_workflow(self):
        """Test contract-aware agent selection workflow."""
        contract = ContractFactory.default(mode=ContractMode.BALANCED)
        contract.activate()

        selector = ResourceAwareSelector(contract)

        # Simulate reaching high utilization
        from yolo_mode.contracts import ResourceDimension
        contract.consume_resource(ResourceDimension.TOKENS, 85000)

        # Should now prefer efficient agents
        available = ["qwen", "claude", "gemini", "crush"]
        agent, reasoning = selector.select_agent("Continue work", available)

        # At high utilization, should prefer qwen (efficient)
        assert agent == "qwen"

    def test_manager_task_workflow(self):
        """Test Manager Agent task workflow."""
        manager = create_manager("Test workflow goal")

        # Create tasks
        t1 = manager._create_task("Research", "Research topic")
        t2 = manager._create_task("Implement", "Implement feature")
        t3 = manager._create_task("Test", "Test implementation")

        # Add dependency
        manager._add_dependency(t2, t1)
        manager._add_dependency(t3, t2)

        # Assign tasks
        manager._assign_task(t1, "qwen")

        # Check workflow status
        status = manager.actions[ManagerAction.GET_WORKFLOW_STATUS]()
        assert status["total_tasks"] == 3
        assert status["pending"] == 2  # t2 and t3


# ============================================================================
# TEST UTILITIES
# ============================================================================

def run_tests_with_coverage():
    """Run tests and show coverage."""
    import subprocess

    print("Running agent integration tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_agents/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    # Run tests when executed directly
    import sys
    sys.exit(0 if run_tests_with_coverage() else 1)
