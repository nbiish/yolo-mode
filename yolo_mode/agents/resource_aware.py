"""
Resource-Aware Agent Selection

Integrates Agent Contracts with agent selection for optimal
resource utilization and cost management.

Based on Agent Contracts paper (arXiv:2601.08815, January 2025)
which shows 90% token reduction through budget-aware prompting.

Selection Logic:
- High token utilization (>80%) → Prefer efficient agents (qwen, crush)
- Low time remaining (<30s) → Prefer fast agents (qwen)
- Low utilization → Prefer quality agents (claude, gemini)
- Default → Role-based selection
"""

import time
from typing import Dict, List, Optional, Tuple
from .registry import (
    AGENT_REGISTRY,
    OSARole,
    AgentConfig,
    get_agent_for_role,
)
from ..contracts import (
    AgentContract,
    ResourceDimension,
    ContractMode,
    ConservationEnforcer,
)


# ============================================================================
# AGENT PERFORMANCE PROFILES
# ============================================================================

# Agent performance profiles based on research
AGENT_PROFILES: Dict[str, Dict[str, str]] = {
    "qwen": {
        "speed": "fast",
        "cost": "low",
        "quality": "high",
        "efficiency": "very_high",
        "token_efficiency": "very_high",
    },
    "gemini": {
        "speed": "medium",
        "cost": "medium",
        "quality": "very_high",
        "efficiency": "high",
        "token_efficiency": "high",
    },
    "crush": {
        "speed": "medium",
        "cost": "low",
        "quality": "high",
        "efficiency": "high",
        "token_efficiency": "high",
    },
    "claude": {
        "speed": "medium",
        "cost": "high",
        "quality": "very_high",
        "efficiency": "medium",
        "token_efficiency": "medium",
    },
    "opencode": {
        "speed": "medium",
        "cost": "low",
        "quality": "high",
        "efficiency": "high",
        "token_efficiency": "high",
    },
}

# Rankings by attribute
SPEED_RANKING = ["qwen", "claude", "crush", "gemini", "opencode"]
COST_RANKING = ["qwen", "crush", "opencode", "gemini", "claude"]
QUALITY_RANKING = ["claude", "gemini", "qwen", "crush", "opencode"]
EFFICIENCY_RANKING = ["qwen", "crush", "opencode", "gemini", "claude"]


# ============================================================================
# RESOURCE-AWARE SELECTION
# ============================================================================

