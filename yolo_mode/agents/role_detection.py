"""
Role Detection - Map tasks to OSA roles and optimal agents.

Enhanced task-to-role mapping with comprehensive keyword detection,
scoring algorithms, and agent selection logic.
"""

from typing import Dict, List, Tuple, Optional
from .registry import OSARole, AGENT_REGISTRY, get_agent_for_role, AgentCapability


# ============================================================================
# ROLE KEYWORD DEFINITIONS
# ============================================================================

# Extended role keywords with comprehensive coverage
ROLE_KEYWORDS: Dict[OSARole, List[str]] = {
    OSARole.ORCHESTRATOR: [
        # Planning and coordination
        "plan", "orchestrate", "coordinate", "manage", "organize",
        "design workflow", "review plan", "breakdown", "decompose",
        "schedule", "coordinate tasks", "project management",
        "roadmap", "timeline", "milestone", "workflow",
        "prioritize", "sequence", "order", "arrange",
        # Meta-coordination
        "supervise", "oversee", "direct", "lead",
        "assign", "delegate", "distribute", "allocate",
    ],

    OSARole.ARCHITECT: [
        # Design and structure
        "architecture", "schema", "design", "structure", "pattern",
        "interface", "api design", "database design", "system design",
        "design pattern", "module structure", "component design",
        # High-level planning
        "blueprint", "specification", "framework", "scaffold",
        # Technical decisions
        "choose technology", "select stack", "tech stack", "approach",
        # Data and storage
        "data model", "storage", "schema", "entity relationship",
    ],

    OSARole.CODER: [
        # Implementation keywords
        "implement", "write", "code", "create", "build",
        "function", "class", "module", "script", "refactor",
        "add feature", "implement feature", "write code",
        # Development tasks
        "develop", "program", "script", "algorithm",
        "logic", "handler", "controller", "service",
        # Code modification
        "update", "modify", "extend", "change", "fix",
        "optimize", "improve", "enhance",
        # Files and artifacts
        "create file", "add file", "generate", "produce",
    ],

    OSARole.SECURITY: [
        # Security analysis
        "security", "audit", "vulnerability", "threat", "risk",
        "sanitize", "validate input", "clean", "filter",
        # Authentication/authorization
        "authenticate", "authorize", "permission", "access control",
        "encrypt", "hash", "protect", "secure",
        # Specific security concerns
        "injection", "xss", "csrf", "exploit", "attack",
        "zero trust", "secret", "credential", "token",
        # Compliance and standards
        "owasp", "compliance", "standard", "policy",
    ],

    OSARole.QA: [
        # Testing keywords
        "test", "verify", "check", "validate", "debug",
        "edge case", "coverage", "benchmark", "inspect",
        "unit test", "integration test", "test suite",
        "spec", "assertion", "mock", "stub",
        # Quality tasks
        "review", "analyze", "examine", "evaluate",
        "measure", "profile", "trace",
        # Bug finding
        "bug", "issue", "problem", "error", "defect",
        "find bug", "fix bug", "debug", "troubleshoot",
    ],
}


# Capability-to-role mapping for specialized routing
CAPABILITY_ROLE_MAP: Dict[AgentCapability, OSARole] = {
    AgentCapability.CODE_GENERATION: OSARole.CODER,
    AgentCapability.REFACTORING: OSARole.CODER,
    AgentCapability.TESTING: OSARole.QA,
    AgentCapability.ARCHITECTURE_DESIGN: OSARole.ARCHITECT,
    AgentCapability.PLANNING: OSARole.ORCHESTRATOR,
    AgentCapability.ORCHESTRATION: OSARole.ORCHESTRATOR,
    AgentCapability.SECURITY_AUDIT: OSARole.SECURITY,
    AgentCapability.CODE_REVIEW: OSARole.QA,
    AgentCapability.DOCUMENTATION: OSARole.CODER,
    AgentCapability.CONTEXT_MANAGEMENT: OSARole.ORCHESTRATOR,
    AgentCapability.VALIDATION: OSARole.QA,
}


# Task complexity indicators
COMPLEXITY_KEYWORDS = {
    "high": ["architecture", "system", "framework", "complete", "full", "entire"],
    "medium": ["module", "component", "feature", "section", "part"],
    "low": ["fix", "small", "simple", "minor", "quick"],
}


# ============================================================================
# ROLE DETECTION FUNCTIONS
# ============================================================================

