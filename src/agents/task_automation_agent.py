from typing import Any, Dict, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TaskAutomationAgent(BaseAgent):
    """Agent for automating various tasks"""
    
    def __init__(self):
        super().__init__(
            name="TaskAutomationAgent",
            description="Automates repetitive tasks and workflows"
        )
        self.tasks_completed = 0
        self.task_history = []
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute an automation task"""
        logger.info(f"Executing task: {task}")
        
        try:
            # Parse task and execute
            result = self._process_task(task, **kwargs)
            
            # Update tracking
            self.tasks_completed += 1
            self.task_history.append({
                "task": task,
                "status": "success",
                "result": result
            })
            
            return {
                "status": "success",
                "task": task,
                "result": result,
                "tasks_completed": self.tasks_completed
            }
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "status": "failed",
                "task": task,
                "error": str(e)
            }
    
    def _process_task(self, task: str, **kwargs) -> str:
        """Process the task based on type"""
        task_lower = task.lower()
        
        if "file" in task_lower:
            return self._handle_file_task(task, **kwargs)
        elif "data" in task_lower:
            return self._handle_data_task(task, **kwargs)
        elif "schedule" in task_lower:
            return self._handle_schedule_task(task, **kwargs)
        else:
            return f"Task '{task}' processed successfully"
    
    def _handle_file_task(self, task: str, **kwargs) -> str:
        """Handle file-related tasks"""
        return f"File task completed: {task}"
    
    def _handle_data_task(self, task: str, **kwargs) -> str:
        """Handle data processing tasks"""
        return f"Data task completed: {task}"
    
    def _handle_schedule_task(self, task: str, **kwargs) -> str:
        """Handle scheduling tasks"""
        return f"Schedule task completed: {task}"
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get history of completed tasks"""
        return self.task_history
