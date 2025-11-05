import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.task_automation_agent import TaskAutomationAgent

def test_task_automation_agent_initialization():
    agent = TaskAutomationAgent()
    assert agent.name == "TaskAutomationAgent"
    assert agent.tasks_completed == 0
    assert len(agent.task_history) == 0

def test_execute_task_success():
    agent = TaskAutomationAgent()
    result = agent.execute("Process data")
    assert result["status"] == "success"
    assert agent.tasks_completed == 1
    assert len(agent.task_history) == 1

def test_multiple_tasks():
    agent = TaskAutomationAgent()
    tasks = ["Task 1", "Task 2", "Task 3"]
    
    for task in tasks:
        result = agent.execute(task)
        assert result["status"] == "success"
    
    assert agent.tasks_completed == 3
    assert len(agent.task_history) == 3

def test_file_task_handling():
    agent = TaskAutomationAgent()
    result = agent.execute("Organize files")
    assert result["status"] == "success"
    assert "File task completed" in result["result"]

def test_data_task_handling():
    agent = TaskAutomationAgent()
    result = agent.execute("Process data")
    assert result["status"] == "success"
    assert "Data task completed" in result["result"]

def test_get_task_history():
    agent = TaskAutomationAgent()
    agent.execute("Test task")
    history = agent.get_task_history()
    assert len(history) == 1
    assert history[0]["task"] == "Test task"
    assert history[0]["status"] == "success"
