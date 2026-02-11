#!/usr/bin/env python3
"""
Agent Contracts Framework for Resource-Bounded Autonomous AI Systems

Based on: "Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems"
arXiv:2601.08815 (January 2025) by Ye & Tan

This module implements formal contracts with:
- Multi-dimensional resource constraints (tokens, API calls, iterations, time, cost)
- Conservation laws for hierarchical coordination
- Contract modes: URGENT, ECONOMICAL, BALANCED
- Runtime monitoring and enforcement

Contract Specification: C = (I, O, S, R, T, Φ, Ψ)
- I: Input specification (schema, validation, preprocessing)
- O: Output specification (schema, quality threshold, formatting)
- S: Skill set (tools, functions, knowledge domains)
- R: Resource constraints (multi-dimensional budget)
- T: Temporal constraints (start time, duration/TTL)
- Φ: Success criteria (measurable conditions with weights)
- Ψ: Termination conditions (resource exhaustion, expiration, cancellation)
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# CONTRACT MODES
# ============================================================================

class ContractMode(Enum):
    """
    Contract modes operationalize Simon's satisficing principle.
    Based on empirical results showing quality-resource tradeoffs.
    """
    URGENT = "urgent"      # No extended reasoning, 30s timeout, ~70% success
    ECONOMICAL = "economical"  # Low reasoning effort, 60s timeout, ~76% success
    BALANCED = "balanced"  # Medium reasoning effort, 90s timeout, ~86% success


# ============================================================================
# RESOURCE DIMENSIONS
# ============================================================================

class ResourceDimension(Enum):
    """
    Standard resource dimensions for tracking agent consumption.
    """
    TOKENS = "tokens"           # LLM tokens consumed
    API_CALLS = "api_calls"     # External API invocations
    ITERATIONS = "iterations"   # Loop/round iterations
    WEB_SEARCHES = "web_searches"  # Search queries
    COMPUTE_TIME = "compute_time"    # CPU/execution time (seconds)
    EXTERNAL_COST = "external_cost"  # Monetary cost (USD)


# ============================================================================
# CONTRACT STATE LIFECYCLE
# ============================================================================

class ContractState(Enum):
    """
    Contract lifecycle states following the transition pattern:
    DRAFTED → ACTIVE → {FULFILLED, VIOLATED, EXPIRED, TERMINATED}
    """
    DRAFTED = "drafted"       # Parameters specified, execution not begun
    ACTIVE = "active"         # Resources reserved, monitoring in progress
    FULFILLED = "fulfilled"   # Success criteria met within constraints
    VIOLATED = "violated"     # Resource/temporal constraint breached
    EXPIRED = "expired"       # Duration/TTL exceeded
    TERMINATED = "terminated"  # External cancellation


# ============================================================================
# CONTRACT SPECIFICATION COMPONENTS
# ============================================================================

@dataclass
class InputSpecification:
    """
    Input specification I = (σI, 𝒱I, 𝒫I)

    - σI: Input schema defining acceptable inputs
    - 𝒱I: Validation rules
    - 𝒫I: Preprocessing transformations
    """
    schema: Dict[str, type] = field(default_factory=dict)
    validation_rules: List[Callable] = field(default_factory=list)
    preprocessing_steps: List[Callable] = field(default_factory=list)

    def validate(self, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate inputs against schema and rules.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Schema validation
        for key, expected_type in self.schema.items():
            if key not in inputs:
                errors.append(f"Missing required input: {key}")
            elif not isinstance(inputs[key], expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type}")

        # Custom validation rules
        for rule in self.validation_rules:
            try:
                result = rule(inputs)
                if result is not True:
                    errors.append(str(result))
            except Exception as e:
                errors.append(f"Validation error: {e}")

        return len(errors) == 0, errors


@dataclass
class OutputSpecification:
    """
    Output specification O = (σO, Qmin, ℱO)

    - σO: Output schema
    - Qmin: Minimum acceptable quality threshold
    - ℱO: Formatting requirements
    """
    schema: Dict[str, type] = field(default_factory=dict)
    quality_threshold: float = 0.8  # Qmin: 80% quality by default
    formatting_requirements: List[str] = field(default_factory=list)

    def meets_quality_threshold(self, output: Any, quality_score: float) -> bool:
        """
        Check if output meets minimum quality threshold.

        Args:
            output: The generated output
            quality_score: Computed quality score (0.0 to 1.0)

        Returns:
            True if quality >= Qmin
        """
        return quality_score >= self.quality_threshold


@dataclass
class SkillSet:
    """
    Skill set S = {s1, s2, ..., sm}

    Available capabilities with associated costs and success probabilities.
    """
    skills: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # Format: {skill_name: {"cost": float, "success_prob": float}}

    def get_skill_cost(self, skill: str) -> float:
        """Get the cost of using a specific skill."""
        return self.skills.get(skill, {}).get("cost", 1.0)

    def get_skill_probability(self, skill: str) -> float:
        """Get the success probability of a specific skill."""
        return self.skills.get(skill, {}).get("success_prob", 1.0)

    def has_skill(self, skill: str) -> bool:
        """Check if a skill is available."""
        return skill in self.skills


@dataclass
class ResourceConstraints:
    """
    Resource constraints R = {r1, r2, ..., rn}

    Multi-dimensional budget governing consumption.
    """
    budgets: Dict[ResourceDimension, float] = field(default_factory=dict)

    def get_budget(self, resource: ResourceDimension) -> float:
        """Get the budget for a specific resource."""
        return self.budgets.get(resource, float('inf'))

    def set_budget(self, resource: ResourceDimension, budget: float):
        """Set the budget for a specific resource."""
        self.budgets[resource] = budget

    def validate_consumption(self, consumption: Dict[ResourceDimension, float]) -> Tuple[bool, List[str]]:
        """
        Validate that consumption doesn't exceed budgets.

        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        for resource, consumed in consumption.items():
            budget = self.get_budget(resource)
            if consumed > budget:
                violations.append(f"{resource.value}: {consumed} > {budget}")

        return len(violations) == 0, violations


