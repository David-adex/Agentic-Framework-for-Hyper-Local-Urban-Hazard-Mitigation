import os
from typing import Any, Dict, List

from anthropic import Anthropic
from anthropic.types import TextBlock

from .db import get_sensor_collection
from .schemas import AgentQuery, MitigationPlan


class MCPAgent:
    def __init__(self, collection=None):
        self.name = "hazard-mitigation-agent"
        self.collection = collection or get_sensor_collection()

    def _fetch_context(self, query: AgentQuery) -> List[dict]:
        longitude, latitude = query.location.coordinates
        near_filter = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "$maxDistance": 500,
                }
            }
        }

        try:
            nearby_docs = list(self.collection.find(near_filter))
            if not nearby_docs:
                nearby_docs = list(self.collection.find())
        except Exception as e:
            nearby_docs = list(self.collection.find().sort("timestamp", -1).limit(10))

        return sorted(
            nearby_docs,
            key=lambda doc: str(doc.get("timestamp") or ""),
            reverse=True,
        )[:10]

    def _build_prompt(self, query: AgentQuery, context: List[dict]) -> str:
        anomaly = query.anomaly
        context_text = "\n".join(
            [
                (
                    f"- sensor_id={doc.get('sensor_id')}, "
                    f"timestamp={doc.get('timestamp')}, "
                    f"temperature_c={doc.get('temperature_c')}, "
                    f"humidity_pct={doc.get('humidity_pct')}, "
                    f"pressure_hpa={doc.get('pressure_hpa')}, "
                    f"rainfall_mm={doc.get('rainfall_mm')}"
                )
                for doc in context
            ]
        ) or "No nearby sensor data available."

        return (
            "You are acting as an urban hazard mitigation agent. "
            "Use the following geospatial sensor context to decide the best localized response for an anomaly.\n\n"
            f"Event ID: {query.event_id}\n"
            f"Coordinates: {query.location.coordinates}\n"
            f"Anomaly metric: {anomaly.metric}\n"
            f"Anomaly value: {anomaly.value}\n"
            f"Z-score: {anomaly.z_score}\n"
            f"Description: {anomaly.description}\n\n"
            f"Nearby sensor context:\n{context_text}\n\n"
            "Return a concise but practical mitigation summary and 3 clear recommendations."
        )

    def generate_response(self, query: AgentQuery) -> MitigationPlan:
        context = self._fetch_context(query)
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            try:
                client = Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=400,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": self._build_prompt(query, context)}
                            ],
                        }
                    ],
                )
                block = response.content[0]
                if isinstance(block, TextBlock):
                     raw_text = block.text
                else:
                    raise ValueError(f"Expected a text block, got {type(block)}")
                if raw_text:
                    return MitigationPlan(
                        location=query.location,
                        summary=raw_text.strip(),
                        priority="high",
                        recommendations=[
                            "Alert the nearest urban infrastructure team.",
                            "Lower exposure for residents in the affected micro-zone.",
                            "Increase monitoring frequency for the next 30 minutes.",
                        ],
                    )
            except Exception:
                pass

        return self._fallback_response(query, context)

    def _fallback_response(self, query: AgentQuery, context: List[dict]) -> MitigationPlan:
        anomaly = query.anomaly
        latest = context[0] if context else {}
        summary = (
            f"Anomaly detected near {query.location.coordinates}: {anomaly.metric} reached {anomaly.value}. "
            f"The nearest sensor readings show pressure/rainfall conditions consistent with a local hazard."
        )
        if latest:
            summary += (
                f" Recent nearby conditions include pressure_hpa={latest.get('pressure_hpa')} and "
                f"rainfall_mm={latest.get('rainfall_mm')}."
            )

        recommendations = [
            "Issue a localized alert to residents in the affected block.",
            "Coordinate with drainage and transport operators to reduce exposure.",
            "Continue escalating sensor monitoring for the next 30 minutes.",
        ]

        return MitigationPlan(
            location=query.location,
            summary=summary,
            priority="high" if anomaly.z_score >= 2.5 else "medium",
            recommendations=recommendations,
        )

    def get_tool_metadata(self) -> Dict[str, Any]:
        return {
            "name": "sensor_data_tool",
            "description": "Returns nearby geospatial sensor context and anomaly details for the current hazard event.",
            "inputs": ["location", "metric", "timestamp", "event_id"],
        }
