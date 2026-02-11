# CLI Agent Integration Research Report

**Date:** 2026-02-11
**Research Focus:** Qwen CLI, Gemini CLI, and Crush CLI Integration with OSA Framework

---

## Executive Summary

This report provides a comprehensive analysis of three leading CLI-based agentic coding tools and their potential integration as subagents within the YOLO Mode OSA Framework. Each tool offers unique capabilities that complement different OSA roles and use cases.

### Tools Analyzed

| Tool | Organization | Open Source | Key Strength | Best OSA Role |
|------|-------------|--------------|--------------|----------------|
| **Qwen CLI** | Alibaba/Alibaba Cloud | Yes | Fast coding, long-horizon reasoning | Coder |
| **Gemini CLI** | Google | Yes | Context-driven development, orchestration | Orchestrator |
| **Crush CLI** | Charmbracelet | Yes | Beautiful UI, local tool access, security | Security/Audit |

---

## 1. Qwen CLI (Qwen Code)

### Overview
Qwen CLI is an open-source agentic programming tool adapted from Gemini CLI, specifically enhanced for Qwen-Coder models. It provides a Claude Code-like experience with rich built-in tools including "Skills" and "SubAgents."

### Key Capabilities

1. **Advanced Coding Performance**
   - Qwen3-Coder-Next (Feb 2026) achieves SOTA results in agentic tool use among open-source models
   - Performance comparable to Claude Sonnet 4 in software engineering challenges
   - Excellent for code generation, refactoring, and implementation tasks

2. **Offline Capability**
   - Full offline functionality without internet connectivity
   - Local model execution for privacy-sensitive work
   - Reduced latency for common operations

3. **Terminal-First Design**
   - IDE-integrated agentic workflow
   - Rich tool ecosystem with Skills and SubAgents
   - Seamless integration with existing development workflows

### CLI Interface
```bash
# Basic usage
qwen --yolo "implement a user authentication system"

# With specific model
qwen --model qwen3-coder-next "write tests for this module"

# Offline mode
qwen --offline "refactor this function"
```

### Integration with OSA Framework

#### Recommended Role: **Coder (Primary)**

Qwen CLI is ideal for the **Coder** role due to:
- Fast code generation capabilities
- Strong performance on software engineering benchmarks
- Efficient token usage for implementation tasks
- Good understanding of existing codebases

#### Implementation Requirements

```python
# In yolo_mode/scripts/yolo_loop.py

AGENT_CONFIGS = {
    "qwen": {
        "cli_command": "qwen",
        "yolo_flag": "--yolo",
        "offline_flag": "--offline",
        "model_flag": "--model",
        "preferred_models": ["qwen3-coder-next", "qwen2.5-coder-32b"],
        "capabilities": ["code_generation", "refactoring", "testing", "documentation"],
        "resource_profile": {
            "speed": "fast",
            "cost": "low",  # Open source, can run locally
            "quality": "high",
            "token_efficiency": "high"
        },
        "osa_roles": ["coder", "qa"],
        "strengths": ["implementation", "code_review", "rapid_prototyping"],
        "weaknesses": ["architecture_design", "high_level_orchestration"]
    },
    # ... other agents
}
```

### Installation & Setup
```bash
# Install via GitHub
git clone https://github.com/QwenLM/qwen-code.git
cd qwen-code
pip install -e .

# Or via pip (if available)
pip install qwen-code

# Configure for YOLO mode
export QWEN_YOLO=true
export QWEN_DANGEROUSLY_SKIP_PERMISSIONS=true
```

---

## 2. Gemini CLI

### Overview
Gemini CLI is Google's open-source AI agent that provides access to Gemini directly in the terminal. It was officially announced on June 25, 2025 and has received continuous updates through 2026, including the "Conductor" feature for context-driven development (December 2025).

### Key Capabilities

1. **Context-Driven Development (Conductor)**
   - Advanced context management for large codebases
   - Deep understanding of project structure
   - Intelligent querying and editing capabilities

2. **Multi-Modal Input**
   - Generate apps from images or PDFs
   - Visual understanding for UI-related tasks
   - Screenshot-to-code capabilities

3. **Google Ecosystem Integration**
   - Direct access to Gemini API
   - Integration with Google Cloud services
   - Official support and documentation