@dataclass
class TemporalConstraints:
    """
    Temporal constraints T = (t_start, τ)

    - t_start: Contract activation timestamp
    - τ: Contract duration (time-to-live)
    """
    start_time: float = field(default_factory=time.time)
    duration: float = 300.0  # Default 5 minutes

    def is_expired(self) -> bool:
        """Check if the contract has expired based on duration."""
        elapsed = time.time() - self.start_time
        return elapsed > self.duration

    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)

    def get_deadline(self) -> float:
        """Get the absolute deadline timestamp."""
        return self.start_time + self.duration


@dataclass
class SuccessCriteria:
    """
    Success criteria Φ = {(φ1, w1), (φ2, w2), ..., (φk, wk)}

    Measurable conditions paired with weights.
    Contract is fulfilled when Σ wi·𝟙[φi] ≥ θ
    """
    criteria: List[Tuple[Callable, float]] = field(default_factory=list)
    threshold: float = 0.8  # θ: threshold for fulfillment

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Evaluate success criteria against context.

        Returns:
            (is_fulfilled, weighted_score)
        """
        if not self.criteria:
            return True, 1.0

        weighted_sum = 0.0
        for criterion, weight in self.criteria:
            try:
                met = float(criterion(context))  # Convert bool to float if needed
                weighted_sum += weight * met
            except Exception:
                pass  # Failed criteria don't contribute

        return weighted_sum >= self.threshold, weighted_sum


@dataclass
class TerminationConditions:
    """
    Termination conditions Ψ = {ψ1 ∨ ψ2 ∨ ... ∨ ψl}

    Events that end the contract regardless of success.
    """
    conditions: List[Callable] = field(default_factory=list)

    def should_terminate(self, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if any termination condition is met.

        Returns:
            (should_terminate, reason)
        """
        for condition in self.conditions:
            try:
                result = condition(context)
                if result:
                    return True, str(condition)
            except Exception:
                pass
        return False, None


# ============================================================================
# AGENT CONTRACT - MAIN CLASS
# ============================================================================

