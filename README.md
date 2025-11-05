# AI Agents Project

AI Agents Project - Intelligent agents for various automation tasks

## Overview

This project provides a framework for creating and managing AI agents that can automate various tasks. The system includes a base agent architecture and specialized agents for different automation needs.

## Features

- 🤖 Base agent framework with extensible architecture
- 🔄 Task Automation Agent for repetitive workflows
- 📊 Task tracking and history
- ✅ Comprehensive test coverage
- 🚀 Easy to extend with new agent types

## Project Structure

```
ai-agents/
├── src/
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py           # Base agent class
│       └── task_automation_agent.py # Task automation implementation
├── tests/
│   ├── __init__.py
│   ├── test_base_agent.py          # Tests for base agent
│   └── test_task_automation_agent.py # Tests for automation agent
├── examples/
│   └── task_automation_example.py   # Usage examples
└── requirements.txt
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/R-c-8008/ai-agents.git
cd ai-agents
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from src.agents.task_automation_agent import TaskAutomationAgent

# Create an agent
agent = TaskAutomationAgent()

# Execute a task
result = agent.execute("Process data from database")
print(result)

# Check status
status = agent.get_status()
print(f"Tasks completed: {agent.tasks_completed}")
```

### Running Examples

```bash
python examples/task_automation_example.py
```

## Creating Custom Agents

Extend the `BaseAgent` class to create your own agents:

```python
from src.agents.base_agent import BaseAgent
from typing import Dict, Any

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyCustomAgent",
            description="My custom agent description"
        )
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        # Your custom logic here
        return {"status": "success", "result": "Task completed"}
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Development

### Code Quality

Run linting:
```bash
flake8 .
```

Format code:
```bash
black .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [x] Base agent framework
- [x] Task Automation Agent
- [ ] Web Scraping Agent
- [ ] Data Analysis Agent
- [ ] Integration with LLMs (OpenAI, Claude)
- [ ] Agent orchestration and chaining
- [ ] Web API interface

## Author

Raghavendra Chary Kurella
- GitHub: [@Raghavendracharykurella](https://github.com/Raghavendracharykurella)