### CLI Interface
```bash
# Basic usage
gemini --yolo "design a REST API for user management"

# With context file
gemini --context project.md "add authentication endpoints"

# Multi-modal
gemini --screenshot design.png "implement this UI"
```

### Integration with OSA Framework

#### Recommended Role: **Orchestrator (Primary)**

Gemini CLI excels as the **Orchestrator** due to:
- Strong context management for understanding project-wide requirements
- Excellent at task decomposition and planning
- Good at coordinating between different components
- Strong reasoning for architectural decisions

#### Secondary Role: **Architect**

Also suitable for **Architect** role due to:
- System design capabilities
- Understanding of large codebases
- API and schema design strengths

#### Implementation Requirements

```python
AGENT_CONFIGS["gemini"] = {
    "cli_command": "gemini",
    "yolo_flag": "--yolo",
    "context_flag": "--context",
    "model_flag": "--model",
    "preferred_models": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "capabilities": [
        "planning",
        "architecture_design",
        "code_generation",
        "context_management",
        "multimodal"
    ],
    "resource_profile": {
        "speed": "medium",
        "cost": "medium",  # API-based pricing
        "quality": "very_high",
        "context_window": "very_large"
    },
    "osa_roles": ["orchestrator", "architect"],
    "strengths": [
        "task_decomposition",
        "workflow_coordination",
        "system_design",
        "codebase_understanding"
    ],
    "weaknesses": ["local_execution", "privacy_sensitive_work"]
}
```

### Installation & Setup
```bash
# Install via GitHub
git clone https://github.com/google-gemini/gemini-cli.git
cd gemini-cli
npm install && npm link

# Configure API key
export GEMINI_API_KEY="your-api-key"

# Configure for YOLO mode
export GEMINI_YOLO=true
```

---

## 3. Crush CLI

### Overview
Crush CLI (formerly OpenCode AI) is developed by Charmbracelet and describes itself as "Glamorous agentic coding for all." It is positioned as one of the top 5 CLI coding agents in 2026, with a focus on beautiful UI design, local tool access, and permission-based security.

### Key Capabilities

1. **Beautiful Terminal UI**
   - Glamorous interface design (Charmbracelet signature style)
   - Excellent user experience for interactive sessions
   - Clean, readable output formatting

2. **Local Tool Access**
   - Direct access to git, docker, npm, ghc, sed, nix, and more
   - No API latency for local operations
   - Full control over execution environment

3. **Permission-Based Security**
   - Explicit permission requests for tool usage
   - Clear audit trail of actions
   - Safety-first approach to autonomous execution

4. **MCP Integration**
   - Model Context Protocol support
   - Web MCP integration for real-time data
   - Extensible with custom tools and context sources

### CLI Interface
```bash
# Basic usage
crush run "add error handling to this function"

# With permissions auto-approved
crush run --yolo "refactor the entire codebase"

# With web MCP for real-time data
crush run --with-web-mcp "implement live stock ticker"
```

### Integration with OSA Framework

#### Recommended Role: **Security (Primary)**

Crush CLI is ideal for the **Security** role due to:
- Permission-based execution model aligns with Zero Trust
- Clear audit trails for security reviews
- Conservative approach to code changes
- Strong validation capabilities

#### Secondary Role: **QA**

Also suitable for **QA** role due to:
- Thorough verification approach
- Clear visibility into all operations
- Strong testing capabilities

#### Implementation Requirements

```python
AGENT_CONFIGS["crush"] = {
    "cli_command": "crush",
    "subcommand": "run",
    "yolo_flag": "--yolo",
    "web_mcp_flag": "--with-web-mcp",
    "capabilities": [
        "security_audit",
        "code_review",
        "testing",
        "validation",
        "local_operations"
    ],
    "resource_profile": {
        "speed": "medium",
        "cost": "low",  # Can use local models
        "quality": "high",
        "safety": "very_high"
    },
    "osa_roles": ["security", "qa"],
    "strengths": [
        "security_analysis",
        "vulnerability_detection",
        "code_validation",
        "safe_execution"
    ],
    "weaknesses": ["speed", "rapid_iteration"],
    "permission_model": "explicit",
    "audit_trail": True
}
```

### Installation & Setup
```bash
# Install via Go (if available)
go install github.com/charmbracelet/crush@latest

# Or via package managers
brew install charmbracelet/tap/crush

# Configure for YOLO mode
export CRUSH_YOLO=true
export CRUSH_DANGEROUSLY_SKIP_PERMISSIONS=true
```