class AgentContract:
    """
    Agent Contract C = (I, O, S, R, T, Φ, Ψ)

    A formal framework that extends the contract metaphor from task allocation
    to resource-bounded execution. Unifies input/output specifications, multi-
    dimensional resource constraints, temporal boundaries, and success criteria
    into a coherent governance mechanism with explicit lifecycle semantics.

    Based on empirical validation showing:
    - 90% token reduction in iterative workflows
    - Zero conservation violations in multi-agent delegation
    - 525× lower variance in resource consumption
    """

    def __init__(
        self,
        inputs: Optional[InputSpecification] = None,
        outputs: Optional[OutputSpecification] = None,
        skills: Optional[SkillSet] = None,
        resources: Optional[ResourceConstraints] = None,
        temporal: Optional[TemporalConstraints] = None,
        success_criteria: Optional[SuccessCriteria] = None,
        termination: Optional[TerminationConditions] = None,
        mode: ContractMode = ContractMode.BALANCED,
        parent_contract: Optional['AgentContract'] = None
    ):
        self.I = inputs or InputSpecification()
        self.O = outputs or OutputSpecification()
        self.S = skills or SkillSet()
        self.R = resources or ResourceConstraints()
        self.T = temporal or TemporalConstraints()
        self.Phi = success_criteria or SuccessCriteria()
        self.Psi = termination or TerminationConditions()

        self.mode = mode
        self.parent = parent_contract
        self.state = ContractState.DRAFTED

        # Resource tracking
        self._resource_consumption: Dict[ResourceDimension, float] = {}
        for r in ResourceDimension:
            self._resource_consumption[r] = 0.0

        self._lock = threading.Lock()  # Thread-safe resource tracking
        self._state_history: List[Tuple[float, ContractState]] = []

        # Apply mode-specific defaults
        self._apply_mode_defaults()

    def _apply_mode_defaults(self):
        """Apply default constraints based on contract mode."""
        if self.mode == ContractMode.URGENT:
            self.T.duration = 30.0
            self.R.set_budget(ResourceDimension.TOKENS, 50000)
            self.R.set_budget(ResourceDimension.ITERATIONS, 3)
        elif self.mode == ContractMode.ECONOMICAL:
            self.T.duration = 60.0
            self.R.set_budget(ResourceDimension.TOKENS, 75000)
            self.R.set_budget(ResourceDimension.ITERATIONS, 6)
        elif self.mode == ContractMode.BALANCED:
            self.T.duration = 90.0
            self.R.set_budget(ResourceDimension.TOKENS, 100000)
            self.R.set_budget(ResourceDimension.ITERATIONS, 10)

    def activate(self) -> bool:
        """
        Transition contract from DRAFTED to ACTIVE state.

        Returns:
            True if activation successful
        """
        if self.state != ContractState.DRAFTED:
            return False

        # Check conservation law against parent if exists
        if self.parent:
            if not self.parent.check_conservation(self.R.budgets):
                return False

        self._set_state(ContractState.ACTIVE)
        self.T.start_time = time.time()
        return True

    def _set_state(self, new_state: ContractState):
        """Thread-safe state transition with history tracking."""
        with self._lock:
            self.state = new_state
            self._state_history.append((time.time(), new_state))

    def consume_resource(self, resource: ResourceDimension, amount: float) -> bool:
        """
        Consume a specified amount of a resource.

        Args:
            resource: The resource dimension to consume
            amount: Amount to consume

        Returns:
            True if consumption within budget, False otherwise
        """
        with self._lock:
            if self.state != ContractState.ACTIVE:
                return False

            current = self._resource_consumption.get(resource, 0.0)
            budget = self.R.get_budget(resource)

            if current + amount > budget:
                self._set_state(ContractState.VIOLATED)
                return False

            self._resource_consumption[resource] = current + amount
            return True

    def get_consumption(self, resource: ResourceDimension) -> float:
        """Get current consumption for a resource."""
        return self._resource_consumption.get(resource, 0.0)

    def get_utilization(self, resource: ResourceDimension) -> float:
        """
        Get utilization ratio (consumed / budget) for a resource.

        Returns:
            Utilization as a float between 0.0 and 1.0+
        """
        budget = self.R.get_budget(resource)
        if budget == float('inf'):
            return 0.0
        return self.get_consumption(resource) / budget

    def get_utilization_vector(self) -> Dict[ResourceDimension, float]:
        """Get utilization vector for all resources."""
        return {
            r: self.get_utilization(r)
            for r in ResourceDimension
            if self.R.get_budget(r) != float('inf')
        }

    def get_max_utilization(self) -> float:
        """
        Get the maximum utilization across all constrained resources.

        This single metric summarizes how close the agent is to any constraint boundary.
        """
        utilizations = list(self.get_utilization_vector().values())
        return max(utilizations) if utilizations else 0.0

    def check_conservation(self, child_budgets: Dict[ResourceDimension, float]) -> bool:
        """
        Verify conservation law: Σ child budgets ≤ parent budgets.

        Ensures delegated budgets respect parent constraints for hierarchical coordination.

        Args:
            child_budgets: Budget allocation for child contract

        Returns:
            True if conservation law satisfied
        """
        if not self.parent:
            return True

        for resource, child_budget in child_budgets.items():
            parent_budget = self.parent.R.get_budget(resource)
            if parent_budget == float('inf'):
                continue
            if child_budget > parent_budget:
                return False

        return True

    def is_violated(self) -> bool:
        """Check if any resource constraint has been violated."""
        return self.state == ContractState.VIOLATED

    def is_expired(self) -> bool:
        """Check if contract has expired due to temporal constraint."""
        return self.T.is_expired() or self.state == ContractState.EXPIRED

    def can_proceed(self) -> Tuple[bool, str]:
        """
        Comprehensive check if agent can proceed with next action.

        Returns:
            (can_proceed, reason)
        """
        if self.state != ContractState.ACTIVE:
            return False, f"Contract not active (state: {self.state.value})"

        if self.is_expired():
            self._set_state(ContractState.EXPIRED)
            return False, "Contract expired (time limit exceeded)"

        # Check resource budgets
        for resource, budget in self.R.budgets.items():
            if budget != float('inf'):
                consumed = self.get_consumption(resource)
                if consumed >= budget:
                    self._set_state(ContractState.VIOLATED)
                    return False, f"Resource {resource.value} exhausted"

        # Check termination conditions
        context = self._build_context()
        should_terminate, reason = self.Psi.should_terminate(context)
        if should_terminate:
            self._set_state(ContractState.TERMINATED)
            return False, f"Termination condition met: {reason}"

        return True, "OK"

    def _build_context(self) -> Dict[str, Any]:
        """Build context dictionary for evaluating criteria."""
        return {
            "consumption": self._resource_consumption.copy(),
            "utilization": self.get_utilization_vector(),
            "max_utilization": self.get_max_utilization(),
            "elapsed": time.time() - self.T.start_time,
            "state": self.state,
        }

    def evaluate_success(self, output: Any, quality_score: float = 1.0) -> Tuple[bool, float]:
        """
        Evaluate if contract is fulfilled based on success criteria.

        Args:
            output: The generated output
            quality_score: Quality score of the output (0.0 to 1.0)

        Returns:
            (is_fulfilled, score)
        """
        context = self._build_context()
        context["output"] = output
        context["quality_score"] = quality_score

        # Check output quality threshold
        if not self.O.meets_quality_threshold(output, quality_score):
            return False, 0.0

        # Evaluate success criteria
        is_fulfilled, score = self.Phi.evaluate(context)

        if is_fulfilled:
            self._set_state(ContractState.FULFILLED)

        return is_fulfilled, score

    def terminate(self, reason: str = "external"):
        """
        Externally terminate the contract.

        Args:
            reason: Reason for termination
        """
        self._set_state(ContractState.TERMINATED)

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive contract status for monitoring.

        Returns:
            Status dictionary with all contract parameters and current state
        """
        return {
            "state": self.state.value,
            "mode": self.mode.value,
            "consumption": {r.value: self.get_consumption(r) for r in ResourceDimension},
            "utilization": {r.value: self.get_utilization(r) for r in ResourceDimension},
            "max_utilization": self.get_max_utilization(),
            "time_remaining": self.T.time_remaining(),
            "budgets": {r.value: self.R.get_budget(r) for r in ResourceDimension},
            "is_expired": self.is_expired(),
            "is_violated": self.is_violated(),
        }


# ============================================================================
# BUDGET-AWARE PROMPTING
# ============================================================================

def build_budget_aware_prompt(
    base_prompt: str,
    contract: AgentContract
) -> str:
    """
    Inject budget awareness into agent prompts.

    Based on research showing budget-aware prompting with dynamic status updates
    enables agents to self-regulate, producing concise outputs when budget is tight
    or taking exploratory actions when resources are ample.

    Args:
        base_prompt: The original agent prompt
        contract: The active contract

    Returns:
        Enhanced prompt with budget information
    """
    status = contract.get_status()

    budget_info = f"""
