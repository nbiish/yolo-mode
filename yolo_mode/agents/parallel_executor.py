"""
Contract-Aware Parallel Executor

Enhanced parallel execution with resource-aware task batching
and conservation law enforcement.

Based on Agent Contracts framework (arXiv:2601.08815, January 2025)
which ensures child contracts respect parent budget constraints.
"""

import time
from typing import List, Dict, Set, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Import OSA components
from .registry import AGENT_REGISTRY, OSARole, AgentConfig
from ..contracts import AgentContract, ResourceDimension, ConservationEnforcer


# ============================================================================
# TASK EXECUTION RESULT
# ============================================================================

@dataclass
class TaskResult:
    """Result of executing a task."""
    task_id: str
    task_description: str
    success: bool
    output: Optional[str] = None
    agent_used: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    resources_consumed: Dict[str, float] = field(default_factory=dict)


# ============================================================================
# CONTRACT-AWARE PARALLEL EXECUTOR
# ============================================================================

class ContractAwareExecutor:
    """
    Executes tasks in parallel while respecting contract constraints.

    Features:
    - Per-task resource allocation with child contracts
    - Conservation law enforcement across all parallel tasks
    - Dynamic batching based on remaining resources
    - Intelligent agent assignment for parallel execution
    """

    def __init__(
        self,
        contract: Optional[AgentContract] = None,
        max_workers: int = 3
    ):
        """
        Initialize parallel executor.

        Args:
            contract: Parent contract for resource governance
            max_workers: Maximum parallel workers (default: 3)
        """
        self.contract = contract
        self.max_workers = max_workers

        # Create conservation enforcer if contract provided
        self.conservation = ConservationEnforcer(contract) if contract else None

        # Track completed tasks
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.execution_history: List[TaskResult] = []

        # Thread-safe tracking
        self._lock = Lock()

    def execute_batch(
        self,
        tasks: List[str],
        agent_selector: Optional[Callable[[str], str]] = None
    ) -> List[TaskResult]:
        """
        Execute a batch of tasks in parallel with contract awareness.

        Args:
            tasks: List of task descriptions
            agent_selector: Optional function to select agent for each task

        Returns:
            List of TaskResult objects
        """
        if not self.contract:
            # No contract - simple parallel execution
            return self._execute_simple_parallel(tasks, agent_selector)

        # Contract-aware execution
        batches = self._plan_contract_aware_batches(tasks)

        all_results = []

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n📦 Executing Batch {batch_num}/{len(batches)} ({len(batch)} tasks)")

            # Create child contracts for this batch
            child_contracts = self._allocate_batch_contracts(len(batch))

            # Execute batch with child contracts
            batch_results = self._execute_batch_with_contracts(
                batch,
                child_contracts,
                agent_selector
            )

            all_results.extend(batch_results)

            # Report batch results
            completed = sum(1 for r in batch_results if r.success)
            print(f"   Batch {batch_num}: {completed}/{len(batch)} tasks completed")

        return all_results

    def _execute_simple_parallel(
        self,
        tasks: List[str],
        agent_selector: Optional[Callable[[str], str]]
    ) -> List[TaskResult]:
        """
        Execute tasks in parallel without contract constraints.

        Args:
            tasks: List of task descriptions
            agent_selector: Optional agent selector function

        Returns:
            List of TaskResult objects
        """
        results = []
        available_agents = list(AGENT_REGISTRY.keys())

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task_id, task in enumerate(tasks):
                agent = agent_selector(task) if agent_selector else "claude"
                future = executor.submit(self._execute_single_task, task, agent)
                future_to_task[future] = (task_id, task)

            # Collect results as they complete
            for future in as_completed(future_to_task.keys()):
                task_id, task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(TaskResult(
                        task_id=f"task_{task_id}",
                        task_description=task,
                        success=False,
                        error=str(e)
                    ))

        return results

    def _plan_contract_aware_batches(self, tasks: List[str]) -> List[List[str]]:
        """
        Plan execution batches respecting conservation laws.

        Creates batches where each batch has a child contract
        with allocated resources that sum to ≤ parent budget.

        Args:
            tasks: List of pending tasks

        Returns:
            List of task batches
        """
        if not self.contract or not self.conservation:
            # No contract - single batch with all tasks
            return [tasks]

        batches = []
        current_batch = []

        # Get parent contract status
        status = self.contract.get_status()
        max_util = status["max_utilization"]

        # Adjust batch size based on utilization
        if max_util > 0.8:
            # High utilization - smaller batches
            target_batch_size = 1
        elif max_util > 0.5:
            # Medium utilization - medium batches
            target_batch_size = 2
        else:
            # Low utilization - larger batches
            target_batch_size = min(self.max_workers, 3)

        for task in tasks:
            # Estimate task resources
            estimated = self._estimate_task_resources(task)

            # Check if we can add to current batch
            if self._can_add_to_batch(current_batch, estimated):
                current_batch.append(task)
            else:
                # Start new batch
                if current_batch:
                    batches.append(current_batch)
                current_batch = [task]

        # Don't forget the last batch
        if current_batch:
            batches.append(current_batch)

        return batches

    def _allocate_batch_contracts(self, batch_size: int) -> List[AgentContract]:
        """
        Allocate child contracts for a batch of tasks.

        Each child contract gets a portion of parent resources
        following conservation laws.

        Args:
            batch_size: Number of tasks in the batch

        Returns:
            List of allocated child contracts
        """
        if not self.conservation:
            return []

        contracts = []
        for _ in range(batch_size):
            child = self.conservation.create_child_contract()
            child.activate()
            contracts.append(child)

        return contracts

    def _execute_batch_with_contracts(
        self,
        batch: List[str],
        child_contracts: List[AgentContract],
        agent_selector: Optional[Callable[[str], str]]
    ) -> List[TaskResult]:
        """
        Execute a batch of tasks with their assigned child contracts.

        Args:
            batch: List of task descriptions
            child_contracts: Child contracts for each task
            agent_selector: Optional agent selector function

        Returns:
            List of TaskResult objects
        """
        results = []

        # Execute tasks in parallel with their contracts
        with ThreadPoolExecutor(max_workers=len(batch)) as executor:
            future_to_task = {}

            for i, (task, contract) in enumerate(zip(batch, child_contracts)):
                # Select agent for this task
                agent = agent_selector(task) if agent_selector else "claude"

                # Submit execution
                future = executor.submit(
                    self._execute_with_contract,
                    task,
                    agent,
                    contract
                )
                future_to_task[future] = (i, task, contract)

            # Collect results
            for future in as_completed(future_to_task.keys()):
                idx, task, contract = future_to_task[future]
                try:
                    result = future.result()

                    # Track contract completion
                    if result.success:
                        contract.evaluate_success(result.output, 1.0)
                    else:
                        contract.terminate("task_failed")

                    results.append(result)

                except Exception as e:
                    results.append(TaskResult(
                        task_id=f"task_{idx}",
                        task_description=task,
                        success=False,
                        error=str(e)
                    ))

        return results

    def _execute_with_contract(
        self,
        task: str,
        agent: str,
        contract: AgentContract
    ) -> TaskResult:
        """
        Execute a single task with contract tracking.

        Args:
            task: Task description
            agent: Agent to use
            contract: Child contract for this task

        Returns:
            TaskResult with resource tracking
        """
        start_time = time.time()

        # Check if contract allows proceeding
        can_proceed, reason = contract.can_proceed()
        if not can_proceed:
            return TaskResult(
                task_id=f"task_{hash(task)}",
                task_description=task,
                success=False,
                agent_used=agent,
                error=f"Contract constraint: {reason}"
            )

        # Import runner here to avoid circular imports
        from .runner import run_agent

        # Execute the task
        try:
            output = run_agent(agent, task, verbose=False)

            # Consume resources
            estimated_tokens = len(str(output)) // 4 if output else 0
            contract.consume_resource(ResourceDimension.TOKENS, estimated_tokens)
            contract.consume_resource(ResourceDimension.ITERATIONS, 1)

            execution_time = time.time() - start_time

            return TaskResult(
                task_id=f"task_{hash(task)}",
                task_description=task,
                success=True,
                output=output,
                agent_used=agent,
                execution_time=execution_time,
                resources_consumed={
                    "tokens": estimated_tokens,
                    "iterations": 1,
                    "time": execution_time
                }
            )

        except Exception as e:
            contract.terminate(f"execution_error: {str(e)}")
            return TaskResult(
                task_id=f"task_{hash(task)}",
                task_description=task,
                success=False,
                agent_used=agent,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def _execute_single_task(self, task: str, agent: str) -> TaskResult:
        """Execute a single task without contract tracking."""
        start_time = time.time()

        from .runner import run_agent

        try:
            output = run_agent(agent, task, verbose=False)
            return TaskResult(
                task_id=f"task_{hash(task)}",
                task_description=task,
                success=True,
                output=output,
                agent_used=agent,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return TaskResult(
                task_id=f"task_{hash(task)}",
                task_description=task,
                success=False,
                agent_used=agent,
                error=str(e)
            )

    def _estimate_task_resources(self, task: str) -> Dict[str, float]:
        """
        Estimate resource needs for a task.

        Args:
            task: Task description

        Returns:
            Dictionary with estimated resource requirements
        """
        # Simple heuristic based on task complexity
        words = len(task.split())

        return {
            "tokens": words * 50,  # Rough estimate
            "time": min(words * 0.5, 120),  # Cap at 2 minutes
            "iterations": 1
        }

    def _can_add_to_batch(self, batch: List[str], estimate: Dict) -> bool:
        """
        Check if task can be added to current batch.

        Args:
            batch: Current batch tasks
            estimate: Estimated resources for new task

        Returns:
            True if task fits in batch
        """
        if len(batch) >= self.max_workers:
            return False

        if not self.contract:
            return True

        # Check contract constraints
        can_proceed, _ = self.contract.can_proceed()
        return can_proceed

    def get_execution_stats(self) -> Dict:
        """
        Get statistics on task executions.

        Returns:
            Dictionary with execution statistics
        """
        if not self.execution_history:
            return {"message": "No executions yet"}

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful

        # Calculate average execution time
        times = [r.execution_time for r in self.execution_history if r.success]
        avg_time = sum(times) / len(times) if times else 0

        # Agent usage
        agent_usage = {}
        for result in self.execution_history:
            if result.agent_used:
                agent_usage[result.agent_used] = agent_usage.get(result.agent_used, 0) + 1

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_execution_time": avg_time,
            "agent_usage": agent_usage,
            "total_execution_time": sum(r.execution_time for r in self.execution_history)
        }

    def print_stats(self):
        """Print execution statistics."""
        stats = self.get_execution_stats()

        if "message" in stats:
            print(stats["message"])
            return

        print("\n=== Parallel Execution Statistics ===\n")
        print(f"Total executions: {stats['total_executions']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']*100:.1f}%")
        print(f"Average execution time: {stats['average_execution_time']:.2f}s")
        print(f"Total execution time: {stats['total_execution_time']:.2f}s")

        print("\nAgent usage:")
        for agent, count in stats['agent_usage'].items():
            print(f"  {agent}: {count} tasks")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_executor(
    contract: Optional[AgentContract] = None,
    max_workers: int = 3
) -> ContractAwareExecutor:
    """
    Factory function to create parallel executor.

    Args:
        contract: Optional contract for resource governance
        max_workers: Maximum parallel workers

    Returns:
        Configured executor instance
    """
    return ContractAwareExecutor(contract=contract, max_workers=max_workers)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    # Demo: Create executor and run parallel tasks
    print("=== Contract-Aware Parallel Executor Demo ===\n")

    from ..contracts import ContractFactory

    # Create a contract
    contract = ContractFactory.default()
    contract.activate()

    # Create executor
    executor = create_executor(contract=contract, max_workers=3)

    # Define some tasks
    tasks = [
        "Research Qwen CLI integration",
        "Implement agent registry module",
        "Write documentation for parallel executor",
    ]

    # Execute batch
    print(f"Executing {len(tasks)} tasks in parallel...\n")

    results = executor.execute_batch(tasks)

    # Show results
    print("\n=== Execution Results ===\n")
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"{status} Task {result.task_id}: {result.task_description[:50]}...")
        if result.success:
            print(f"   Agent: {result.agent_used}")
            print(f"   Time: {result.execution_time:.2f}s")
        else:
            print(f"   Error: {result.error}")

    # Show stats
    executor.print_stats()
