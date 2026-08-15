from typing import List

from fastapi import APIRouter, HTTPException

from .agent import MCPAgent
from .db import get_sensor_collection
from .schemas import AgentQuery, AnomalyResult, MitigationPlan, SensorReading
from .sensor_data import detect_anomalies, generate_dummy_sensor_data

router = APIRouter()


@router.get("/sensors/sample", response_model=List[SensorReading])
def get_sample_sensors():
    center = [-0.090, 51.505]
    samples = generate_dummy_sensor_data(center, count=20)
    return samples


@router.post("/sensors", response_model=SensorReading)
def ingest_sensor_reading(reading: SensorReading):
    collection = get_sensor_collection()
    data = reading.model_dump()
    data["location"] = {
        "type": data["location"]["type"],
        "coordinates": data["location"]["coordinates"],
    }
    collection.insert_one(data)
    return reading


@router.get("/sensors/recent", response_model=List[SensorReading])
def recent_sensor_readings():
    collection = get_sensor_collection()
    rows = list(collection.find().sort("timestamp", -1).limit(50))
    return [
        SensorReading(**{k: v for k, v in row.items() if k != "_id"}) 
        for row in rows
    ]


@router.get("/anomalies", response_model=List[AnomalyResult])
def compute_anomalies():
    collection = get_sensor_collection()
    rows = list(collection.find().sort("timestamp", -1).limit(100))
    if not rows:
        return []
    readings = [
        SensorReading(**{k: v for k, v in row.items() if k != "_id"}) 
        for row in reversed(rows)
    ]
    anomalies = detect_anomalies(readings)
    return anomalies


@router.post("/agent/query", response_model=MitigationPlan)
def agent_query(query: AgentQuery):
    agent = MCPAgent()
    return agent.generate_response(query)
