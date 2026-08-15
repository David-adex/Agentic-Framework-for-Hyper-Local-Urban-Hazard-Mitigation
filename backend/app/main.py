from fastapi import FastAPI
from .api import router as api_router

app = FastAPI(
    title="Agentic Urban Hazard Mitigation API",
    description="Backend service for geospatial sensor monitoring, anomaly detection, and MCP-style agent orchestration.",
    version="0.1.0",
)
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Agentic hazard mitigation backend running."}