---

## 4. Comparative Analysis

### Performance Comparison

| Aspect | Qwen CLI | Gemini CLI | Crush CLI |
|---------|-----------|------------|-----------|
| **Speed** | Fast (local) | Medium (API) | Medium (local) |
| **Cost** | Low (open source) | Medium (API) | Low (open source) |
| **Quality** | High | Very High | High |
| **Privacy** | High (offline) | Medium (cloud) | High (local) |
| **Context Window** | Medium | Very Large | Medium |
| **UI/UX** | Good | Good | Excellent |
| **Tool Access** | Rich | Rich | Extensive |
| **Offline Mode** | Yes | No | Yes |

### OSA Role Assignment Matrix

| Role | Best Agent | Second Best | Rationale |
|------|------------|-------------|-----------|
| **Orchestrator** | Gemini | Claude | Strong context management and planning |
| **Architect** | Gemini | Claude | Excellent system design capabilities |
| **Coder** | Qwen | Claude | Fast, efficient code generation |
| **Security** | Crush | OpenCode | Permission-based, audit trails |
| **QA** | Crush | Claude | Thorough verification approach |

### Task Type Recommendations

| Task Type | Recommended Agent | Reason |
|-----------|------------------|--------|
| Initial planning | Gemini | Best at task decomposition |
| Architecture design | Gemini | Strong system design |
| Implementation | Qwen | Fast coding, efficient |
| Code review | Qwen/Crush | Good at finding issues |
| Security audit | Crush | Permission-based, thorough |
| Testing | Qwen | Fast test generation |
| Refactoring | Qwen | Efficient code modification |
| Documentation | Qwen | Fast doc generation |
| Emergency fixes | Qwen | Speed when needed |
| Complex orchestration | Gemini | Best at coordination |

---

## 5. Enhanced Integration Architecture

### Proposed Agent Registry System

