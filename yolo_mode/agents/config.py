"""
YOLO Mode Agent Configuration

Provides configuration file support for managing CLI agents.
Allows users to customize agent behavior, add custom agents, and manage
agent priorities without editing code.

Configuration file location: .claude-agents/config.yml
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Try to import YOLO components
try:
    from yolo_mode.agents.registry import AgentConfig, OSARole, AgentCapability
    from yolo_mode.agents import AGENT_REGISTRY
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


# ============================================================================
# CONFIGURATION DATA STRUCTURES
# ============================================================================

@dataclass
class AgentOverride:
    """Override configuration for a built-in agent."""
    agent_id: str
    enabled: bool = True
    priority: Optional[int] = None
    custom_flags: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None


@dataclass
class CustomAgent:
    """Configuration for a custom agent."""
    name: str
    description: str
    cli_command: str
    yolo_flag: str = "--yolo"
    subcommand: Optional[str] = None
    model_flag: Optional[str] = None
    preferred_models: List[str] = field(default_factory=list)
    osa_roles: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    priority: int = 99


@dataclass
class AgentConfigFile:
    """Complete agent configuration file structure."""

    version: str = "1.0"
    default_agent: str = "claude"

    # Built-in agent overrides
    agent_overrides: Dict[str, AgentOverride] = field(default_factory=dict)

    # Custom agents
    custom_agents: Dict[str, CustomAgent] = field(default_factory=dict)

    # Global settings
    global_settings: Dict[str, Any] = field(default_factory=dict)

    # Contract defaults
    contract_mode: str = "balanced"
    max_parallel_workers: int = 3


# ============================================================================
# CONFIGURATION FILE MANAGER
# ============================================================================

class AgentConfigManager:
    """
    Manages agent configuration from .claude-agents/config.yml

    Provides ability to:
    - Override built-in agent configurations
    - Add custom CLI agents
    - Set global agent defaults
    - Configure contract behavior
    """

    CONFIG_PATH = ".claude-agents/config.yml"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to config file (default: .claude-agents/config.yml)
        """
        self.config_path = config_path or self.CONFIG_PATH
        self.config: Optional[AgentConfigFile] = None
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            # Create default config
            self.config = self._create_default_config()
            self._save_config()
            return

        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)

            self.config = self._dict_to_config(data)

        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            self.config = self._create_default_config()

    def _dict_to_config(self, data: Dict) -> AgentConfigFile:
        """Convert dictionary to AgentConfigFile object."""
        overrides = {}
        for agent_id, override_data in data.get("agent_overrides", {}).items():
            overrides[agent_id] = AgentOverride(**override_data)

        custom_agents = {}
        for agent_id, custom_data in data.get("custom_agents", {}).items():
            custom_agents[agent_id] = CustomAgent(**custom_data)

        return AgentConfigFile(
            version=data.get("version", "1.0"),
            default_agent=data.get("default_agent", "claude"),
            agent_overrides=overrides,
            custom_agents=custom_agents,
            global_settings=data.get("global_settings", {}),
            contract_mode=data.get("contract_mode", "balanced"),
            max_parallel_workers=data.get("max_parallel_workers", 3)
        )

    def _create_default_config(self) -> AgentConfigFile:
        """Create default configuration."""
        return AgentConfigFile(
            version="1.0",
            default_agent="claude",
            agent_overrides={},
            custom_agents={},
            global_settings={
                "log_agent_selection": True,
                "show_resource_usage": True,
                "enable_tts_default": False
            },
            contract_mode="balanced",
            max_parallel_workers=3
        )

    def _save_config(self) -> bool:
        """Save configuration to YAML file."""
        if not self.config:
            return False

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)

        data = {
            "version": self.config.version,
            "default_agent": self.config.default_agent,
            "agent_overrides": self.config.agent_overrides,
            "custom_agents": self.config.custom_agents,
            "global_settings": self.config.global_settings,
            "contract_mode": self.config.contract_mode,
            "max_parallel_workers": self.config.max_parallel_workers
        }

        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get effective configuration for an agent.

        Applies overrides and returns merged configuration.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentConfig with overrides applied, or None if agent not found
        """
        if not YOLO_AVAILABLE:
            return None

        # Check for custom agent first
        if agent_id in self.config.custom_agents:
            custom = self.config.custom_agents[agent_id]
            return AgentConfig(
                name=custom.name,
                description=custom.description,
                cli_command=custom.cli_command,
                yolo_flag=custom.yolo_flag,
                subcommand=custom.subcommand,
                model_flag=custom.model_flag,
                preferred_models=custom.preferred_models,
                osa_roles=[OSARole(r) for r in custom.osa_roles],
                capabilities=[AgentCapability(c) for c in custom.capabilities],
                env_vars=custom.env_vars.copy(),
                priority=custom.priority
            )

        # Check for built-in agent
        if agent_id in AGENT_REGISTRY:
            base_config = AGENT_REGISTRY[agent_id]

            # Apply overrides
            if agent_id in self.config.agent_overrides:
                override = self.config.agent_overrides[agent_id]

                # Merge env vars
                env_vars = base_config.env_vars.copy()
                env_vars.update(override.env_vars)

                return AgentConfig(
                    name=base_config.name,
                    cli_command=base_config.cli_command,
                    yolo_flag=override.custom_flags.get("yolo_flag", base_config.yolo_flag),
                    subcommand=override.custom_flags.get("subcommand", base_config.subcommand),
                    model_flag=override.custom_flags.get("model_flag", base_config.model_flag),
                    preferred_models=override.custom_flags.get("preferred_models", base_config.preferred_models),
                    osa_roles=base_config.osa_roles,
                    capabilities=base_config.capabilities,
                    env_vars=env_vars,
                    priority=override.priority or base_config.priority,
                    description=override.custom_flags.get("description", base_config.description)
                )

            return base_config

        return None

    def get_all_available_agents(self) -> List[str]:
        """
        Get list of all available agent IDs.

        Includes both built-in and custom agents.
        """
        agents = []

        # Add built-in agents (unless disabled)
        if YOLO_AVAILABLE:
            for agent_id, override in self.config.agent_overrides.items():
                if override.enabled:
                    agents.append(agent_id)

            # Add agents without explicit overrides (enabled by default)
            for agent_id in AGENT_REGISTRY:
                if agent_id not in self.config.agent_overrides:
                    agents.append(agent_id)

        # Add custom agents
        agents.extend(self.config.custom_agents.keys())

        return agents

    def get_default_agent(self) -> str:
        """Get default agent ID."""
        return self.config.default_agent

    def set_default_agent(self, agent_id: str) -> bool:
        """Set default agent."""
        if agent_id not in self.get_all_available_agents():
            print(f"Warning: Agent '{agent_id}' not available")
            return False

        self.config.default_agent = agent_id
        return self._save_config()

    def add_custom_agent(self, agent: CustomAgent) -> bool:
        """Add a custom agent configuration."""
        self.config.custom_agents[agent.name] = agent
        return self._save_config()

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent (custom or override)."""
        # Try custom agents first
        if agent_id in self.config.custom_agents:
            del self.config.custom_agents[agent_id]
            return self._save_config()

        # Try overrides
        if agent_id in self.config.agent_overrides:
            del self.config.agent_overrides[agent_id]
            return self._save_config()

        return False

    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """Get a global setting value."""
        return self.config.global_settings.get(key, default)

    def set_global_setting(self, key: str, value: Any) -> bool:
        """Set a global setting value."""
        self.config.global_settings[key] = value
        return self._save_config()

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def print_config(self) -> None:
        """Print current configuration."""
        print("\n=== YOLO Agent Configuration ===\n")

        print(f"Config file: {self.config_path}")
        print(f"Version: {self.config.version}")
        print(f"Default agent: {self.config.default_agent}")
        print(f"Contract mode: {self.config.contract_mode}")
        print(f"Max parallel workers: {self.config.max_parallel_workers}")

        print("\nAvailable agents:")
        for agent_id in self.get_all_available_agents():
            config = self.get_agent_config(agent_id)
            if config:
                print(f"  {agent_id}:")
                print(f"    Name: {config.name}")
                print(f"    Command: {config.cli_command}")
                if config.osa_roles:
                    print(f"    Roles: {[r.value for r in config.osa_roles]}")
                if config.priority != 99:
                    print(f"    Priority: {config.priority}")

        print("\nGlobal settings:")
        for key, value in self.config.global_settings.items():
            print(f"  {key}: {value}")


