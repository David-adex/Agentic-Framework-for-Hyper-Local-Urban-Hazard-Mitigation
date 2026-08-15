import sys
import json
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found.")
    print("   Install with: pip install requests")
    sys.exit(1)

API_BASE_URL = "http://127.0.0.1:8001"
AGENT_ENDPOINT = f"{API_BASE_URL}/api/agent/query"

TEST_SCENARIOS = [
    {
        "name": "🔥 Extreme Heat Alert",
        "event_id": "hazard-heat-001",
        "location": {"lat": 51.505, "lon": -0.090},
        "anomaly": {
            "sensor_id": "sensor-london-001",
            "metric": "temperature",
            "value": 38.5,
            "z_score": 3.2,
            "description": "Temperature spike detected - potential heat wave"
        }
    },
    {
        "name": "💧 Flash Flood Warning",
        "event_id": "hazard-flood-001",
        "location": {"lat": 51.515, "lon": -0.085},
        "anomaly": {
            "sensor_id": "sensor-london-002",
            "metric": "pressure",
            "value": 995.2,
            "z_score": 2.8,
            "description": "Barometric pressure drop detected - heavy rainfall incoming"
        }
    },
    {
        "name": "🌧️ Heavy Rainfall Alert",
        "event_id": "hazard-rain-001",
        "location": {"lat": 51.510, "lon": -0.095},
        "anomaly": {
            "sensor_id": "sensor-london-003",
            "metric": "rainfall",
            "value": 22.5,
            "z_score": 2.5,
            "description": "Significant rainfall detected - drainage systems at risk"
        }
    },
    {
        "name": "🌡️ Temperature Drop",
        "event_id": "hazard-cold-001",
        "location": {"lat": 51.520, "lon": -0.075},
        "anomaly": {
            "sensor_id": "sensor-london-004",
            "metric": "temperature",
            "value": -8.3,
            "z_score": 2.6,
            "description": "Extreme cold detected - frost formation risk"
        }
    }
]


def build_agent_query(scenario):
    return {
        "event_id": scenario["event_id"],
        "location": {
            "type": "Point",
            "coordinates": [scenario["location"]["lon"], scenario["location"]["lat"]]
        },
        "anomaly": {
            "sensor_id": scenario["anomaly"]["sensor_id"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metric": scenario["anomaly"]["metric"],
            "value": scenario["anomaly"]["value"],
            "z_score": scenario["anomaly"]["z_score"],
            "is_anomaly": True,
            "description": scenario["anomaly"]["description"]
        }
    }


def query_agent(scenario):
    query = build_agent_query(scenario)
    
    try:
        response = requests.post(
            AGENT_ENDPOINT,
            json=query,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - is backend running on 127.0.0.1:8001?"
    except requests.exceptions.Timeout:
        return False, "Request timeout - agent may be calling external API"
    except Exception as e:
        return False, str(e)


def print_mitigation_plan(plan):
    print()
    print("  📋 MITIGATION PLAN:")
    print(f"    Priority: {plan.get('priority', 'N/A').upper()}")
    print()
    print("    Summary:")
    for line in plan.get('summary', '').split('\n'):
        if line.strip():
            print(f"      {line.strip()}")
    print()
    print("    Recommendations:")
    for i, rec in enumerate(plan.get('recommendations', []), 1):
        print(f"      {i}. {rec}")
    print()


def main():
    print("=" * 80)
    print("Agent Query Test Suite")
    print("=" * 80)
    print()
    
    print("🔌 Checking API connectivity...")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5).json()
        print(f"✅ API is running: {health.get('message', 'OK')}")
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        print("   Make sure backend is running on 127.0.0.1:8001")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("Running Test Scenarios")
    print("=" * 80)
    print()
    
    success_count = 0
    
    for scenario in TEST_SCENARIOS:
        print(f"{scenario['name']}")
        print("-" * 80)
        print(f"  Event ID: {scenario['event_id']}")
        print(f"  Location: ({scenario['location']['lat']}, {scenario['location']['lon']})")
        print(f"  Anomaly: {scenario['anomaly']['description']}")
        print(f"  Metric: {scenario['anomaly']['metric']} = {scenario['anomaly']['value']}")
        print(f"  Z-Score: {scenario['anomaly']['z_score']}")
        print()
        
        success, result = query_agent(scenario)
        
        if success:
            print_mitigation_plan(result)
            print("  ✅ Agent successfully processed hazard event")
            success_count += 1
        else:
            print(f"  ❌ Failed to query agent: {result}")
            print()
        
        print()
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {success_count}/{len(TEST_SCENARIOS)} scenarios")
    print()
    
    if success_count == len(TEST_SCENARIOS):
        print("🎉 All tests passed! The agent is working correctly.")
        print()
        print("💡 The agentic framework successfully:")
        print("   • Received anomaly events")
        print("   • Fetched contextual sensor data")
        print("   • Generated mitigation recommendations")
        print("   • Prioritized hazard responses")
    else:
        print("⚠️  Some tests failed. Check your setup:")
        print("   • Backend running on 127.0.0.1:8001?")
        print("   • MongoDB connection working?")
        print("   • ANTHROPIC_API_KEY set in .env? (optional for fallback)")
    
    print()
    print("Next steps:")
    print("  1. Check live dashboard: http://localhost:3000")
    print("  2. View detected anomalies: GET http://127.0.0.1:8001/api/anomalies")
    print("  3. Ingest more data: python ingest_sensor_data.py")
    print()


if __name__ == "__main__":
    main()