```python
# yolo_mode/agents/registry.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum

class AgentCapability(Enum):
    """Core agent capabilities."""
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
    """OSA Framework roles."""
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    CODER = "coder"
    SECURITY = "security"
    QA = "qa"

@dataclass
class AgentConfig:
    """Configuration for a CLI agent."""
    name: str
    cli_command: str
    yolo_flag: str = "--yolo"
    subcommand: Optional[str] = None
    model_flag: Optional[str] = None
    preferred_models: List[str] = None
    capabilities: Set[AgentCapability] = None
    osa_roles: Set[OSARole] = None
    resource_profile: Dict[str, str] = None
    strengths: List[str] = None
    weaknesses: List[str] = None

    def get_command(self, prompt: str, model: str = None) -> List[str]:
        """Build CLI command for this agent."""
        cmd = [self.cli_command]

        if self.subcommand:
            cmd.append(self.subcommand)

        cmd.append(self.yolo_flag)

        if model and self.model_flag:
            cmd.extend([self.model_flag, model])

        cmd.append(prompt)

        return cmd

# Agent Registry
AGENT_REGISTRY: Dict[str, AgentConfig] = {
    "qwen": AgentConfig(
        name="Qwen CLI",
        cli_command="qwen",
        yolo_flag="--yolo",
        model_flag="--model",
        preferred_models=["qwen3-coder-next", "qwen2.5-coder-32b"],
        capabilities={
            AgentCapability.CODE_GENERATION,
            AgentCapability.REFACTORING,
            AgentCapability.TESTING,
            AgentCapability.DOCUMENTATION,
        },
        osa_roles={OSARole.CODER, OSARole.QA},
        resource_profile={"speed": "fast", "cost": "low", "quality": "high"},
        strengths=["implementation", "speed", "token_efficiency"],
        weaknesses=["architecture_design"],
    ),

    "gemini": AgentConfig(
        name="Gemini CLI",
        cli_command="gemini",
        yolo_flag="--yolo",
        model_flag="--model",
        preferred_models=["gemini-2.5-flash", "gemini-2.5-pro"],
        capabilities={
            AgentCapability.PLANNING,
            AgentCapability.ARCHITECTURE_DESIGN,
            AgentCapability.CODE_GENERATION,
            AgentCapability.CONTEXT_MANAGEMENT,
            AgentCapability.MULTIMODAL,
        },
        osa_roles={OSARole.ORCHESTRATOR, OSARole.ARCHITECT},
        resource_profile={"speed": "medium", "cost": "medium", "quality": "very_high"},
        strengths=["planning", "orchestration", "context_management"],
        weaknesses=["local_execution", "privacy_sensitive"],
    ),

    "crush": AgentConfig(
        name="Crush CLI",
        cli_command="crush",
        subcommand="run",
        yolo_flag="--yolo",
        preferred_models=None,  # Can use various local models
        capabilities={
            AgentCapability.SECURITY_AUDIT,
            AgentCapability.CODE_REVIEW,
            AgentCapability.VALIDATION,
            AgentCapability.TESTING,
        },
        osa_roles={OSARole.SECURITY, OSARole.QA},
        resource_profile={"speed": "medium", "cost": "low", "safety": "very_high"},
        strengths=["security", "audit_trail", "safe_execution"],
        weaknesses=["speed", "rapid_iteration"],
    ),

    "claude": AgentConfig(
        name="Claude Code",
        cli_command="claude",
        yolo_flag="--dangerously-skip-permissions",
        preferred_models=["claude-sonnet-4", "claude-opus-4"],
        capabilities={
            AgentCapability.CODE_GENERATION,
            AgentCapability.ARCHITECTURE_DESIGN,
            AgentCapability.CODE_REVIEW,
            AgentCapability.TESTING,
        },
        osa_roles={OSARole.ARCHITECT, OSARole.QA},
        resource_profile={"speed": "medium", "cost": "high", "quality": "very_high"},
        strengths=["reasoning", "code_quality", "comprehensive"],
        weaknesses=["cost", "speed"],
    ),

    "opencode": AgentConfig(
        name="OpenCode",
        cli_command="opencode",
        subcommand="run",
        yolo_flag="--yolo",
        preferred_models=None,
        capabilities={
            AgentCapability.SECURITY_AUDIT,
            AgentCapability.VALIDATION,
            AgentCapability.CODE_REVIEW,
        },
        osa_roles={OSARole.SECURITY},
        resource_profile={"speed": "medium", "cost": "low", "safety": "high"},
        strengths=["schema_validation", "security"],
        weaknesses=["planning", "architecture"],
    ),
}

def get_agent_for_role(role: OSARole, available_agents: List[str] = None) -> str:
    """Get the best agent for a given OSA role."""
    available = available_agents or list(AGENT_REGISTRY.keys())

    # Score agents by capability match
    scored_agents = []
    for agent_name in available:
        agent = AGENT_REGISTRY.get(agent_name)
        if agent and role in agent.osa_roles:
            score = len(agent.capabilities)  # More capabilities = higher score
            scored_agents.append((agent_name, score))

    if not scored_agents:
        # Fallback to first available
        return available[0] if available else "claude"

    scored_agents.sort(key=lambda x: x[1], reverse=True)
    return scored_agents[0][0]

def get_agent_for_capability(capability: AgentCapability, available_agents: List[str] = None) -> str:
    """Get the best agent for a specific capability."""
    available = available_agents or list(AGENT_REGISTRY.keys())

    for agent_name in available:
        agent = AGENT_REGISTRY.get(agent_name)
        if agent and capability in agent.capabilities:
            return agent_name

    return available[0] if available else "claude"
```

### Enhanced Role Detection

