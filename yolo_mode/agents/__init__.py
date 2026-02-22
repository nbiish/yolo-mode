"""
YOLO Mode Agents Module

Provides unified interface for CLI-based agentic coding tools including:
- Qwen CLI (fast, efficient code generation)
- Gemini CLI (context-driven orchestration)
- Crush CLI (permission-based security)
- Claude Code (high-quality reasoning)
- OpenCode (security-focused reviews)
- Mini-SWE-Agent (100-line AI agent for SWE tasks)

This module centralizes agent configuration, execution, and role-based routing
for the OSA (Orchestrated System of Agents) Framework.

Usage:
    from yolo_mode.agents import run_agent, detect_role_and_agent, AGENT_REGISTRY

    # Run an agent
    output = run_agent("qwen", "write a hello world function")

    # Detect role and agent for a task
    role, agent = detect_role_and_agent("implement authentication")
    print(f"Role: {role}, Agent: {agent}")

    # Get agent configuration
    config = AGENT_REGISTRY.get("gemini")
    print(f"Description: {config.description}")

Components:
    - registry: Agent configurations and selection logic
    - runner: Unified agent execution interface
    - role_detection: Task-to-role mapping with keyword detection
    - resource_aware: Contract-aware agent selection
    - mini_swe_agent: Mini-SWE-Agent integration

Based on research from:
    - reference/CLI_AGENT_INTEGRATION_RESEARCH.md
    - reference/OSA_IMPROVEMENT_RECOMMENDATIONS.md
"""

from .registry import (
    # Enums
    AgentCapability,
    OSARole,

    # Configuration
    AgentConfig,
    AGENT_REGISTRY,

    # Selection functions
    get_agent_for_role,
    get_agent_for_capability,
    get_all_agents,
    get_agent_config,
    is_agent_available,

    # Utilities
    get_role_description,
    print_registry_summary,
)

from .runner import (
    # Main runner class
    AgentRunner,

    # Convenience functions
    run_agent,
    run_agent_interactive,
    get_execution_stats,
    print_execution_stats,

    # Legacy compatibility
    run_agent_legacy,
)

from .role_detection import (
    # Role detection
    detect_role,
    detect_role_and_agent,
    detect_role_with_confidence,

    # Capability detection
    detect_capability,
    detect_task_complexity,

    # Context-aware selection
    select_agent_by_context,

    # Batch processing
    detect_roles_for_batch,
    group_tasks_by_role,

    # Utilities
    get_role_prompt,
    print_detection_result,
)

from . import resource_aware  # noqa: F401
from . import manager  # noqa: F401
from . import parallel_executor  # noqa: F401
from . import config  # noqa: F401
from .resource_aware import (
    # Resource-aware selection
    ResourceAwareSelector,
    build_contract_aware_prompt,

    # Batch optimization
    optimize_agent_batch,
    group_tasks_by_agent,

    # Child contract allocation
    create_child_contract,
    allocate_batch_contracts,

    # Utilities
    get_agent_profile,
    print_selection_stats,
)

# Mini-SWE-Agent integration
from .mini_swe_agent import (
    MiniSweAgentRunner,
    MiniSweResult,
    run_mini_swe_agent,
    is_mini_available,
)

__all__ = [
    # Enums
    "AgentCapability",
    "OSARole",
    "AgentConfig",
    "ManagerAction",

    # Registry
    "AGENT_REGISTRY",
    "get_agent_for_role",
    "get_agent_for_capability",
    "get_all_agents",
    "get_agent_config",
    "is_agent_available",
    "get_role_description",
    "print_registry_summary",

    # Runner
    "AgentRunner",
    "run_agent",
    "run_agent_interactive",
    "get_execution_stats",
    "print_execution_stats",
    "run_agent_legacy",

    # Role Detection
    "detect_role",
    "detect_role_and_agent",
    "detect_role_with_confidence",
    "detect_capability",
    "detect_task_complexity",
    "select_agent_by_context",
    "detect_roles_for_batch",
    "group_tasks_by_role",
    "get_role_prompt",
    "print_detection_result",

    # Resource Aware
    "ResourceAwareSelector",
    "build_contract_aware_prompt",
    "optimize_agent_batch",
    "group_tasks_by_agent",
    "create_child_contract",
    "allocate_batch_contracts",
    "get_agent_profile",
    "print_selection_stats",

    # Manager Agent
    "OSAManagerAgent",
    "create_manager",
    "Task",
    "WorkflowState",

    # Parallel Executor
    "ContractAwareExecutor",
    "create_executor",
    "TaskResult",

    # Configuration
    "AgentConfigManager",
    "create_config",
    "init_config_file",
    "AgentOverride",
    "CustomAgent",
    "AgentConfigFile",

    # Mini-SWE-Agent
    "MiniSweAgentRunner",
    "MiniSweResult",
    "run_mini_swe_agent",
    "is_mini_available",
]

# Version info
__version__ = "1.0.0"
__author__ = "YOLO Mode Contributors"

# Print registry summary on import for debugging (optional)
# Uncomment to see all registered agents on module load
# print_registry_summary()
