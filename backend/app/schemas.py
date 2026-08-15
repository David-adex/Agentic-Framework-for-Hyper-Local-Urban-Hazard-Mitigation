from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class GeometryType(str, Enum):
    Point = "Point"

class GeoPoint(BaseModel):
    type: GeometryType = GeometryType.Point
    coordinates: List[float] = Field(..., description="Longitude and latitude")

class SensorReading(BaseModel):
    sensor_id: str
    timestamp: datetime
    location: GeoPoint
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float
    rainfall_mm: float
    pollutant_index: Optional[float] = None

class AnomalyResult(BaseModel):
    sensor_id: str
    timestamp: datetime
    metric: str
    value: float
    z_score: float
    is_anomaly: bool
    description: str

class MitigationPlan(BaseModel):
    location: GeoPoint
    summary: str
    priority: str
    recommendations: List[str]

class AgentQuery(BaseModel):
    event_id: str
    location: GeoPoint
    anomaly: AnomalyResult
