"""
YOLO Mode State File Handler

Enhanced state management with YAML format for tracking:
- Contract status and resource utilization
- Agent usage statistics
- Task completion metrics
- Session metadata

Based on research recommendations from OSA_IMPROVEMENT_RECOMMENDATIONS.md
"""

import os
import time
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


# Try to import YAML library
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# STATE DATA STRUCTURES
# ============================================================================

@dataclass
class YoloState:
    """
    Complete YOLO Mode state representation.

    Matches the YAML format specification for comprehensive
    state tracking and persistence.
    """
    # Metadata
    version: str = "2.0"
    created_at: str = ""
    last_updated: str = ""

    # Goal
    original_goal: str = ""
    current_status: str = "pending"

    # Session
    iteration: int = 0
    max_iterations: int = 50
    start_time: str = ""

    # Contract
    contract_mode: str = "balanced"
    contract_state: str = "drafted"
    contract_max_utilization: float = 0.0
    contract_time_remaining: float = 0.0
    contract_is_expired: bool = False
    contract_is_violated: bool = False

    # Resources
    tokens_budget: float = 100000
    tokens_consumed: float = 0
    tokens_utilization: float = 0.0

    iterations_budget: int = 10
    iterations_consumed: int = 0
    iterations_utilization: float = 0.0

    time_budget: float = 300
    time_remaining: float = 0.0
    time_utilization: float = 0.0

    # Agent usage
    agent_stats: Dict[str, Dict] = field(default_factory=dict)

    # Tasks
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_pending: int = 0
    tasks_failed: int = 0

    # Workflow
    current_phase: str = "planning"
    next_actions: list = field(default_factory=list)


# ============================================================================
# STATE FILE MANAGER
# ============================================================================

