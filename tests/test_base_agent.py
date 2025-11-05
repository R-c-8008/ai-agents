import pytest
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""

    def execute(self, task: str, **kwargs):
        return {"status": "success", "task": task}


def test_agent_initialization():
    agent = TestAgent("TestAgent", "Test Description")
    assert agent.name == "TestAgent"
    assert agent.description == "Test Description"
    assert agent.state == {}


def test_agent_get_status():
    agent = TestAgent("TestAgent", "Test Description")
    status = agent.get_status()
    assert status["name"] == "TestAgent"
    assert status["description"] == "Test Description"
    assert "state" in status


def test_agent_update_state():
    agent = TestAgent("TestAgent")
    agent.update_state("key1", "value1")
    assert agent.state["key1"] == "value1"


def test_agent_execute():
    agent = TestAgent("TestAgent")
    result = agent.execute("test task")
    assert result["status"] == "success"
    assert result["task"] == "test task"
