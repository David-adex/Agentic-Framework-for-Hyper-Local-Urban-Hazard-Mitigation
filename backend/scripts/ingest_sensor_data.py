import sys
import json
import time
from datetime import datetime, timedelta
import random

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found.")
    print("   Install with: pip install requests")
    sys.exit(1)

API_BASE_URL = "http://127.0.0.1:8001"
SENSORS_ENDPOINT = f"{API_BASE_URL}/api/sensors"

SENSOR_LOCATIONS = [
    {"id": "sensor-london-001", "lat": 51.505, "lon": -0.090, "name": "Westminster"},
    {"id": "sensor-london-002", "lat": 51.515, "lon": -0.085, "name": "Holborn"},
    {"id": "sensor-london-003", "lat": 51.510, "lon": -0.095, "name": "Leicester Square"},
    {"id": "sensor-london-004", "lat": 51.520, "lon": -0.075, "name": "East End"},
    {"id": "sensor-london-005", "lat": 51.500, "lon": -0.100, "name": "South Bank"},
]


def generate_sensor_reading(sensor_loc, is_anomaly=False, anomaly_type=None):
    now = datetime.utcnow()
    
    temp = random.gauss(18, 4)
    humidity = random.gauss(65, 15)
    pressure = random.gauss(1013, 3)
    rainfall = random.gauss(0, 1)
    if is_anomaly:
        if anomaly_type == 'heat':
            temp = random.uniform(35, 42)  # Extreme heat
            humidity = random.uniform(20, 40)  # Low humidity
        elif anomaly_type == 'flood':
            pressure = random.uniform(990, 1000)  # Low pressure (storm)
            rainfall = random.uniform(15, 30)  # Heavy rainfall
        elif anomaly_type == 'rainfall':
            rainfall = random.uniform(8, 20)  # Significant rainfall
    
    return {
        "sensor_id": sensor_loc["id"],
        "timestamp": now.isoformat() + "Z",
        "location": {
            "type": "Point",
            "coordinates": [sensor_loc["lon"], sensor_loc["lat"]]
        },
        "temperature_c": round(max(-20, min(60, temp)), 2),  # Clamp realistic range
        "humidity_pct": round(max(0, min(100, humidity)), 1),
        "pressure_hpa": round(pressure, 2),
        "rainfall_mm": round(max(0, rainfall), 2)
    }


def ingest_reading(reading):
    try:
        response = requests.post(
            SENSORS_ENDPOINT,
            json=reading,
            timeout=5
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - is backend running on 127.0.0.1:8001?"
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 70)
    print("Sensor Data Ingestion Script")
    print("=" * 70)
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
    
    print("📊 Ingesting NORMAL sensor readings...")
    normal_count = 0
    for sensor in SENSOR_LOCATIONS:
        reading = generate_sensor_reading(sensor, is_anomaly=False)
        success, result = ingest_reading(reading)
        
        if success:
            print(f"  ✅ {sensor['name']}: {reading['temperature_c']}°C, {reading['humidity_pct']}%")
            normal_count += 1
        else:
            print(f"  ❌ {sensor['name']}: {result}")
    
    print(f"\n  Ingested {normal_count}/{len(SENSOR_LOCATIONS)} normal readings")
    print()
    
    print("⚠️  Ingesting ANOMALOUS sensor readings...")
    anomaly_count = 0
    anomaly_types = ['heat', 'flood', 'rainfall']
    
    for i, anomaly_type in enumerate(anomaly_types):
        sensor = SENSOR_LOCATIONS[i % len(SENSOR_LOCATIONS)]
        reading = generate_sensor_reading(sensor, is_anomaly=True, anomaly_type=anomaly_type)
        success, result = ingest_reading(reading)
        
        if success:
            if anomaly_type == 'heat':
                print(f"  ✅ {sensor['name']} (HEAT SPIKE): {reading['temperature_c']}°C ⚡")
            elif anomaly_type == 'flood':
                print(f"  ✅ {sensor['name']} (FLOOD RISK): {reading['rainfall_mm']}mm 💧")
            elif anomaly_type == 'rainfall':
                print(f"  ✅ {sensor['name']} (HEAVY RAIN): {reading['rainfall_mm']}mm 🌧️")
            anomaly_count += 1
        else:
            print(f"  ❌ {sensor['name']}: {result}")
    
    print(f"\n  Ingested {anomaly_count}/{len(anomaly_types)} anomalous readings")
    print()
    
    total = normal_count + anomaly_count
    print("=" * 70)
    print(f"✅ INGESTION COMPLETE: {total} readings sent to MongoDB")
    print("=" * 70)
    print()
    print("💡 Next steps:")
    print("   1. View anomalies: GET http://127.0.0.1:8001/api/anomalies")
    print("   2. Test the agent: python test_agent_query.py")
    print("   3. Check dashboard: http://localhost:3000")
    print()


if __name__ == "__main__":
    main()