# ============================================================================
# CONFIGURATION FILE TEMPLATE
# ============================================================================

DEFAULT_CONFIG_TEMPLATE = """# YOLO Mode Agent Configuration
# Auto-generated - do not edit manually unless you know what you're doing!

version: 1.0

# Default agent to use when no role-specific agent is available
# Options: claude, qwen, gemini, crush, opencode
default_agent: claude

# Contract mode for resource management
# Options: urgent, economical, balanced
contract_mode: balanced

# Maximum parallel workers for batch execution
max_parallel_workers: 3

# ==============================================================================
# BUILT-IN AGENT OVERRIDES
# ==============================================================================
# Override settings for built-in agents without modifying code

agent_overrides:
  # Example: Override qwen to use different model or flags
  qwen:
    enabled: true
    priority: 1  # Lower = higher priority
    custom_flags:
      yolo_flag: "--yolo"
      model_flag: "--model"
      preferred_models: ["qwen3-coder-32b", "qwen3-coder-next"]
      description: "Qwen with optimized models"
    env_vars:
      QWEN_MAX_TOKENS: "100000"
      QWEN_TEMPERATURE: "0.7"

  # Example: Enable gemini with custom timeout
  gemini:
    enabled: true
    priority: 2
    timeout_seconds: 120

  # Example: Disable crush (set enabled: false)
  crush:
    enabled: false

# ==============================================================================
# CUSTOM AGENTS
# ==============================================================================
# Define your own CLI agents or external tools

custom_agents:
  # Example: Add a custom agent for specific use case
  aider:
    name: "Aider CLI"
    description: "Fast AI pair programming tool"
    cli_command: "aider"
    yolo_flag: "--yolo"
    osa_roles:
      - coder
    capabilities:
      - code_generation
      - refactoring
      - testing
    priority: 5
    preferred_models:
      - "gpt-4"
      - "claude-3.5-sonnet"
    env_vars:
      AIDER_MODEL: "gpt-4"

  # Example: Add another custom agent
  continue:
    name: "Continue CLI"
    description: "DevOps AI assistant"
    cli_command: "continue"
    yolo_flag: "-y"
    subcommand: "run"
    osa_roles:
      - orchestrator
      - architect
    capabilities:
      - planning
      - context_management
      - documentation
    priority: 10

# ==============================================================================
# GLOBAL SETTINGS
# ==============================================================================

global_settings:
  # Enable logging of agent selection decisions
  log_agent_selection: true

  # Show resource usage after each task
  show_resource_usage: true

  # Enable TTS by default
  enable_tts_default: false

  # Maximum iterations before prompting for user input
  max_auto_iterations: 50

  # Timeout for single agent execution (seconds)
  default_agent_timeout: 120

  # Allow auto-continuation after task completion
  auto_continue: true
"""


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_config(config_path: Optional[str] = None) -> AgentConfigManager:
    """
    Factory function to create configuration manager.

    Args:
        config_path: Optional path to config file

    Returns:
        Configured configuration manager
    """
    return AgentConfigManager(config_path=config_path)


def init_config_file(config_path: Optional[str] = None) -> None:
    """
    Initialize configuration file with default template.

    Args:
        config_path: Optional path to config file (default: .claude-agents/config.yml)
    """
    config_path = config_path or AgentConfigManager.CONFIG_PATH

    if not os.path.exists(config_path):
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

        # Write default template
        with open(config_path, 'w') as f:
            f.write(DEFAULT_CONFIG_TEMPLATE)

        print(f"Created default config file: {config_path}")


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== YOLO Agent Configuration Demo ===\n")

    # Initialize default config
    init_config_file()

    # Create config manager
    manager = create_config()

    # Print configuration
    manager.print_config()

    # Example: Add a custom agent
    print("\nExample: Adding custom agent...")
    custom = CustomAgent(
        name="example-agent",
        description="An example custom agent",
        cli_command="example-cli",
        yolo_flag="--auto",
        osa_roles=["coder"],
        capabilities=["code_generation"],
        priority=50
    )
    manager.add_custom_agent(custom)
    print("Custom agent added!")
