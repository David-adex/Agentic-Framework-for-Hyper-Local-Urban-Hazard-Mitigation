from datetime import datetime
from types import SimpleNamespace

from backend.app.agent import MCPAgent
from backend.app.schemas import AgentQuery, AnomalyResult, GeoPoint


class FakeCollection:
    def __init__(self, docs):
        self.docs = docs

    def find(self, *args, **kwargs):
        return self.docs


def test_agent_uses_mongo_context_for_model_prompt(monkeypatch):
    docs = [
        {
            "sensor_id": "sensor-1",
            "timestamp": "2026-08-14T12:00:00",
            "location": {"type": "Point", "coordinates": [-0.09, 51.50]},
            "temperature_c": 25.4,
            "humidity_pct": 72,
            "pressure_hpa": 995.8,
            "rainfall_mm": 12.2,
            "pollutant_index": 66,
        }
    ]

    class FakeMessages:
        def create(self, **kwargs):
            prompt = kwargs["messages"][-1]["content"][0]["text"]
            assert "sensor-1" in prompt
            assert "995.8" in prompt
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text="This is a localised flash-flood warning.")]
            )

    class FakeAnthropic:
        def __init__(self, *args, **kwargs):
            self.messages = FakeMessages()

    monkeypatch.setattr("backend.app.agent.Anthropic", FakeAnthropic)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    agent = MCPAgent(collection=FakeCollection(docs))
    query = AgentQuery(
        event_id="evt-1",
        location=GeoPoint(coordinates=[-0.09, 51.50]),
        anomaly=AnomalyResult(
            sensor_id="sensor-1",
            timestamp=datetime.utcnow(),
            metric="pressure_hpa",
            value=995.8,
            z_score=3.1,
            is_anomaly=True,
            description="Rapid pressure drop.",
        ),
    )

    result = agent.generate_response(query)
    assert "flash" in result.summary.lower()
    assert result.priority in {"high", "medium", "low"}


def test_agent_falls_back_to_local_recommendation_when_no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    agent = MCPAgent(collection=FakeCollection([]))
    query = AgentQuery(
        event_id="evt-2",
        location=GeoPoint(coordinates=[-0.1, 51.51]),
        anomaly=AnomalyResult(
            sensor_id="sensor-2",
            timestamp=datetime.utcnow(),
            metric="rainfall_mm",
            value=14.2,
            z_score=2.9,
            is_anomaly=True,
            description="High rainfall.",
        ),
    )

    result = agent.generate_response(query)
    assert "rainfall" in result.summary.lower() or "anomaly" in result.summary.lower()
    assert len(result.recommendations) >= 3
