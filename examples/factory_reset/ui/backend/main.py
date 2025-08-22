#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2024-2025,
# NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import yaml
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add the parent directory to the path to import AIQ modules
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DCGM Agent Chat UI", version="1.0.0")

# Enable CORS for development (support multiple frontend ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",  # Default Next.js
        "http://localhost:3001",
        "http://127.0.0.1:3001",  # Alt port 1
        "http://localhost:3100",
        "http://127.0.0.1:3100",  # Alt port 2
        "http://localhost:8080",
        "http://127.0.0.1:8080",  # Backend (for docs)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ToolExecution(BaseModel):
    tool_name: str
    status: str  # "started", "completed", "error"
    input: Optional[Dict[str, Any]] = None
    output: Optional[Any] = None
    timestamp: datetime
    execution_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_executions: List[ToolExecution]
    total_time: float


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)


manager = ConnectionManager()


class AIQWorkflowRunner:

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.available_tools = self._extract_available_tools()

    def _load_config(self) -> Dict[str, Any]:
        """Load the AIQ workflow configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load AIQ configuration: {e}")

    def _extract_available_tools(self) -> List[str]:
        """Extract available tools from the configuration"""
        try:
            return list(self.config.get('functions', {}).keys())
        except Exception:
            return []

    async def execute_workflow(self, message: str, session_id: str) -> ChatResponse:
        """Execute the AIQ workflow and track tool usage"""
        start_time = asyncio.get_event_loop().time()
        tool_executions = []

        # Create a custom callback to track tool executions
        async def tool_callback(tool_name: str, status: str, **kwargs):
            execution = ToolExecution(tool_name=tool_name,
                                      status=status,
                                      input=kwargs.get('input'),
                                      output=kwargs.get('output'),
                                      timestamp=datetime.utcnow(),
                                      execution_id=str(uuid.uuid4()))
            tool_executions.append(execution)

            # Send real-time update via WebSocket
            await manager.send_personal_message({"type": "tool_execution", "data": execution.dict()}, session_id)

        try:
            # Send initial message
            await manager.send_personal_message(
                {
                    "type": "status", "data": {
                        "message": "Processing your request...", "status": "processing"
                    }
                },
                session_id)

            # Run the workflow
            result = await self._run_workflow_with_tracking(message, tool_callback)

            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time

            response = ChatResponse(response=result,
                                    session_id=session_id,
                                    tool_executions=tool_executions,
                                    total_time=total_time)

            # Send completion message
            await manager.send_personal_message({"type": "response_complete", "data": response.dict()}, session_id)

            return response

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            await manager.send_personal_message({"type": "error", "data": {"message": f"Error: {str(e)}"}}, session_id)
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {e}")

    async def _run_workflow_with_tracking(self, message: str, tool_callback) -> str:
        """Run the workflow and capture tool executions"""
        try:
            # Set up environment for AIQ workflow
            import asyncio
            import os
            import sys
            from pathlib import Path

            venv_bin = Path(sys.executable).parent
            env = os.environ.copy()
            env["PATH"] = str(venv_bin) + os.pathsep + env.get("PATH", "")
            aiq_bin = venv_bin / "aiq"
            if aiq_bin.exists():
                cmd = [str(aiq_bin), "run", "--config_file", str(self.config_path), "--input", message]
            else:
                cmd = [
                    sys.executable,
                    "-m",
                    "aiq.cli.main",
                    "run",
                    "--config_file",
                    str(self.config_path),
                    "--input",
                    message
                ]

            result = await asyncio.create_subprocess_exec(*cmd,
                                                          stdout=asyncio.subprocess.PIPE,
                                                          stderr=asyncio.subprocess.PIPE,
                                                          env=env)

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                output = stdout.decode('utf-8').strip()
                return output if output else "Task completed successfully"
            else:
                error_msg = stderr.decode('utf-8').strip()
                logger.error(f"AIQ workflow failed: {error_msg}")

                # Handle common authentication errors gracefully
                if ("401" in error_msg and "Unauthorized" in error_msg) or ("openai" in error_msg.lower()
                                                                            and "api" in error_msg.lower()):
                    return ("Authentication required for LLM. Please set up your API credentials:\n"
                            "• For NVIDIA NIM: Set your NVIDIA API key\n"
                            "• For OpenAI: Set OPENAI_API_KEY environment variable\n\n"
                            "The DCGM agent configuration is working correctly - you have access to these tools:\n"
                            f"• {', '.join(self.available_tools)}\n\n"
                            "To test without authentication, you can call the tools directly from the UI.")

                return f"Workflow execution failed: {error_msg}"

        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            return f"Error executing workflow: {str(e)}"

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get information about available tools"""
        tools_info = []
        for tool_name in self.available_tools:
            tool_config = self.config.get('functions', {}).get(tool_name, {})
            tools_info.append({
                "name": tool_name,
                "type": tool_config.get('_type', 'unknown'),
                "description": self._get_tool_description(tool_name)
            })
        return tools_info

    def _get_tool_description(self, tool_name: str) -> str:
        """Get tool description from the code or config"""
        descriptions = {
            "gpu_status": "Get GPU health and usage status",
            "gpu_run_diagnostics": "Run DCGM diagnostics on GPUs",
            "gpu_enable_health": "Enable DCGM background health checks",
            "gpu_nvlink_status": "Check NVLink connectivity status",
            "prom_stack_start": "Start Prometheus monitoring stack",
            "prom_query": "Query Prometheus for metrics",
            "grafana_create_dashboard": "Create Grafana dashboards"
        }
        return descriptions.get(tool_name, f"AIQ tool: {tool_name}")


# Initialize the workflow runner
# Use test config by default (works without API keys), can be overridden with env var
config_name = os.getenv("DCGM_CONFIG", "dcgm_agent.yml")
config_path = Path(__file__).parent.parent.parent / "src" / "aiq_dgx_factory_reset" / "configs" / config_name
workflow_runner = AIQWorkflowRunner(str(config_path))


@app.get("/")
async def root():
    return {"message": "DCGM Agent Chat UI Backend", "status": "running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "available_tools": len(workflow_runner.available_tools),
        "config_path": str(workflow_runner.config_path)
    }


@app.get("/tools")
async def get_available_tools():
    """Get information about available tools"""
    return {"tools": workflow_runner.get_available_tools(), "count": len(workflow_runner.available_tools)}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint"""
    session_id = chat_message.session_id or str(uuid.uuid4())

    try:
        response = await workflow_runner.execute_workflow(message=chat_message.message, session_id=session_id)
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, session_id)
    try:
        # Send initial connection message
        await manager.send_personal_message(
            {
                "type": "connected",
                "data": {
                    "session_id": session_id, "available_tools": workflow_runner.get_available_tools()
                }
            },
            session_id)

        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Handle any client messages if needed
                message_data = json.loads(data)
                if message_data.get("type") == "ping":
                    await manager.send_personal_message(
                        {
                            "type": "pong", "data": {
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        }, session_id)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for {session_id}: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(session_id)


# Mount static files (for serving the frontend if needed)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="info")