## RESOURCE BUDGET (Contract Mode: {contract.mode.value.upper()})

You are operating under a resource contract with the following constraints:

"""

    for resource, utilization in status["utilization"].items():
        budget = status["budgets"].get(resource, float('inf'))
        if budget != float('inf'):
            consumed = status["consumption"][resource]
            budget_info += f"- {resource.upper()}: {consumed:.0f} / {budget:.0f} ({utilization*100:.1f}%)\n"

    budget_info += f"""
Time Remaining: {status['time_remaining']:.0f} seconds
Overall Utilization: {status['max_utilization']*100:.1f}%

## BUDGET AWARENESS INSTRUCTIONS

- Monitor your resource consumption carefully
- When utilization is high (>80%), be concise and efficient
- Stop and report completion if running low on budget
- Do NOT exceed the specified resource limits
"""

    return budget_info + "\n" + base_prompt


# ============================================================================
# CONTRACT FACTORY
# ============================================================================

class ContractFactory:
    """
    Factory for creating pre-configured contracts based on common scenarios.
    """

    @staticmethod
    def default(mode: ContractMode = ContractMode.BALANCED) -> AgentContract:
        """Create a default contract with standard constraints."""
        return AgentContract(mode=mode)

    @staticmethod
    def code_review(
        max_iterations: int = 5,
        token_budget: int = 50000
    ) -> AgentContract:
        """Create a contract optimized for code review tasks."""
        contract = AgentContract(mode=ContractMode.BALANCED)
        contract.R.set_budget(ResourceDimension.ITERATIONS, max_iterations)
        contract.R.set_budget(ResourceDimension.TOKENS, token_budget)
        return contract

    @staticmethod
    def research_pipeline(
        web_search_limit: int = 10,
        time_limit_seconds: int = 300
    ) -> AgentContract:
        """Create a contract optimized for research tasks."""
        contract = AgentContract(mode=ContractMode.ECONOMICAL)
        contract.R.set_budget(ResourceDimension.WEB_SEARCHES, web_search_limit)
        contract.T.duration = time_limit_seconds
        return contract

    @staticmethod
    def rapid_prototype(
        time_limit_seconds: int = 30
    ) -> AgentContract:
        """Create a contract for rapid prototyping (urgent mode)."""
        return AgentContract(mode=ContractMode.URGENT)


# ============================================================================
# CONSERVATION LAW ENFORCEMENT
# ============================================================================

class ConservationEnforcer:
    """
    Enforces conservation laws for multi-agent coordination.

    Ensures that Σ c(r)j ≤ B(r) ∀ r ∈ R across all agents.
    """

    def __init__(self, root_contract: AgentContract):
        """
        Initialize with root (parent) contract.

        Args:
            root_contract: The top-level contract with total budgets
        """
        self.root = root_contract
        self.child_contracts: List[AgentContract] = []
        self._lock = threading.Lock()

    def allocate_child_budget(
        self,
        allocation_strategy: str = "equal",
        reserve_buffer: float = 0.15
    ) -> Dict[ResourceDimension, float]:
        """
        Allocate budget to a child contract using specified strategy.

        Args:
            allocation_strategy: "equal", "proportional", or "negotiated"
            reserve_buffer: Percentage to reserve for coordination overhead (0.0-1.0)

        Returns:
            Allocated budget dictionary
        """
        total_budget = {}

        for resource in ResourceDimension:
            parent_budget = self.root.R.get_budget(resource)
            if parent_budget == float('inf'):
                total_budget[resource] = float('inf')
                continue

            # Reserve buffer for coordination overhead
            reserved = parent_budget * reserve_buffer
            available = parent_budget - reserved

            if allocation_strategy == "equal":
                # Divide equally among potential children
                n_children = max(1, len(self.child_contracts) + 1)
                total_budget[resource] = available / n_children

            elif allocation_strategy == "proportional":
                # Would need task complexity weights - simplify to equal for now
                n_children = max(1, len(self.child_contracts) + 1)
                total_budget[resource] = available / n_children

            else:  # negotiated
                # For now, use equal as fallback
                n_children = max(1, len(self.child_contracts) + 1)
                total_budget[resource] = available / n_children

        return total_budget

    def create_child_contract(
        self,
        mode: ContractMode = ContractMode.BALANCED
    ) -> AgentContract:
        """
        Create a child contract with budget respecting conservation laws.

        Args:
            mode: Contract mode for the child

        Returns:
            New child contract with allocated budget
        """
        allocated = self.allocate_child_budget()

        child = AgentContract(
            mode=mode,
            parent=self.root
        )

        # Apply allocated budgets
        for resource, budget in allocated.items():
            if budget != float('inf'):
                child.R.set_budget(resource, budget)

        with self._lock:
            self.child_contracts.append(child)

        return child

    def verify_conservation(self) -> bool:
        """
        Verify that all child contracts respect conservation laws.

        Returns:
            True if conservation satisfied across all children
        """
        total_consumption = {r: 0.0 for r in ResourceDimension}

        # Sum consumption from all children
        for child in self.child_contracts:
            for resource in ResourceDimension:
                total_consumption[resource] += child.get_consumption(resource)

        # Add root's own consumption
        for resource in ResourceDimension:
            total_consumption[resource] += self.root.get_consumption(resource)

        # Verify against root budgets
        for resource, total in total_consumption.items():
            budget = self.root.R.get_budget(resource)
            if budget != float('inf') and total > budget:
                return False

        return True


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create a contract and monitor resource usage
    print("=== Agent Contracts Framework Demo ===\n")

    # Create a balanced contract
    contract = ContractFactory.default(mode=ContractMode.BALANCED)

    # Activate the contract
    if contract.activate():
        print(f"✅ Contract activated (mode: {contract.mode.value})")

    # Check if we can proceed
    can_proceed, reason = contract.can_proceed()
    print(f"\nCan proceed: {can_proceed} - {reason}")

    # Simulate resource consumption
    print("\n--- Simulating resource consumption ---")
    contract.consume_resource(ResourceDimension.TOKENS, 25000)
    print(f"Consumed 25K tokens. Utilization: {contract.get_utilization(ResourceDimension.TOKENS)*100:.1f}%")

    contract.consume_resource(ResourceDimension.TOKENS, 25000)
    print(f"Consumed 25K tokens. Utilization: {contract.get_utilization(ResourceDimension.TOKENS)*100:.1f}%")

    # Check status
    print(f"\nMax utilization: {contract.get_max_utilization()*100:.1f}%")
    print(f"Time remaining: {contract.T.time_remaining():.0f}s")

    # Demonstrate conservation law
    print("\n--- Demonstrating conservation laws ---")
    root = ContractFactory.default()
    root.activate()

    enforcer = ConservationEnforcer(root)
    child1 = enforcer.create_child_contract(mode=ContractMode.ECONOMICAL)
    child1.activate()

    print(f"Root token budget: {root.R.get_budget(ResourceDimension.TOKENS)}")
    print(f"Child token budget: {child1.R.get_budget(ResourceDimension.TOKENS)}")
    print(f"Conservation verified: {enforcer.verify_conservation()}")

    # Build budget-aware prompt
    print("\n--- Budget-aware prompt snippet ---")
    prompt = build_budget_aware_prompt("You are a helpful assistant.", contract)
    print(prompt[:500] + "...")
