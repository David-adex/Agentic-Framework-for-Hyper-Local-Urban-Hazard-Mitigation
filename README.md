# Agentic Framework for Hyper-Local Urban Hazard Mitigation

This repository is a scaffold for a Master’s project implementing an agentic cyber-physical system for hyper-local urban hazard mitigation.

Core components:
- `backend/` — Python FastAPI service with geospatial sensor ingestion, anomaly detection, MongoDB integration, and a local MCP-style agent layer.
- `frontend/` — React dashboard for visualizing sensor alerts, simulated microclimate hazards, and agent recommendations.

Quick start:
```powershell
cd backend
& "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001

bash
cd frontend
npm start
```