class ResourceAwareSelector:
    """
    Selects agents based on contract state and task requirements.

    Implements budget-aware prompting strategies from the Agent Contracts paper,
    enabling agents to self-regulate based on remaining resources.
    """

    def __init__(self, contract: Optional[AgentContract] = None):
        """
        Initialize the selector.

        Args:
            contract: Active contract for resource tracking
        """
        self.contract = contract
        self.selection_history: List[Dict] = []

    def select_agent(
        self,
        task: str,
        available_agents: List[str],
        role_override: Optional[OSARole] = None
    ) -> Tuple[str, str]:
        """
        Select agent based on contract state and task requirements.

        Args:
            task: Task description
            available_agents: Available agent names
            role_override: Optional role override (skips role detection)

        Returns:
            Tuple of (agent_name, reasoning)
        """
        # Get contract status if available
        if self.contract:
            status = self.contract.get_status()
            max_util = status["max_utilization"]
            time_remaining = status["time_remaining"]
        else:
            max_util = 0
            time_remaining = float('inf')

        # Determine role
        if role_override:
            role = role_override
        else:
            from .role_detection import detect_role
            role = detect_role(task)

        # Apply selection logic
        reasoning = f"Role: {role.value}"

        # Urgent mode or low time: prioritize speed
        if self.contract and self.contract.mode == ContractMode.URGENT:
            agent = self._select_by_speed(available_agents)
            reasoning += f" → Urgent: {agent} (fast)"
            self._track_selection(task, agent, "urgent")
            return agent, reasoning

        if time_remaining < 30:
            agent = self._select_by_speed(available_agents)
            reasoning += f" → Low time: {agent} (fast)"
            self._track_selection(task, agent, "time_constraint")
            return agent, reasoning

        # High utilization: prioritize efficiency
        if max_util > 0.8:
            agent = self._select_by_efficiency(available_agents)
            reasoning += f" → High utilization ({max_util*100:.0f}%): {agent} (efficient)"
            self._track_selection(task, agent, "resource_constraint")
            return agent, reasoning

        # Medium utilization: balanced approach
        if max_util > 0.5:
            agent = self._select_by_cost(available_agents)
            reasoning += f" → Medium utilization: {agent} (cost-effective)"
            self._track_selection(task, agent, "balanced")
            return agent, reasoning

        # Low utilization: prioritize quality
        if max_util < 0.5:
            agent = self._select_by_quality(available_agents)
            reasoning += f" → Low utilization: {agent} (quality)"
            self._track_selection(task, agent, "quality")
            return agent, reasoning

        # Default: role-based selection
        agent = get_agent_for_role(role, available_agents)
        reasoning += f" → Default: {agent} (role-based)"
        self._track_selection(task, agent, "default")
        return agent, reasoning

    def _select_by_speed(self, available: List[str]) -> str:
        """Select fastest available agent."""
        for agent in SPEED_RANKING:
            if agent in available:
                return agent
        return available[0] if available else "claude"

    def _select_by_efficiency(self, available: List[str]) -> str:
        """Select most efficient available agent."""
        for agent in EFFICIENCY_RANKING:
            if agent in available:
                return agent
        return available[0] if available else "claude"

    def _select_by_cost(self, available: List[str]) -> str:
        """Select lowest cost available agent."""
        for agent in COST_RANKING:
            if agent in available:
                return agent
        return available[0] if available else "claude"

    def _select_by_quality(self, available: List[str]) -> str:
        """Select highest quality available agent."""
        for agent in QUALITY_RANKING:
            if agent in available:
                return agent
        return available[0] if available else "claude"

    def _track_selection(self, task: str, agent: str, reason: str):
        """Track selection for analysis."""
        self.selection_history.append({
            "task": task[:100],  # Truncate for storage
            "agent": agent,
            "reason": reason,
            "timestamp": time.time(),
        })

    def get_selection_stats(self) -> Dict[str, Dict]:
        """Get statistics on agent selections."""
        stats = {}
        for entry in self.selection_history:
            agent = entry["agent"]
            if agent not in stats:
                stats[agent] = {"count": 0, "by_reason": {}}
            stats[agent]["count"] += 1
            reason = entry["reason"]
            if reason not in stats[agent]["by_reason"]:
                stats[agent]["by_reason"][reason] = 0
            stats[agent]["by_reason"][reason] += 1
        return stats


# ============================================================================
# CONTRACT-AWARE PROMPT BUILDING
# ============================================================================

def build_contract_aware_prompt(
    base_prompt: str,
    agent: str,
    contract: Optional[AgentContract] = None
) -> str:
    """
    Inject contract and agent context into prompts.

    Based on budget-aware prompting research showing that dynamic
    status updates enable agents to self-regulate.

    Args:
        base_prompt: Original prompt
        agent: Agent being used
        contract: Active contract

    Returns:
        Enhanced prompt with context
    """
    if not contract:
        return base_prompt

    config = AGENT_REGISTRY.get(agent)
    if not config:
        return base_prompt

    # Get contract status
    status = contract.get_status()
    max_util = status["max_utilization"]

    # Build budget awareness section
    budget_section = f"""

## RESOURCE BUDGET (Contract Mode: {contract.mode.value.upper()})

You are operating under a resource contract with the following constraints:
"""

    for resource, utilization in status["utilization"].items():
        budget = status["budgets"].get(resource, float('inf'))
        if budget != float('inf'):
            consumed = status["consumption"][resource]
            budget_section += f"- {resource.upper()}: {consumed:.0f} / {budget:.0f} ({utilization*100:.1f}%)\\n"

    budget_section += f"""
Time Remaining: {status['time_remaining']:.0f} seconds
Overall Utilization: {max_util*100:.1f}%

## BUDGET AWARENESS INSTRUCTIONS

- Monitor your resource consumption carefully
- When utilization is high (>80%), be concise and efficient
- Stop and report completion if running low on budget
- Do NOT exceed the specified resource limits

"""

    # Add agent-specific instructions
    agent_section = f"""

## AGENT CONTEXT
You are running as: {config.name}
Your primary strengths: {', '.join(c.value for c in config.capabilities)}
"""

    # Add urgency warning if needed
    urgency_section = ""
    if max_util > 0.8 or status["time_remaining"] < 60:
        urgency_section = """

## ⚠️ RESOURCE CONSTRAINT ACTIVE

You are running low on resources. Please:
- Be concise and direct
- Avoid unnecessary explanations
- Focus on core deliverables
- Report completion early rather than late
"""

    return budget_section + agent_section + urgency_section + "\n" + base_prompt