```python
# yolo_mode/agents/role_detection.py

from typing import Dict, List, Tuple
from agents.registry import OSARole, AgentCapability

ROLE_KEYWORDS = {
    OSARole.ORCHESTRATOR: [
        "plan", "orchestrate", "coordinate", "manage", "organize",
        "design workflow", "review plan", "coordinate", "decompose",
    ],
    OSARole.ARCHITECT: [
        "architecture", "schema", "design", "structure", "pattern",
        "interface", "api design", "database design", "system design",
    ],
    OSARole.CODER: [
        "implement", "write", "code", "create", "build",
        "function", "class", "module", "script", "refactor",
    ],
    OSARole.SECURITY: [
        "security", "audit", "validate", "sanitize", "authenticate",
        "authorize", "encrypt", "vulnerability", "secure",
    ],
    OSARole.QA: [
        "test", "verify", "check", "validate", "debug",
        "edge case", "coverage", "benchmark", "inspect",
    ],
}

CAPABILITY_KEYWORDS = {
    AgentCapability.CODE_GENERATION: ["implement", "write", "create", "build", "function"],
    AgentCapability.REFACTORING: ["refactor", "clean up", "improve", "optimize"],
    AgentCapability.TESTING: ["test", "spec", "coverage", "pytest"],
    AgentCapability.ARCHITECTURE_DESIGN: ["architecture", "design", "schema", "structure"],
    AgentCapability.PLANNING: ["plan", "roadmap", "schedule", "breakdown"],
    AgentCapability.SECURITY_AUDIT: ["security", "audit", "vulnerability", "sanitize"],
    AgentCapability.CODE_REVIEW: ["review", "check", "inspect", "analyze"],
}

def detect_role_and_agent(task_description: str, available_agents: List[str] = None) -> Tuple[OSARole, str]:
    """
    Detect the appropriate role and agent for a given task.

    Returns:
        Tuple of (OSA role, agent name)
    """
    task_lower = task_description.lower()

    # Score each role by keyword matches
    role_scores = {}
    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > 0:
            role_scores[role] = score

    # Get best role
    detected_role = max(role_scores, key=role_scores.get) if role_scores else OSARole.CODER

    # Get best agent for this role
    agent = get_agent_for_role(detected_role, available_agents)

    return detected_role, agent

def detect_capability(task_description: str) -> AgentCapability:
    """Detect the primary capability needed for a task."""
    task_lower = task_description.lower()

    for capability, keywords in CAPABILITY_KEYWORDS.items():
        if any(kw in task_lower for kw in keywords):
            return capability

    return AgentCapability.CODE_GENERATION
```

---

## 6. Enhanced YOLO Loop Integration

### Updated run_agent Function

```python
# Enhanced version for yolo_mode/scripts/yolo_loop.py

from yolo_mode.agents.registry import AGENT_REGISTRY, get_agent_for_role
from yolo_mode.agents.role_detection import detect_role_and_agent

def run_agent_v2(agent: str, prompt: str, verbose: bool = False) -> Optional[str]:
    """
    Enhanced agent runner with support for Qwen, Gemini, Crush, and others.

    Args:
        agent: Agent name (qwen, gemini, crush, claude, opencode)
        prompt: The task prompt
        verbose: Whether to print verbose output

    Returns:
        Agent output string, or None if failed
    """
    agent_config = AGENT_REGISTRY.get(agent)

    if not agent_config:
        print(f"⚠️ Unknown agent '{agent}', defaulting to claude-style invocation")
        cmd = [agent, prompt]
    else:
        cmd = agent_config.get_command(prompt)

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] Running {agent_config.name if agent_config else agent} task...")

    try:
        # Special handling for agents needing environment variables
        env_vars = None
        if agent == "opencode":
            env_vars = os.environ.copy()
            env_vars["OPENCODE_YOLO"] = "true"
            env_vars["OPENCODE_DANGEROUSLY_SKIP_PERMISSIONS"] = "true"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env_vars if env_vars else None
        )

        if result.returncode != 0:
            print(f"Error running {agent}: {result.stderr}")
            return None

        if verbose:
            print(f"Output: {result.stdout.strip()[:200]}...")

        return result.stdout

    except FileNotFoundError:
        print(f"❌ Agent '{agent}' not found in PATH.")
        return None
```

### Intelligent Agent Selection

```python
def select_best_agent_for_task(
    task: str,
    available_agents: List[str],
    goal: str = None
) -> Tuple[str, str]:
    """
    Intelligently select the best agent for a given task.

    Args:
        task: Task description
        available_agents: List of available agent names
        goal: Overall goal (for context)

    Returns:
        Tuple of (agent_name, reasoning)
    """
    detected_role, recommended_agent = detect_role_and_agent(task, available_agents)

    reasoning = f"Role: {detected_role.value}"

    # Check if recommended agent is available
    if recommended_agent not in available_agents:
        # Fallback logic
        fallback_map = {
            OSARole.ORCHESTRATOR: ["claude", "gemini"],
            OSARole.ARCHITECT: ["claude", "gemini"],
            OSARole.CODER: ["qwen", "claude"],
            OSARole.SECURITY: ["crush", "opencode", "claude"],
            OSARole.QA: ["crush", "claude"],
        }

        for fallback in fallback_map.get(detected_role, ["claude"]):
            if fallback in available_agents:
                recommended_agent = fallback
                reasoning += f" → Fallback to {fallback}"
                break

    return recommended_agent, reasoning
```