def detect_role(task_description: str) -> OSARole:
    """
    Detect the appropriate OSA role for a task.

    Uses keyword scoring with tie-breaking logic:
    1. Score each role by keyword matches
    2. Use keyword weights (some keywords are more significant)
    3. Apply tie-breaking rules

    Args:
        task_description: The task text to analyze

    Returns:
        The detected OSA role
    """
    task_lower = task_description.lower()

    # Score each role by keyword matches
    role_scores: Dict[OSARole, float] = {}
    role_matches: Dict[OSARole, List[str]] = {}

    for role, keywords in ROLE_KEYWORDS.items():
        matches = []
        score = 0.0

        for keyword in keywords:
            if keyword in task_lower:
                matches.append(keyword)
                # Weight multi-word matches higher
                weight = len(keyword.split()) * 1.5
                score += weight

        if matches:
            role_scores[role] = score
            role_matches[role] = matches

    if not role_scores:
        return OSARole.CODER  # Default fallback

    # Get highest scoring role
    detected_role = max(role_scores, key=role_scores.get)

    return detected_role


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


def detect_role_with_confidence(
    task_description: str
) -> Tuple[OSARole, float]:
    """
    Detect role with confidence score.

    Args:
        task_description: The task text to analyze

    Returns:
        Tuple of (OSA role, confidence score 0-1)
    """
    task_lower = task_description.lower()

    role_scores: Dict[OSARole, float] = {}
    total_keywords = 0

    for role, keywords in ROLE_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in task_lower)
        if matches > 0:
            role_scores[role] = matches
            total_keywords += matches

    if not role_scores:
        return OSARole.CODER, 0.0

    # Calculate confidence as ratio of top score to total
    max_score = max(role_scores.values())
    confidence = max_score / total_keywords if total_keywords > 0 else 0.0

    detected_role = max(role_scores, key=role_scores.get)
    return detected_role, min(confidence, 1.0)


def detect_capability(task_description: str) -> Optional[AgentCapability]:
    """
    Detect the primary capability needed for a task.

    Args:
        task_description: The task text to analyze

    Returns:
        The most relevant AgentCapability, or None
    """
    task_lower = task_description.lower()

    # Map task keywords to capabilities
    capability_keywords = {
        AgentCapability.CODE_GENERATION: ["implement", "write", "create", "build", "function"],
        AgentCapability.REFACTORING: ["refactor", "clean up", "improve", "optimize", "restructure"],
        AgentCapability.TESTING: ["test", "spec", "coverage", "pytest", "verify"],
        AgentCapability.ARCHITECTURE_DESIGN: ["architecture", "design", "schema", "structure", "pattern"],
        AgentCapability.PLANNING: ["plan", "roadmap", "schedule", "breakdown", "decompose"],
        AgentCapability.SECURITY_AUDIT: ["security", "audit", "vulnerability", "sanitize"],
        AgentCapability.CODE_REVIEW: ["review", "check", "inspect", "analyze code"],
    }

    best_capability = None
    best_score = 0

    for capability, keywords in capability_keywords.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > best_score:
            best_score = score
            best_capability = capability

    return best_capability


def detect_task_complexity(task_description: str) -> str:
    """
    Detect the complexity level of a task.

    Args:
        task_description: The task text

    Returns:
        "high", "medium", or "low"
    """
    task_lower = task_description.lower()

    # Check for complexity indicators
    high_score = sum(1 for kw in COMPLEXITY_KEYWORDS["high"] if kw in task_lower)
    medium_score = sum(1 for kw in COMPLEXITY_KEYWORDS["medium"] if kw in task_lower)
    low_score = sum(1 for kw in COMPLEXITY_KEYWORDS["low"] if kw in task_lower)

    if high_score > 0:
        return "high"
    elif medium_score > 0:
        return "medium"
    elif low_score > 0:
        return "low"
    else:
        return "medium"  # Default


# ============================================================================
# AGENT SELECTION WITH CONTEXT
# ============================================================================

