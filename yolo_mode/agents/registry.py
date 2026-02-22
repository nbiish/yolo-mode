"""
Agent Registry for YOLO Mode OSA Framework

Centralizes configuration and routing for all CLI-based agent tools.

Based on research from:
- CLI_AGENT_INTEGRATION_RESEARCH.md
- OSA_IMPROVEMENT_RECOMMENDATIONS.md
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


# ============================================================================
# ENUMERATIONS
# ============================================================================

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
    MULTIMODAL = "multimodal"
    VALIDATION = "validation"


class OSARole(Enum):
    """OSA Framework roles from .claude/OSA_FRAMEWORK.md"""
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    CODER = "coder"
    SECURITY = "security"
    QA = "qa"


# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

@dataclass
class AgentConfig:
    """Configuration for a CLI agent."""
    name: str                          # Display name
    cli_command: str                    # Command to invoke
    yolo_flag: str = "--yolo"          # YOLO mode flag
    subcommand: Optional[str] = None     # Subcommand if needed (e.g., "run")
    prompt_position: str = "last"        # Where prompt goes: "last" or flag name
    model_flag: Optional[str] = None     # Flag for model selection
    preferred_models: List[str] = field(default_factory=list)
    osa_roles: Set[OSARole] = field(default_factory=set)
    capabilities: Set[AgentCapability] = field(default_factory=set)
    env_vars: Dict[str, str] = field(default_factory=dict)  # Required env vars
    priority: int = 99                 # Selection priority (lower = preferred)
    description: str = ""                # Human-readable description


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
        description="Fast, efficient code generation with Qwen3-Coder-Next model",
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
            AgentCapability.MULTIMODAL,
        },
        env_vars={"GEMINI_YOLO": "true"},
        priority=2,  # Primary for orchestration
        description="Context-driven development with Conductor feature",
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
            AgentCapability.VALIDATION,
            AgentCapability.TESTING,
        },
        env_vars={"CRUSH_YOLO": "true"},
        priority=3,  # Primary for security
        description="Permission-based execution with beautiful terminal UI",
    ),

    "claude": AgentConfig(
        name="Claude Code",
        cli_command="claude",
        yolo_flag="--dangerously-skip-permissions",
        prompt_position="last",
        preferred_models=["claude-sonnet-4.5", "claude-opus-4"],
        osa_roles={OSARole.ARCHITECT, OSARole.QA},
        capabilities={
            AgentCapability.ARCHITECTURE_DESIGN,
            AgentCapability.CODE_REVIEW,
            AgentCapability.TESTING,
            AgentCapability.CODE_GENERATION,
        },
        env_vars={},
        priority=4,  # Fallback for most roles
        description="High-quality reasoning and code generation",
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
            AgentCapability.VALIDATION,
        },
        env_vars={
            "OPENCODE_YOLO": "true",
            "OPENCODE_DANGEROUSLY_SKIP_PERMISSIONS": "true"
        },
        priority=5,
        description="Schema validation and security-focused reviews",
    ),

    "mini": AgentConfig(
        name="Mini-SWE-Agent",
        cli_command="mini",
        yolo_flag="",  # Always runs in autonomous mode
        prompt_position="last",
        preferred_models=["minimax/minimax-m2.5", "gpt-4.1", "claude-sonnet-4.5"],
        osa_roles={OSARole.CODER, OSARole.QA},
        capabilities={
            AgentCapability.CODE_GENERATION,
            AgentCapability.TESTING,
            AgentCapability.VALIDATION,
        },
        env_vars={},
        priority=6,
        description="100-line AI agent for SWE tasks (>74% SWE-bench verified)",
    ),
}


# ============================================================================
# AGENT SELECTION FUNCTIONS
# ============================================================================

def get_agent_for_role(role: OSARole, available: List[str] = None) -> str:
    """
    Get best agent for a role, respecting availability.

    Args:
        role: The OSA role to find an agent for
        available: List of available agent names (defaults to all registered)

    Returns:
        Agent name that best supports the given role
    """
    available = available or list(AGENT_REGISTRY.keys())

    # Filter agents that support this role
    candidates = [
        (name, config)
        for name, config in AGENT_REGISTRY.items()
        if name in available and role in config.osa_roles
    ]

    if not candidates:
        # Fallback: return first available
        return available[0] if available else "claude"

    # Sort by priority (lower = preferred)
    candidates.sort(key=lambda x: x[1].priority)
    return candidates[0][0]


def get_agent_for_capability(capability: AgentCapability, available: List[str] = None) -> str:
    """
    Get the best agent for a specific capability.

    Args:
        capability: The capability needed
        available: List of available agent names

    Returns:
        Agent name that supports the capability
    """
    available = available or list(AGENT_REGISTRY.keys())

    for agent_name in available:
        agent = AGENT_REGISTRY.get(agent_name)
        if agent and capability in agent.capabilities:
            return agent_name

    return available[0] if available else "claude"


def get_all_agents() -> List[str]:
    """Get list of all registered agent names."""
    return list(AGENT_REGISTRY.keys())


def get_agent_config(agent_name: str) -> Optional[AgentConfig]:
    """
    Get configuration for a specific agent.

    Args:
        agent_name: Name of the agent

    Returns:
        AgentConfig or None if not found
    """
    return AGENT_REGISTRY.get(agent_name)


def is_agent_available(agent_name: str) -> bool:
    """Check if an agent is registered."""
    return agent_name in AGENT_REGISTRY


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_role_description(role: OSARole) -> str:
    """Get human-readable description of an OSA role."""
    descriptions = {
        OSARole.ORCHESTRATOR: "Planning, task decomposition, and coordination",
        OSARole.ARCHITECT: "System design, patterns, and architecture",
        OSARole.CODER: "Implementation and code writing",
        OSARole.SECURITY: "Security audits and vulnerability detection",
        OSARole.QA: "Testing, verification, and quality assurance",
    }
    return descriptions.get(role, "")


def print_registry_summary():
    """Print a summary of all registered agents."""
    print("\n=== YOLO Mode Agent Registry ===\n")
    for name, config in AGENT_REGISTRY.items():
        print(f"  {name} (priority {config.priority})")
        print(f"    Description: {config.description}")
        print(f"    OSA Roles: {', '.join(r.value for r in config.osa_roles)}")
        print(f"    Capabilities: {', '.join(c.value for c in config.capabilities)}")
        print(f"    CLI: {config.cli_command}")
        print()


if __name__ == "__main__":
    # Demo: print registry summary
    print_registry_summary()

    # Demo: role-based selection
    print("=== Role-Based Agent Selection ===\n")
    for role in OSARole:
        agent = get_agent_for_role(role)
        print(f"  {role.value:12} → {agent}")