---

## 7. Resource-Aware Agent Selection

### Integration with Agent Contracts

```python
# yolo_mode/agents/resource_aware.py

from yolo_mode.contracts import AgentContract, ResourceDimension, ContractMode

def select_agent_by_contract(
    task: str,
    available_agents: List[str],
    contract: AgentContract
) -> str:
    """
    Select agent based on contract constraints and remaining resources.

    Args:
        task: Task description
        available_agents: Available agents
        contract: Active contract with resource constraints

    Returns:
        Selected agent name
    """
    # Get contract status
    status = contract.get_status()
    max_util = status["max_utilization"]
    time_remaining = status["time_remaining"]

    # High utilization or low time: prioritize speed
    if max_util > 0.8 or time_remaining < 30:
        # Choose fastest available agent
        speed_ranking = ["qwen", "claude", "crush", "gemini"]
        for agent in speed_ranking:
            if agent in available_agents:
                return agent

    # Low utilization: choose by quality
    if max_util < 0.5:
        quality_ranking = ["claude", "gemini", "crush", "qwen"]
        for agent in quality_ranking:
            if agent in available_agents:
                return agent

    # Default: role-based selection
    _, agent = detect_role_and_agent(task, available_agents)
    return agent

def optimize_agent_batch(
    tasks: List[str],
    available_agents: List[str],
    contract: AgentContract
) -> Dict[str, str]:
    """
    Optimize agent assignment for a batch of tasks.

    Args:
        tasks: List of task descriptions
        available_agents: Available agents
        contract: Active contract

    Returns:
        Dictionary mapping task → agent
    """
    assignment = {}

    for task in tasks:
        agent = select_agent_by_contract(task, available_agents, contract)
        assignment[task] = agent

    return assignment
```

---

## 8. Implementation Roadmap

### Phase 1: Core Integration (Week 1-2)

- [ ] Create `yolo_mode/agents/` module
- [ ] Implement agent registry system
- [ ] Add role detection with agent mapping
- [ ] Update `run_agent()` function for all CLI tools
- [ ] Add environment variable configuration for each agent

### Phase 2: Intelligent Selection (Week 3)

- [ ] Implement resource-aware agent selection
- [ ] Add capability-based routing
- [ ] Integrate with Agent Contracts framework
- [ ] Add fallback logic for unavailable agents

### Phase 3: Advanced Features (Week 4)

- [ ] Add agent performance tracking
- [ ] Implement dynamic agent switching
- [ ] Add multi-agent collaboration patterns
- [ ] Create agent benchmarking suite

### Phase 4: Testing & Documentation (Week 5)

- [ ] Comprehensive testing of all agent integrations
- [ ] Documentation for each agent's capabilities
- [ ] Usage examples and tutorials
- [ ] Performance benchmarking

---

## 9. Configuration File Format

### Proposed Agent Configuration

```yaml
# .claude-agents/config.yml

agents:
  qwen:
    enabled: true
    priority: 1
    models:
      default: qwen3-coder-next
      alternatives:
        - qwen2.5-coder-32b
        - qwen2.5-coder-14b
    osa_roles:
      - coder
      - qa
    environment:
      QWEN_YOLO: "true"
      QWEN_MAX_TOKENS: "100000"

  gemini:
    enabled: true
    priority: 2
    api_key_env: GEMINI_API_KEY
    models:
      default: gemini-2.5-flash
      pro: gemini-2.5-pro
    osa_roles:
      - orchestrator
      - architect
    environment:
      GEMINI_YOLO: "true"
      GEMINI_CONTEXT_SIZE: "large"

  crush:
    enabled: true
    priority: 3
    osa_roles:
      - security
      - qa
    environment:
      CRUSH_YOLO: "true"
      CRUSH_PERMISSION_MODEL: "explicit"

  claude:
    enabled: true
    priority: 4
    osa_roles:
      - architect
      - qa
    environment:
      ANTHROPIC_API_KEY_ENV: "ANTHROPIC_API_KEY"

role_mappings:
  orchestrator:
    primary: gemini
    fallback: claude
  architect:
    primary: gemini
    fallback: claude
  coder:
    primary: qwen
    fallback: claude
  security:
    primary: crush
    fallback: opencode
  qa:
    primary: crush
    fallback: claude

resource_profiles:
  urgent:
    preferred_agents:
      - qwen
      - crush
  economical:
    preferred_agents:
      - qwen
      - crush
  balanced:
    preferred_agents:
      - gemini
      - claude
```