# ============================================================================
# BATCH OPTIMIZATION
# ============================================================================

def optimize_agent_batch(
    tasks: List[str],
    available_agents: List[str],
    contract: Optional[AgentContract] = None
) -> Dict[str, str]:
    """
    Optimize agent assignment for a batch of tasks.

    Groups tasks by role and assigns optimal agents based on
    contract state to minimize resource usage.

    Args:
        tasks: List of task descriptions
        available_agents: Available agents
        contract: Active contract

    Returns:
        Dictionary mapping task → agent
    """
    selector = ResourceAwareSelector(contract)

    assignment = {}

    for task in tasks:
        agent, _ = selector.select_agent(task, available_agents)
        assignment[task] = agent

    return assignment


def group_tasks_by_agent(
    tasks: List[str],
    available_agents: List[str],
    contract: Optional[AgentContract] = None
) -> Dict[str, List[str]]:
    """
    Group tasks by optimal agent for batch execution.

    Args:
        tasks: List of task descriptions
        available_agents: Available agents
        contract: Active contract

    Returns:
        Dictionary mapping agent → list of tasks
    """
    assignment = optimize_agent_batch(tasks, available_agents, contract)

    grouped: Dict[str, List[str]] = {agent: [] for agent in available_agents}

    for task, agent in assignment.items():
        grouped[agent].append(task)

    return grouped


# ============================================================================
# CHILD CONTRACT ALLOCATION
# ============================================================================

def create_child_contract(
    parent: AgentContract,
    mode: ContractMode = ContractMode.BALANCED
) -> AgentContract:
    """
    Create a child contract with proper budget allocation.

    Uses ConservationEnforcer to ensure the child contract
    respects parent budget constraints.

    Args:
        parent: Parent contract
        mode: Mode for child contract

    Returns:
        New child contract with allocated budget
    """
    enforcer = ConservationEnforcer(parent)
    child = enforcer.create_child_contract(mode=mode)
    return child


def allocate_batch_contracts(
    parent: AgentContract,
    num_children: int,
    mode: ContractMode = ContractMode.BALANCED
) -> List[AgentContract]:
    """
    Allocate multiple child contracts for parallel execution.

    Args:
        parent: Parent contract
        num_children: Number of child contracts to create
        mode: Mode for child contracts

    Returns:
        List of child contracts with allocated budgets
    """
    enforcer = ConservationEnforcer(parent)
    children = []

    for _ in range(num_children):
        child = enforcer.create_child_contract(mode=mode)
        children.append(child)

    return children


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_agent_profile(agent: str) -> Dict[str, str]:
    """Get performance profile for an agent."""
    return AGENT_PROFILES.get(agent, {})


def print_selection_stats(selector: ResourceAwareSelector):
    """Print agent selection statistics."""
    stats = selector.get_selection_stats()

    if not stats:
        print("No selection statistics available.")
        return

    print("\n=== Agent Selection Statistics ===\n")
    for agent, data in stats.items():
        print(f"  {agent}:")
        print(f"    Selections: {data['count']}")
        print(f"    By reason:")
        for reason, count in data["by_reason"].items():
            print(f"      {reason}: {count}")


if __name__ == "__main__":
    # Demo: resource-aware selection
    print("=== Resource-Aware Selection Demo ===\n")

    from ..contracts import ContractFactory

    # Create test contract
    contract = ContractFactory.default(mode=ContractMode.BALANCED)
    contract.activate()

    # Simulate some resource usage
    contract.consume_resource(ResourceDimension.TOKENS, 60000)
    contract.consume_resource(ResourceDimension.ITERATIONS, 5)

    # Test selection
    selector = ResourceAwareSelector(contract)

    test_tasks = [
        "Implement authentication system",
        "Design database schema",
        "Audit for security issues",
    ]

    available = ["qwen", "gemini", "crush", "claude"]

    print(f"Contract utilization: {contract.get_max_utilization()*100:.0f}%")
    print("Agent selection with resource awareness:\n")

    for task in test_tasks:
        agent, reasoning = selector.select_agent(task, available)
        print(f"  Task: {task[:50]}...")
        print(f"    → {agent:8} | {reasoning}")
        print()
