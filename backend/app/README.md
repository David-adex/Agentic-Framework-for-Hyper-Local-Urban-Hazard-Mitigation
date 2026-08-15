# Backend Service

This backend implements a FastAPI application for ingesting geospatial sensor data, running anomaly detection, and providing agent-driven mitigation insights.

## Setup

1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the service from the backend directory using the project venv:
   ```powershell
   cd backend
   & "..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
   ```

## Endpoints

- `GET /health` — health status
- `GET /api/sensors/sample` — sample sensor data
- `POST /api/sensors` — ingest a sensor reading
- `GET /api/sensors/recent` — recent stored readings
- `GET /api/anomalies` — compute anomalies from recent data
- `POST /api/agent/query` — placeholder agent mitigation query
