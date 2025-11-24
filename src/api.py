from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import logging
from src.agents.agent_orchestrator import AgentOrchestrator
from src.agents.task_automation_agent import TaskAutomationAgent
from src.agents.web_scraping_agent import WebScrapingAgent
from src.agents.data_analysis_agent import DataAnalysisAgent
from src.agents.llm_integration_agent import LLMIntegrationAgent

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agents API",
    description="REST API for AI agent management and execution",
    version="1.0.0",
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Request/Response Models
class AgentExecuteRequest(BaseModel):
    agent_name: str
    task: str
    kwargs: Optional[Dict[str, Any]] = {}

class AgentChainRequest(BaseModel):
    chain: List[Dict[str, Any]]

class AgentRegisterRequest(BaseModel):
    agent_type: str
    agent_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "AI Agents API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {"agents": orchestrator.list_agents()}

@app.post("/agents/register")
async def register_agent(request: AgentRegisterRequest):
    """Register a new agent"""
    try:
        agent_type = request.agent_type.lower()

        if agent_type == "task_automation":
            agent = TaskAutomationAgent()
        elif agent_type == "web_scraping":
            agent = WebScrapingAgent()
        elif agent_type == "data_analysis":
            agent = DataAnalysisAgent()
        elif agent_type == "llm_integration":
            provider = request.config.get("provider", "openai")
            api_key = request.config.get("api_key")
            agent = LLMIntegrationAgent(provider=provider, api_key=api_key)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

        orchestrator.register_agent(agent, request.agent_name)

        return {
            "status": "success",
            "agent_name": request.agent_name or agent.name,
            "agent_type": agent_type,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/execute")
async def execute_agent(request: AgentExecuteRequest):
    """Execute a specific agent"""
    try:
        result = orchestrator.execute_agent(
            request.agent_name,
            request.task,
            **request.kwargs
        )

        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/chain")
async def execute_chain(request: AgentChainRequest):
    """Execute a chain of agent tasks"""
    try:
        results = orchestrator.execute_chain(request.chain)
        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    try:
        status = orchestrator.get_agent_status(agent_name)

        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])

        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_name}")
async def unregister_agent(agent_name: str):
    """Unregister an agent"""
    try:
        orchestrator.unregister_agent(agent_name)
        return {"status": "success", "message": f"Agent {agent_name} unregistered"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_execution_history():
    """Get execution history"""
    return {"history": orchestrator.get_execution_history()}

@app.delete("/history")
async def clear_history():
    """Clear execution history"""
    orchestrator.clear_history()
    return {"status": "success", "message": "History cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
