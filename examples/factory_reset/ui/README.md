# DCGM Agent Chat UI

A modern, interactive web interface for the DCGM (Data Center GPU Manager) agent. This UI provides a chatbot-style interface for GPU monitoring, diagnostics, and management tasks.

## Features

### 🎯 Key Capabilities
- **Interactive Chat Interface**: Natural language interaction with your DCGM agent
- **Real-time Tool Tracking**: See which tools are being executed in real-time
- **Dynamic Tool Discovery**: Automatically adapts to changes in your agent configuration
- **WebSocket Integration**: Live updates of tool execution status
- **Modern UI**: Built with React/Next.js and Tailwind CSS
- **Responsive Design**: Works on desktop and mobile devices

### 🛠 Available Tools
The UI automatically discovers and displays available tools from your DCGM agent:
- `gpu_status` - Get GPU health and usage status
- `gpu_run_diagnostics` - Run DCGM diagnostics on GPUs
- `gpu_enable_health` - Enable DCGM background health checks
- `gpu_nvlink_status` - Check NVLink connectivity status
- `prom_stack_start` - Start Prometheus monitoring stack
- `prom_query` - Query Prometheus for metrics
- `grafana_create_dashboard` - Create Grafana dashboards

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   AIQ Agent     │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│  (DCGM Tools)   │
│                 │    │                 │    │                 │
│ • Chat UI       │    │ • WebSocket     │    │ • GPU Status    │
│ • Real-time     │    │ • Tool Tracking │    │ • Diagnostics   │
│ • Tool Display  │    │ • AIQ Interface │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- Access to GPUs with DCGM installed

### Option 1: Quick Start Script (Recommended)
```bash
# Navigate to the UI directory
cd examples/factory_reset/ui/

# Run the startup script (handles all setup)
./start_ui.sh
```

The script will:
1. Check dependencies
2. Create Python virtual environment
3. Install Python and Node.js dependencies
4. Build the frontend
5. Start both backend and frontend servers

### Option 2: Development Mode
For development with auto-reload:
```bash
cd examples/factory_reset/ui/
./dev.sh
```

### Option 3: Manual Setup
1. **Backend Setup**:
   ```bash
   cd examples/factory_reset/ui/backend/
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt

   # Install AIQ package
   cd ../../
   pip install -e .

   # Start backend
   cd ui/backend/
   python main.py
   ```

2. **Frontend Setup**:
   ```bash
   cd examples/factory_reset/ui/frontend/
   npm install
   npm run build
   npm start
   ```

### Option 4: Docker (Production)
```bash
cd examples/factory_reset/ui/
docker-compose up -d
```

## Usage

1. **Open the UI**: Navigate to http://localhost:3000
2. **Start Chatting**: Type your questions or requests in the chat input
3. **Watch Tool Execution**: See real-time updates as tools are executed
4. **View Results**: Get comprehensive responses with execution details

### Example Queries
- "Show me the current GPU status"
- "Run a quick diagnostic on all GPUs"
- "Check NVLink connectivity"
- "Start the monitoring stack"
- "Create a Grafana dashboard for GPU monitoring"

## Configuration

### Backend Configuration
The backend automatically loads configuration from:
```
examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml
```

### Environment Variables
- `PYTHONPATH`: Set to include your AIQ source directory
- `GRAFANA_ADMIN_PASSWORD`: Password for Grafana admin user (default: admin)
- `PROM_URL`: Prometheus URL (default: http://localhost:9090)
- `GRAFANA_URL`: Grafana URL (default: http://localhost:3000)

### Frontend Configuration
- API endpoint is automatically configured via Next.js rewrites
- WebSocket connection uses the same port as the API (8000)

## Customization

### Adding New Tools
1. Add your new function to `dcgm_register.py` using the `@register_function` decorator
2. Update `dcgm_agent.yml` to include the new tool in the workflow configuration
3. Restart the UI - it will automatically discover the new tool

### Modifying the UI
The UI is designed to be adaptable:
- **Tool descriptions**: Modify the `_get_tool_description()` method in `backend/main.py`
- **UI components**: Edit React components in `frontend/src/components/`
- **Styling**: Modify Tailwind classes or add custom CSS
- **Tool icons**: Update the `getToolIcon()` function in `ToolPanel.tsx`

## API Endpoints

### REST API
- `GET /` - Health check
- `GET /health` - Detailed health information
- `GET /tools` - List available tools
- `POST /chat` - Send chat message
- `GET /docs` - Interactive API documentation

### WebSocket
- `WS /ws/{session_id}` - Real-time updates

## Development

### Project Structure
```
ui/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main backend application
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js 13+ app router
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── styles/        # CSS styles
│   │   └── types/         # TypeScript types
│   ├── package.json       # Node.js dependencies
│   └── next.config.js     # Next.js configuration
├── docker-compose.yml      # Docker composition
├── Dockerfile.backend      # Backend Docker image
├── Dockerfile.frontend     # Frontend Docker image
├── start_ui.sh            # Production startup script
├── dev.sh                 # Development startup script
└── README.md              # This file
```

### Key Components
- **ChatMessage**: Displays individual chat messages with tool execution details
- **ToolExecution**: Shows real-time tool execution status
- **ToolPanel**: Sidebar showing available tools and current executions
- **useChat**: React hook managing WebSocket connection and chat state

## Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check if `dcgm_agent.yml` exists in the expected location
   - Ensure Python virtual environment is activated
   - Verify AIQ package is installed (`pip install -e .`)

2. **Frontend can't connect to backend**:
   - Ensure backend is running on port 8000
   - Check browser console for WebSocket connection errors
   - Verify CORS settings if accessing from different domain

3. **Tools not showing**:
   - Check `dcgm_agent.yml` configuration
   - Verify tools are properly registered in `dcgm_register.py`
   - Check backend logs for configuration loading errors

4. **Docker issues**:
   - Ensure Docker and docker-compose are installed
   - Check if ports 3000 and 8000 are available
   - Review container logs: `docker-compose logs`

### Logs and Debugging
- **Backend logs**: Check console output where you started the backend
- **Frontend logs**: Check browser console (F12)
- **Docker logs**: `docker-compose logs dcgm-chat-backend` or `docker-compose logs dcgm-chat-frontend`

## Performance Considerations

- The UI limits message lengths to 2000 characters
- Tool execution outputs are truncated for display (configurable in backend)
- WebSocket connections auto-reconnect after 3 seconds if disconnected
- Frontend includes virtual scrolling for large message lists

## Security Notes

- The UI is designed for internal/development use
- No authentication is implemented by default
- WebSocket connections are not encrypted (use reverse proxy for production)
- Consider implementing rate limiting for production deployments

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Update documentation for significant changes
4. Test both development and production builds

## License

This project follows the same license as the parent AIQ project.
