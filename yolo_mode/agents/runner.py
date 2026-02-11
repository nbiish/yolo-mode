"""
Unified Agent Runner - Consistent interface for all CLI agents.

Provides a single `run_agent()` function that works with all registered
CLI agents (Qwen, Gemini, Crush, Claude, OpenCode) with proper
command construction, environment handling, and error management.
"""

import subprocess
import os
import sys
import time
from typing import Optional, Dict, Any
from .registry import AGENT_REGISTRY, AgentConfig


# ============================================================================
# AGENT RUNNER
# ============================================================================

class AgentRunner:
    """
    Unified runner for all CLI agents.

    Handles command construction, environment setup, execution,
    and error handling consistently across all agent types.
    """

    def __init__(self, default_timeout: int = 300):
        """
        Initialize the agent runner.

        Args:
            default_timeout: Default timeout in seconds (5 minutes)
        """
        self.default_timeout = default_timeout
        self.execution_stats: Dict[str, Dict[str, Any]] = {}

    def run(
        self,
        agent: str,
        prompt: str,
        verbose: bool = False,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        Run any registered agent with consistent interface.

        Args:
            agent: Agent name (must be in AGENT_REGISTRY)
            prompt: Task prompt
            verbose: Enable verbose logging
            timeout: Custom timeout in seconds
            capture_output: Whether to capture stdout/stderr
            model: Specific model to use

        Returns:
            Agent output as string, or None if failed
        """
        config = AGENT_REGISTRY.get(agent)

        if not config:
            print(f"⚠️ Unknown agent '{agent}', attempting direct invocation")
            return self._run_direct(agent, prompt, verbose, timeout)

        # Build command
        cmd = self._build_command(config, prompt, model)

        if verbose:
            print(f"🤖 Running {config.name}: {self._format_cmd(cmd)}")

        # Prepare environment
        env = self._prepare_env(config)

        # Track execution start
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=not capture_output,
                env=env,
                timeout=timeout or self.default_timeout
            )

            # Track execution stats
            elapsed = time.time() - start_time
            self._track_stats(agent, elapsed, result.returncode == 0)

            if result.returncode != 0:
                if verbose:
                    stderr = result.stderr if capture_output else "see terminal output"
                    print(f"❌ {config.name} error (exit {result.returncode}): {stderr}")
                return None

            if capture_output:
                return result.stdout
            return ""

        except FileNotFoundError:
            print(f"❌ Agent '{agent}' not found in PATH.")
            print(f"   Install with appropriate package manager for '{config.cli_command}'")
            return None
        except subprocess.TimeoutExpired:
            print(f"⏱️ Agent '{agent}' timed out after {timeout or self.default_timeout}s")
            return None
        except Exception as e:
            print(f"❌ Error running {agent}: {e}")
            return None

    def _build_command(self, config: AgentConfig, prompt: str, model: Optional[str] = None) -> list:
        """Build CLI command based on agent configuration."""
        cmd = [config.cli_command]

        # Add subcommand if specified
        if config.subcommand:
            cmd.append(config.subcommand)

        # Add YOLO flag if specified
        if config.yolo_flag:
            cmd.append(config.yolo_flag)

        # Add model selection if specified
        if model and config.model_flag:
            cmd.extend([config.model_flag, model])

        # Add prompt
        cmd.append(prompt)

        return cmd

    def _prepare_env(self, config: AgentConfig) -> Dict[str, str]:
        """Prepare environment variables for the agent."""
        env = os.environ.copy()
        env.update(config.env_vars)
        return env

    def _run_direct(self, agent: str, prompt: str, verbose: bool, timeout: int) -> Optional[str]:
        """Fallback for unknown agents - try direct invocation."""
        try:
            result = subprocess.run(
                [agent, prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout if result.returncode == 0 else None
        except Exception:
            return None

    def _format_cmd(self, cmd: list) -> str:
        """Format command for display (truncate long prompts)."""
        if len(cmd) > 3:
            return f"{cmd[0]} {cmd[1]} ... {cmd[-1][:50]}..."
        return " ".join(cmd)

    def _track_stats(self, agent: str, elapsed: float, success: bool):
        """Track execution statistics for each agent."""
        if agent not in self.execution_stats:
            self.execution_stats[agent] = {
                "count": 0,
                "successes": 0,
                "failures": 0,
                "total_time": 0.0,
            }

        stats = self.execution_stats[agent]
        stats["count"] += 1
        stats["total_time"] += elapsed

        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1

    def get_stats(self, agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics.

        Args:
            agent: Specific agent to get stats for, or None for all

        Returns:
            Dictionary of statistics
        """
        if agent:
            return self.execution_stats.get(agent, {})
        return self.execution_stats

    def print_stats(self):
        """Print execution statistics summary."""
        if not self.execution_stats:
            print("No execution statistics available.")
            return

        print("\n=== Agent Execution Statistics ===\n")
        for agent, stats in self.execution_stats.items():
            count = stats["count"]
            success_rate = stats["successes"] / count * 100 if count > 0 else 0
            avg_time = stats["total_time"] / count if count > 0 else 0

            print(f"  {agent}:")
            print(f"    Executions: {count}")
            print(f"    Success rate: {success_rate:.1f}%")
            print(f"    Avg time: {avg_time:.1f}s")


# Global runner instance for convenience
_global_runner = AgentRunner()


def run_agent(
    agent: str,
    prompt: str,
    verbose: bool = False,
    timeout: Optional[int] = None,
    model: Optional[str] = None
) -> Optional[str]:
    """
    Convenience function to run an agent.

    Args:
        agent: Agent name (must be in AGENT_REGISTRY)
        prompt: Task prompt
        verbose: Enable verbose logging
        timeout: Custom timeout in seconds
        model: Specific model to use

    Returns:
        Agent output as string, or None if failed

    Example:
        >>> output = run_agent("qwen", "write a hello world function")
        >>> output = run_agent("gemini", "plan this project", model="gemini-2.5-pro")
    """
    return _global_runner.run(agent, prompt, verbose, timeout, True, model)


def run_agent_interactive(
    agent: str,
    prompt: str,
    verbose: bool = False
) -> bool:
    """
    Run an agent with interactive output (not captured).

    Args:
        agent: Agent name (must be in AGENT_REGISTRY)
        prompt: Task prompt
        verbose: Enable verbose logging

    Returns:
        True if successful, False otherwise

    Example:
        >>> success = run_agent_interactive("qwen", "write a hello world function")
    """
    result = _global_runner.run(agent, prompt, verbose, capture_output=False)
    return result is not None


def get_execution_stats(agent: Optional[str] = None) -> Dict[str, Any]:
    """Get execution statistics for an agent or all agents."""
    return _global_runner.get_stats(agent)


def print_execution_stats():
    """Print execution statistics summary."""
    _global_runner.print_stats()


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

def run_agent_legacy(agent: str, prompt: str, verbose: bool = False) -> Optional[str]:
    """
    Legacy function for backward compatibility with yolo_loop.py

    This maintains the same signature as the original run_agent function
    in yolo_mode/scripts/yolo_loop.py for easy migration.

    Args:
        agent: Agent name
        prompt: Task prompt
        verbose: Enable verbose output

    Returns:
        Agent output or None if failed
    """
    config = AGENT_REGISTRY.get(agent)

    if not config:
        print(f"⚠️ Unknown agent '{agent}'")
        return None

    cmd = [config.cli_command]

    if config.subcommand:
        cmd.append(config.subcommand)

    if config.yolo_flag:
        cmd.append(config.yolo_flag)

    cmd.append(prompt)

    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] Running {config.name} task...")

    env = os.environ.copy()
    env.update(config.env_vars)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode != 0:
            if verbose:
                print(f"Error running {agent}: {result.stderr}")
            return None

        if verbose:
            print(f"Output: {result.stdout.strip()[:200]}...")

        return result.stdout

    except FileNotFoundError:
        print(f"❌ Agent '{agent}' not found in PATH.")
        return None
    except Exception as e:
        print(f"❌ Error running {agent}: {e}")
        return None


if __name__ == "__main__":
    # Demo: test agent runner
    print("=== Agent Runner Demo ===\n")

    # Test registry access
    from .registry import get_agent_for_role, OSARole

    print("Testing agent retrieval:")
    for role in OSARole:
        agent = get_agent_for_role(role)
        config = AGENT_REGISTRY.get(agent)
        print(f"  {role.value:12} → {agent:10} ({config.description})")

    # Test command building
    print("\nCommand building examples:")
    for agent_name in ["qwen", "gemini", "crush"]:
        config = AGENT_REGISTRY.get(agent_name)
        runner = AgentRunner()
        cmd = runner._build_command(config, "write hello world")
        print(f"  {agent_name}: {' '.join(cmd)}")
