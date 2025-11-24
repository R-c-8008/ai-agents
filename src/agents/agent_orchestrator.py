from typing import Any, Dict, List, Optional
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents to work together"""

    def __init__(self):
        self.agents = {}
        self.execution_history = []
        logger.info("AgentOrchestrator initialized")

    def register_agent(self, agent: BaseAgent, name: Optional[str] = None):
        """Register an agent with the orchestrator"""
        agent_name = name or agent.name
        self.agents[agent_name] = agent
        logger.info(f"Registered agent: {agent_name}")

    def unregister_agent(self, name: str):
        """Unregister an agent"""
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Unregistered agent: {name}")

    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())

    def execute_agent(self, agent_name: str, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific agent"""
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found"
            logger.error(error_msg)
            return {"status": "failed", "error": error_msg}

        agent = self.agents[agent_name]
        result = agent.execute(task, **kwargs)

        self.execution_history.append({
            "agent": agent_name,
            "task": task,
            "result": result,
        })

        return result

    def execute_chain(self, chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a chain of agent tasks"""
        results = []
        previous_result = None

        for step in chain:
            agent_name = step.get("agent")
            task = step.get("task")
            kwargs = step.get("kwargs", {})

            # Allow passing previous result to next step
            if step.get("use_previous_result") and previous_result:
                kwargs["previous_result"] = previous_result

            result = self.execute_agent(agent_name, task, **kwargs)
            results.append(result)
            previous_result = result

            # Stop chain if any step fails
            if result.get("status") == "failed" and not step.get("continue_on_error"):
                logger.warning(f"Chain stopped at step {len(results)} due to failure")
                break

        return results

    def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple agent tasks in parallel (simulated)"""
        results = []

        for task_config in tasks:
            agent_name = task_config.get("agent")
            task = task_config.get("task")
            kwargs = task_config.get("kwargs", {})

            result = self.execute_agent(agent_name, task, **kwargs)
            results.append(result)

        return results

    def create_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]):
        """Create a reusable workflow"""
        if not hasattr(self, "workflows"):
            self.workflows = {}

        self.workflows[workflow_name] = steps
        logger.info(f"Created workflow: {workflow_name}")

    def execute_workflow(self, workflow_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a saved workflow"""
        if not hasattr(self, "workflows") or workflow_name not in self.workflows:
            error_msg = f"Workflow '{workflow_name}' not found"
            logger.error(error_msg)
            return [{"status": "failed", "error": error_msg}]

        steps = self.workflows[workflow_name]
        return self.execute_chain(steps)

    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        if agent_name not in self.agents:
            return {"error": f"Agent '{agent_name}' not found"}

        return self.agents[agent_name].get_status()

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all agent executions"""
        return self.execution_history

    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
        logger.info("Execution history cleared")