---

## 10. Testing Strategy

### Agent Integration Tests

```python
# tests/test_agent_integration.py

import pytest
from yolo_mode.agents.registry import AGENT_REGISTRY, get_agent_for_role
from yolo_mode.agents.role_detection import detect_role_and_agent

class TestAgentRegistry:
    """Test agent registry functionality."""

    def test_agent_configs_loaded(self):
        """All agents should have valid configs."""
        assert "qwen" in AGENT_REGISTRY
        assert "gemini" in AGENT_REGISTRY
        assert "crush" in AGENT_REGISTRY

    def test_get_command_generation(self):
        """Test CLI command generation."""
        qwen = AGENT_REGISTRY["qwen"]
        cmd = qwen.get_command("write tests")
        assert "qwen" in cmd
        assert "--yolo" in cmd
        assert "write tests" in cmd

class TestRoleDetection:
    """Test role-based agent selection."""

    @pytest.mark.parametrize("task,expected_role", [
        ("implement a user class", "coder"),
        ("design the system architecture", "architect"),
        ("plan the implementation steps", "orchestrator"),
        ("audit for security vulnerabilities", "security"),
        ("write unit tests", "qa"),
    ])
    def test_role_detection(self, task, expected_role):
        """Test role detection from task descriptions."""
        role, agent = detect_role_and_agent(task)
        assert role.value == expected_role

class TestResourceAwareSelection:
    """Test resource-aware agent selection."""

    def test_high_utilization_fast_agent(self):
        """High utilization should select fast agents."""
        # Test implementation
        pass

    def test_low_utilization_quality_agent(self):
        """Low utilization should select quality agents."""
        # Test implementation
        pass
```

---

## 11. Sources

### Qwen CLI
- [Qwen3-Coder: Agentic Coding in the World](https://qwen.ai/blog?id=qwen3-coder)
- [Qwen3-Coder-Next Release](https://dev.to/sienna/qwen3-coder-next-the-complete-2026-guide-to-running-powerful-ai-coding-agents-locally-1k95)
- [Qwen Code GitHub Repository](https://github.com/QwenLM/qwen-code)
- [Qwen Code CLI Tool Overview](https://www.kdnuggets.com/qwen-code-leverages-qwen3-as-a-cli-agentic-programming-tool)

### Gemini CLI
- [Gemini CLI Documentation](https://developers.google.com/gemini-code-assist/docs/gemini-cli)
- [Gemini CLI Official Website](https://geminicli.com/)
- [Gemini CLI GitHub Repository](https://github.com/google-gemini/gemini-cli)
- [Google Announces Gemini CLI](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/)
- [Conductor Feature Announcement](https://developers.googleblog.com/conductor-introducing-context-driven-development-for-gemini-cli/)

### Crush CLI
- [Crush CLI GitHub Repository](https://github.com/charmbracelet/crush)
- [Top 5 CLI Coding Agents in 2026](https://pinggy.io/blog/top_cli_based_ai_coding_agents/)
- [2026 Guide: 15 AI CLI Tools Compared](https://www.tembo.io/blog/coding-cli-tools-comparison)
- [Crush Comes Home - Charm Blog](https://charm.land/blog/crush-comes-home/)
- [Crush CLI with Web MCP](https://brightdata.com/blog/ai/crush-cli-with-web-mcp)

---

## 12. Conclusion

The integration of Qwen CLI, Gemini CLI, and Crush CLI as subagents within the YOLO Mode OSA Framework provides a powerful, flexible multi-agent system:

1. **Qwen CLI** excels as the **Coder** role with fast, efficient code generation
2. **Gemini CLI** provides excellent **Orchestration** and **Architecture** capabilities
3. **Crush CLI** offers strong **Security** and **QA** features with permission-based execution

By implementing the agent registry system, intelligent role-based routing, and resource-aware selection, the OSA Framework can leverage each tool's strengths while providing a unified, production-ready agentic coding system.

The proposed implementation roadmap provides a clear path to integration, starting with core agent support and progressing to advanced features like performance tracking and dynamic agent selection.

---

*Report prepared by YOLO Mode autonomous research agent*
*Date: 2026-02-11*