def select_agent_by_context(
    task: str,
    available_agents: List[str],
    context: Optional[Dict] = None
) -> Tuple[OSARole, str, str]:
    """
    Select agent based on task and additional context.

    Context can include:
    - resource_budget: Remaining resource budget
    - time_constraint: Time available for task
    - quality_requirement: Quality level needed
    - cost_constraint: Cost sensitivity

    Args:
        task: Task description
        available_agents: Available agent names
        context: Additional context for selection

    Returns:
        Tuple of (role, agent, reasoning)
    """
    role, agent = detect_role_and_agent(task, available_agents)
    reasoning = f"Role: {role.value}"

    if context:
        # Apply context-aware overrides
        if context.get("resource_budget", 1.0) < 0.3:
            # Low budget: prefer efficient agents
            if "qwen" in available_agents and agent != "qwen":
                agent = "qwen"
                reasoning += " → Budget override: qwen (efficient)"
            elif "crush" in available_agents:
                agent = "crush"
                reasoning += " → Budget override: crush (efficient)"

        if context.get("time_constraint", 300) < 60:
            # Tight deadline: prefer fast agents
            if "qwen" in available_agents and agent != "qwen":
                agent = "qwen"
                reasoning += " → Time override: qwen (fast)"

        if context.get("quality_requirement") == "highest":
            # High quality: prefer best agents
            if "claude" in available_agents and agent not in ["claude", "gemini"]:
                agent = "claude"
                reasoning += " → Quality override: claude (highest quality)"
            elif "gemini" in available_agents:
                agent = "gemini"
                reasoning += " → Quality override: gemini (high quality)"

    return role, agent, reasoning


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def detect_roles_for_batch(tasks: List[str]) -> List[Tuple[str, OSARole, str]]:
    """
    Detect roles for multiple tasks efficiently.

    Args:
        tasks: List of task descriptions

    Returns:
        List of (task, role, recommended_agent) tuples
    """
    results = []
    for task in tasks:
        role, agent = detect_role_and_agent(task)
        results.append((task, role, agent))
    return results


def group_tasks_by_role(
    tasks: List[str]
) -> Dict[OSARole, List[str]]:
    """
    Group tasks by their detected roles.

    Useful for parallel execution planning.

    Args:
        tasks: List of task descriptions

    Returns:
        Dictionary mapping roles to task lists
    """
    grouped: Dict[OSARole, List[str]] = {role: [] for role in OSARole}

    for task in tasks:
        role = detect_role(task)
        grouped[role].append(task)

    return grouped


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_role_prompt(role: OSARole) -> str:
    """Get the system prompt for a role."""
    prompts = {
        OSARole.ORCHESTRATOR: """You are the ORCHESTRATOR role in the OSA Framework.

Your responsibilities:
- Planning and task decomposition
- Progress tracking and coordination
- Ensuring tasks are properly ordered
- Managing dependencies between tasks

Approach: Think systematically, break down complex goals into clear steps.""",

        OSARole.ARCHITECT: """You are the ARCHITECT role in the OSA Framework.

Your responsibilities:
- System design and architecture
- Finding and applying patterns
- Defining structures and interfaces
- Ensuring scalability and maintainability

Approach: Think in terms of SOLID principles, DRY, KISS, YAGNI.
Consider the bigger picture and long-term implications.""",

        OSARole.CODER: """You are the CODER role in the OSA Framework.

Your responsibilities:
- Implementation of designed solutions
- Writing clean, maintainable code
- Following coding standards (SOLID, DRY, KISS)
- Making focused, minimal changes

Approach: Write production-ready code that matches existing style.
Prioritize clarity and correctness over cleverness.""",

        OSARole.SECURITY: """You are the SECURITY role in the OSA Framework.

Your responsibilities:
- Zero Trust validation of all inputs
- Ensuring proper authentication/authorization
- Identifying security vulnerabilities
- Secret management and encryption

Approach: Verify everything. Sanitize all inputs.
Apply principle of least privilege. Consider OWASP Top 10.""",

        OSARole.QA: """You are the QA role in the OSA Framework.

Your responsibilities:
- Verification of completed work
- Testing and edge-case analysis
- Quality assurance and validation
- Finding bugs and issues

Approach: Be thorough and methodical.
Test edge cases. Verify assumptions. Document any issues found.""",
    }
    return prompts.get(role, "")


def print_detection_result(task: str, role: OSARole, agent: str, confidence: float = None):
    """Print formatted detection result."""
    conf_str = f" ({confidence*100:.0f}% confidence)" if confidence is not None else ""
    print(f"  Task: {task[:60]}...")
    print(f"    → Role: {role.value:12} | Agent: {agent:8}{conf_str}")


if __name__ == "__main__":
    # Demo: test role detection
    print("=== Role Detection Demo ===\n")

    test_tasks = [
        "Implement a user authentication system",
        "Design the database schema for the application",
        "Plan the implementation roadmap for Q1",
        "Audit the code for SQL injection vulnerabilities",
        "Write unit tests for the payment module",
        "Refactor the user service to use async/await",
    ]

    for task in test_tasks:
        role, agent = detect_role_and_agent(task)
        role_c, confidence = detect_role_with_confidence(task)
        complexity = detect_task_complexity(task)
        print_detection_result(task, role, agent, confidence)
        print(f"       Complexity: {complexity}")
        print()
