from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

from .schemas import SensorReading, AnomalyResult


def generate_dummy_sensor_data(center: List[float], count: int = 20) -> List[SensorReading]:
    now = datetime.utcnow()
    readings = []
    for i in range(count):
        lat = center[1] + np.random.normal(scale=0.003)
        lon = center[0] + np.random.normal(scale=0.003)
        reading = SensorReading(
            sensor_id=f"sensor-{i+1}",
            timestamp=now - timedelta(minutes=5 * i),
            location={"type": "Point", "coordinates": [lon, lat]},
            temperature_c=20 + np.random.normal(scale=4),
            humidity_pct=55 + np.random.normal(scale=10),
            pressure_hpa=1010 + np.random.normal(scale=4),
            rainfall_mm=max(0.0, np.random.normal(loc=0.4, scale=0.6)),
            pollutant_index=max(0.0, np.random.normal(loc=40, scale=20)),
        )
        readings.append(reading)
    return readings


def rolling_z_scores(values: List[float], window: int = 10) -> List[float]:
    z_scores = []
    for i in range(len(values)):
        window_values = values[max(0, i - window + 1) : i + 1]
        mean = np.mean(window_values)
        std = np.std(window_values, ddof=0)
        z = 0.0 if std == 0 else (values[i] - mean) / std
        z_scores.append(float(z))
    return z_scores


def detect_anomalies(readings: List[SensorReading]) -> List[AnomalyResult]:
    pressures = [r.pressure_hpa for r in readings]
    rainfalls = [r.rainfall_mm for r in readings]
    pressure_z = rolling_z_scores(pressures, window=10)
    rainfall_z = rolling_z_scores(rainfalls, window=10)
    anomalies: List[AnomalyResult] = []
    for idx, reading in enumerate(readings):
        if abs(pressure_z[idx]) >= 2.5:
            anomalies.append(
                AnomalyResult(
                    sensor_id=reading.sensor_id,
                    timestamp=reading.timestamp,
                    metric="pressure_hpa",
                    value=reading.pressure_hpa,
                    z_score=pressure_z[idx],
                    is_anomaly=True,
                    description="Rapid barometric pressure change indicates a potential storm or flash flood trigger.",
                )
            )
        if rainfall_z[idx] >= 2.0:
            anomalies.append(
                AnomalyResult(
                    sensor_id=reading.sensor_id,
                    timestamp=reading.timestamp,
                    metric="rainfall_mm",
                    value=reading.rainfall_mm,
                    z_score=rainfall_z[idx],
                    is_anomaly=True,
                    description="Unusually heavy rainfall detected relative to recent history.",
                )
            )
    return anomalies
