from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.state = {}
        logger.info(f"Agent '{self.name}' initialized")
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "state": self.state
        }
    
    def update_state(self, key: str, value: Any) -> None:
        """Update agent state"""
        self.state[key] = value
        logger.info(f"Agent '{self.name}' state updated: {key}={value}")
