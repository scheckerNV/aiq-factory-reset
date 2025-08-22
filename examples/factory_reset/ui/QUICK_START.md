# 🚀 Quick Start Guide

Get your DCGM Agent Chat UI running in under 2 minutes!

## One-Command Start

```bash
cd examples/factory_reset/ui/
./start_ui.sh
```

That's it! The script will handle everything:
- ✅ Check dependencies (Python 3.8+, Node.js 18+)
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Build the frontend
- ✅ Start both servers

## What You'll Get

🌐 **Frontend**: http://localhost:3000
🔧 **Backend API**: http://localhost:8000
📋 **API Docs**: http://localhost:8000/docs

## First Steps

1. **Open** http://localhost:3000 in your browser
2. **Try these example queries**:
   - "Show me the current GPU status"
   - "Run a quick diagnostic on all GPUs"
   - "Start the monitoring stack"

3. **Watch the magic**:
   - See tools executing in real-time on the right panel
   - View detailed execution results
   - Get comprehensive responses

## Development Mode

For development with auto-reload:
```bash
./dev.sh
```

## Stopping the Services

Press `Ctrl+C` in the terminal where you started the services.

## Troubleshooting

**Problem**: Script fails with permission error
**Solution**: `chmod +x start_ui.sh`

**Problem**: "Command not found" errors
**Solution**: Install the missing dependency:
- Python 3: https://python.org/downloads/
- Node.js: https://nodejs.org/

**Problem**: Backend won't start
**Solution**: Check that you're in the right directory and `dcgm_agent.yml` exists

Need more help? Check the full [README.md](README.md) for detailed documentation.

---

🎉 **You're ready to chat with your DCGM agent!**