class YoloStateManager:
    """
    Manages YOLO Mode state file with YAML format.

    Provides read/write operations with automatic conversion
    between legacy markdown format and new YAML format.
    """

    def __init__(self, state_file: str = ".claude/yolo-state.md"):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file (legacy .md or new .yaml)
        """
        # Support both legacy and new paths
        if state_file.endswith(".md"):
            self.yaml_file = state_file.replace(".md", ".yaml")
            self.legacy_file = state_file
        else:
            self.yaml_file = state_file
            self.legacy_file = state_file.replace(".yaml", ".md")

        self.state: Optional[YoloState] = None

    def load_state(self) -> YoloState:
        """
        Load state from file, with automatic format detection.

        Returns:
            YoloState object with current state
        """
        # Try YAML first
        if os.path.exists(self.yaml_file):
            try:
                return self._load_yaml_state()
            except Exception as e:
                print(f"Warning: Could not load YAML state: {e}")

        # Fall back to legacy markdown format
        if os.path.exists(self.legacy_file):
            try:
                return self._load_legacy_state()
            except Exception as e:
                print(f"Warning: Could not load legacy state: {e}")

        # Return default state if no file exists
        return YoloState(
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            current_status="pending"
        )

    def _load_yaml_state(self) -> YoloState:
        """Load state from YAML file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML not installed")

        with open(self.yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        return self._dict_to_state(data)

    def _load_legacy_state(self) -> YoloState:
        """
        Load state from legacy markdown format.

        Converts the old iteration-based format to new structured format.
        """
        with open(self.legacy_file, 'r') as f:
            content = f.read()

        # Parse iteration count from legacy format
        iteration = 0
        for line in content.split('\n'):
            if 'Iteration:' in line:
                try:
                    iteration = int(line.split(':')[1].strip())
                except ValueError:
                    pass

        return YoloState(
            version="2.0",
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            last_updated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            iteration=iteration,
            original_goal="YOLO Mode Session",
            current_status="in_progress"
        )

    def _dict_to_state(self, data: Dict) -> YoloState:
        """Convert dictionary to YoloState object."""
        metadata = data.get("metadata", {})
        goal = data.get("goal", {})
        session = data.get("session", {})
        contract = data.get("contract", {})
        resources = data.get("resources", {})
        agents = data.get("agents", {})
        tasks = data.get("tasks", {})
        workflow = data.get("workflow", {})

        return YoloState(
            version=metadata.get("version", "2.0"),
            created_at=metadata.get("created_at", ""),
            last_updated=metadata.get("last_updated", ""),
            original_goal=goal.get("original", ""),
            current_status=goal.get("current_status", "pending"),
            iteration=session.get("iteration", 0),
            max_iterations=session.get("max_iterations", 50),
            start_time=session.get("start_time", ""),
            contract_mode=contract.get("mode", "balanced"),
            contract_state=contract.get("state", "drafted"),
            contract_max_utilization=contract.get("status", {}).get("max_utilization", 0.0),
            contract_time_remaining=contract.get("status", {}).get("time_remaining", 0.0),
            contract_is_expired=contract.get("status", {}).get("is_expired", False),
            contract_is_violated=contract.get("status", {}).get("is_violated", False),
            tokens_budget=resources.get("tokens", {}).get("budget", 100000),
            tokens_consumed=resources.get("tokens", {}).get("consumed", 0),
            tokens_utilization=resources.get("tokens", {}).get("utilization", 0.0),
            iterations_budget=resources.get("iterations", {}).get("budget", 10),
            iterations_consumed=resources.get("iterations", {}).get("consumed", 0),
            iterations_utilization=resources.get("iterations", {}).get("utilization", 0.0),
            time_budget=resources.get("time", {}).get("budget", 300),
            time_remaining=resources.get("time", {}).get("remaining", 0.0),
            time_utilization=resources.get("time", {}).get("utilization", 0.0),
            agent_stats=agents,
            tasks_total=tasks.get("total", 0),
            tasks_completed=tasks.get("completed", 0),
            tasks_pending=tasks.get("pending", 0),
            tasks_failed=tasks.get("failed", 0),
            current_phase=workflow.get("current_phase", "planning"),
            next_actions=workflow.get("next_actions", [])
        )

    def save_state(self, state: YoloState) -> bool:
        """
        Save state to both YAML and legacy formats.

        Args:
            state: YoloState object to save

        Returns:
            True if save successful
        """
        self.state = state

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.yaml_file)), exist_ok=True)

        # Save YAML format if available
        if YAML_AVAILABLE:
            try:
                self._save_yaml_state(state)
            except Exception as e:
                print(f"Warning: Could not save YAML state: {e}")

        # Also save legacy format for compatibility
        try:
            self._save_legacy_state(state)
        except Exception as e:
            print(f"Warning: Could not save legacy state: {e}")
            return False

        return True

    def _save_yaml_state(self, state: YoloState):
        """Save state to YAML file."""
        data = self._state_to_dict(state)

        with open(self.yaml_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def _save_legacy_state(self, state: YoloState):
        """Save state to legacy markdown format."""
        content = f"""# YOLO Mode State
# Auto-generated - do not edit manually

Iteration: {state.iteration}
Last Updated: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}

---
"""
        with open(self.legacy_file, 'w') as f:
            f.write(content)

    def _state_to_dict(self, state: YoloState) -> Dict:
        """Convert YoloState to dictionary for YAML serialization."""
        return {
            "metadata": {
                "version": state.version,
                "created_at": state.created_at,
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "goal": {
                "original": state.original_goal,
                "current_status": state.current_status
            },
            "session": {
                "iteration": state.iteration,
                "max_iterations": state.max_iterations,
                "start_time": state.start_time
            },
            "contract": {
                "mode": state.contract_mode,
                "state": state.contract_state,
                "status": {
                    "max_utilization": state.contract_max_utilization,
                    "time_remaining": state.contract_time_remaining,
                    "is_expired": state.contract_is_expired,
                    "is_violated": state.contract_is_violated
                }
            },
            "resources": {
                "tokens": {
                    "budget": state.tokens_budget,
                    "consumed": state.tokens_consumed,
                    "utilization": state.tokens_utilization
                },
                "iterations": {
                    "budget": state.iterations_budget,
                    "consumed": state.iterations_consumed,
                    "utilization": state.iterations_utilization
                },
                "time": {
                    "budget": state.time_budget,
                    "remaining": state.time_remaining,
                    "utilization": state.time_utilization
                }
            },
            "agents": state.agent_stats,
            "tasks": {
                "total": state.tasks_total,
                "completed": state.tasks_completed,
                "pending": state.tasks_pending,
                "failed": state.tasks_failed
            },
            "workflow": {
                "current_phase": state.current_phase,
                "next_actions": state.next_actions
            }
        }

    def update_from_contract(self, contract) -> None:
        """
        Update state from an AgentContract object.

        Args:
            contract: AgentContract to pull status from
        """
        if self.state is None:
            self.state = self.load_state()

        status = contract.get_status()

        self.state.contract_mode = contract.mode.value
        self.state.contract_state = status["state"]
        self.state.contract_max_utilization = status["max_utilization"]
        self.state.contract_time_remaining = status["time_remaining"]
        self.state.contract_is_expired = status["is_expired"]
        self.state.contract_is_violated = status["is_violated"]

        # Update resource stats
        self.state.tokens_consumed = status["consumption"].get("tokens", 0)
        self.state.iterations_consumed = status["consumption"].get("iterations", 0)

        # Update utilizations
        for resource, utilization in status["utilization"].items():
            if resource == "tokens":
                self.state.tokens_utilization = utilization
            elif resource == "iterations":
                self.state.iterations_utilization = utilization
            elif resource == "compute_time":
                self.state.time_utilization = utilization

    def increment_iteration(self) -> None:
        """Increment the iteration counter."""
        if self.state is None:
            self.state = self.load_state()

        self.state.iteration += 1
        self.state.last_updated = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def get_state(self) -> YoloState:
        """Get current state, loading if necessary."""
        if self.state is None:
            self.state = self.load_state()
        return self.state

    def print_summary(self) -> None:
        """Print a summary of the current state."""
        state = self.get_state()

        print(f"\n=== YOLO Mode State Summary ===")
        print(f"Iteration: {state.iteration}/{state.max_iterations}")
        print(f"Status: {state.current_status}")
        print(f"Contract: {state.contract_mode} ({state.contract_state})")

        if state.contract_state != "drafted":
            print(f"\n📊 Resource Utilization:")
            print(f"  Tokens: {state.tokens_consumed:.0f}/{state.tokens_budget:.0f} ({state.tokens_utilization*100:.1f}%)")
            print(f"  Iterations: {state.iterations_consumed}/{state.iterations_budget} ({state.iterations_utilization*100:.1f}%)")
            print(f"  Time: {state.contract_time_remaining:.0f}s remaining")

            if state.contract_is_expired or state.contract_is_violated:
                print(f"  ⚠️  Contract: {'EXPIRED' if state.contract_is_expired else ''} {'VIOLATED' if state.contract_is_violated else ''}")

        if state.tasks_total > 0:
            print(f"\n📋 Tasks:")
            print(f"  Total: {state.tasks_total}")
            print(f"  Completed: {state.tasks_completed}")
            print(f"  Pending: {state.tasks_pending}")
            print(f"  Failed: {state.tasks_failed}")


# ============================================================================
# GLOBAL STATE MANAGER INSTANCE
# ============================================================================

# Default state manager instance
_global_state_manager: Optional[YoloStateManager] = None


def get_state_manager(state_file: str = ".claude/yolo-state.md") -> YoloStateManager:
    """
    Get or create the global state manager.

    Args:
        state_file: Optional path to state file

    Returns:
        YoloStateManager instance
    """
    global _global_state_manager

    if _global_state_manager is None:
        _global_state_manager = YoloStateManager(state_file)

    return _global_state_manager


def load_state(state_file: str = ".claude/yolo-state.md") -> YoloState:
    """
    Convenience function to load state.

    Args:
        state_file: Optional path to state file

    Returns:
        YoloState object
    """
    return get_state_manager(state_file).load_state()


def save_state(state: YoloState, state_file: str = ".claude/yolo-state.md") -> bool:
    """
    Convenience function to save state.

    Args:
        state: YoloState object to save
        state_file: Optional path to state file

    Returns:
        True if save successful
    """
    return get_state_manager(state_file).save_state(state)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Demo: Create and save state
    print("=== YOLO State Manager Demo ===\n")

    # Check YAML availability
    print(f"PyYAML available: {YAML_AVAILABLE}")

    # Create state manager
    manager = YoloStateManager(".claude/yolo-state.md")

    # Load or create state
    state = manager.load_state()
    print(f"Loaded state: {state.current_status}")

    # Update some fields
    state.original_goal = "Demo YOLO Mode session"
    state.iteration = 1
    state.current_phase = "execution"
    state.next_actions = ["execute_tasks", "verify_completion"]

    # Save state
    manager.save_state(state)
    print("State saved successfully")

    # Print summary
    manager.print_summary()
