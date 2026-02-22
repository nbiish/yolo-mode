#!/usr/bin/env python3
"""Mini-SWE-Agent Integration for YOLO Mode"""

import subprocess
from typing import Optional
from dataclasses import dataclass

@dataclass
class MiniSweResult:
    """Result from mini-swe-agent execution."""
    success: bool
    output: str
    error: Optional[str] = None
    model_used: str = ""

class MiniSweAgentRunner:
    """Runner for mini-swe-agent."""
    
    def __init__(self, model_name: str = "gpt-4o", timeout: int = 300, verbose: bool = True):
        self.model_name = model_name
        self.timeout = timeout
        self.verbose = verbose
    
    def run(self, task: str) -> MiniSweResult:
        """Run mini-swe-agent on a task."""
        try:
            from minisweagent import DefaultAgent, LitellmModel, LocalEnvironment
            model = LitellmModel(model_name=self.model_name)
            env = LocalEnvironment(timeout=self.timeout)
            agent = DefaultAgent(model, env)
            if self.verbose:
                print(f"Running mini-swe-agent with model: {self.model_name}")
            output = agent.run(task)
            return MiniSweResult(success=True, output=str(output), model_used=self.model_name)
        except ImportError:
            return self._run_cli(task)
        except Exception as e:
            return MiniSweResult(success=False, output="", error=str(e))
    
    def _run_cli(self, task: str) -> MiniSweResult:
        """Run using mini CLI command."""
        try:
            result = subprocess.run(["mini", task], capture_output=True, text=True, timeout=self.timeout)
            if result.returncode == 0:
                return MiniSweResult(success=True, output=result.stdout, model_used=self.model_name)
            return MiniSweResult(success=False, output=result.stdout, error=result.stderr)
        except Exception as e:
            return MiniSweResult(success=False, output="", error=str(e))

def run_mini_swe_agent(task: str, model: str = "gpt-4o", timeout: int = 300) -> MiniSweResult:
    """Convenience function to run mini-swe-agent."""
    runner = MiniSweAgentRunner(model_name=model, timeout=timeout)
    return runner.run(task)

def is_mini_available() -> bool:
    """Check if mini-swe-agent is available."""
    try:
        from minisweagent import DefaultAgent
        return True
    except ImportError:
        try:
            result = subprocess.run(["mini", "--help"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
