import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.task_automation_agent import TaskAutomationAgent

def main():
    # Initialize the agent
    agent = TaskAutomationAgent()
    
    print("=" * 50)
    print("Task Automation Agent Example")
    print("=" * 50)
    
    # Example tasks
    tasks = [
        "Process data from database",
        "Schedule report generation",
        "Organize files in directory",
        "Analyze data patterns"
    ]
    
    # Execute tasks
    for task in tasks:
        print(f"\nExecuting: {task}")
        result = agent.execute(task)
        print(f"Status: {result['status']}")
        print(f"Result: {result.get('result', 'N/A')}")
    
    # Show agent status
    print("\n" + "=" * 50)
    status = agent.get_status()
    print(f"Agent: {status['name']}")
    print(f"Description: {status['description']}")
    print(f"Tasks Completed: {agent.tasks_completed}")
    
    # Show task history
    print("\nTask History:")
    for idx, task in enumerate(agent.get_task_history(), 1):
        print(f"{idx}. {task['task']} - {task['status']}")

if __name__ == "__main__":
    main()
