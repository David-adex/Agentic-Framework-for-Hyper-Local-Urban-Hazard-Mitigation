import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import './App.css';

// Fix Leaflet icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function App() {
  const [samples, setSamples] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [selectedSensor, setSelectedSensor] = useState(null);
  const mapRef = useRef(null);

  // Create custom marker icons
  const normalMarkerIcon = L.icon({
    iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%231d4ed8"><path d="M12 2C7.58 2 4 5.58 4 10c0 5.25 8 13 8 13s8-7.75 8-13c0-4.42-3.58-8-8-8zm0 11c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });

  const anomalyMarkerIcon = L.icon({
    iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23dc2626"><path d="M12 2C7.58 2 4 5.58 4 10c0 5.25 8 13 8 13s8-7.75 8-13c0-4.42-3.58-8-8-8zm0 11c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  });

  useEffect(() => {
    async function loadData() {
      try {
        const sensorRes = await axios.get('/api/sensors/sample');
        const anomalyRes = await axios.get('/api/anomalies');
        setSamples(sensorRes.data);
        setAnomalies(anomalyRes.data);
        setLastUpdated(new Date());
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const latest = samples[0] || null;
  const avgTemp = samples.length
    ? (samples.reduce((sum, item) => sum + item.temperature_c, 0) / samples.length).toFixed(1)
    : '0.0';
  const avgRain = samples.length
    ? (samples.reduce((sum, item) => sum + item.rainfall_mm, 0) / samples.length).toFixed(2)
    : '0.00';
  const avgHumidity = samples.length
    ? (samples.reduce((sum, item) => sum + item.humidity_pct, 0) / samples.length).toFixed(1)
    : '0.0';
  const heatRisk = anomalies.length ? Math.min(100, 35 + anomalies.length * 18) : 14;

  // Calculate map center from sensor locations
  const mapCenter = samples.length > 0
    ? [samples.reduce((sum, s) => sum + s.location.coordinates[1], 0) / samples.length,
       samples.reduce((sum, s) => sum + s.location.coordinates[0], 0) / samples.length]
    : [40.7128, -74.0060]; // NYC fallback

  return (
    <div className="app-container-geospatial">
      <header className="map-header">
        <div className="title-row">
          <div className="status-dot" />
          <h1>Urban Microclimate Dashboard</h1>
        </div>
        <p>Real-time geospatial hazard monitoring and agentic response planning</p>
      </header>

      <div className="map-layout">
        {/* MAP PANEL */}
        <div className="map-panel">
          {loading ? (
            <div className="loading-overlay">Loading hazard map...</div>
          ) : (
            <MapContainer center={mapCenter} zoom={13} className="leaflet-map">
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
              />
              
              {/* Render normal sensor markers */}
              {samples.map((sensor) => {
                const isAnomaly = anomalies.some((a) => a.sensor_id === sensor.sensor_id);
                const temp = sensor.temperature_c;
                const riskColor = temp > 35 ? '#dc2626' : temp > 30 ? '#f97316' : '#22c55e';

                return (
                  <Marker
                    key={sensor.sensor_id}
                    position={[sensor.location.coordinates[1], sensor.location.coordinates[0]]}
                    icon={isAnomaly ? anomalyMarkerIcon : normalMarkerIcon}
                    eventHandlers={{
                      click: () => setSelectedSensor(sensor),
                    }}
                  >
                    <Popup>
                      <div className="popup-content">
                        <strong>{sensor.sensor_id}</strong>
                        <p>Temp: {temp.toFixed(1)}°C</p>
                        <p>Humidity: {sensor.humidity_pct.toFixed(1)}%</p>
                        <p>Rainfall: {sensor.rainfall_mm.toFixed(2)} mm</p>
                        {isAnomaly && <p className="anomaly-badge">⚠️ Anomaly detected</p>}
                      </div>
                    </Popup>
                  </Marker>
                );
              })}

              {/* Heat risk visualization circles */}
              {samples.map((sensor) => {
                const temp = sensor.temperature_c;
                const riskRadius = temp > 35 ? 800 : temp > 30 ? 600 : 400;
                const riskColor = temp > 35 ? '#dc2626' : temp > 30 ? '#f97316' : '#22c55e';

                return (
                  <Circle
                    key={`risk-${sensor.sensor_id}`}
                    center={[sensor.location.coordinates[1], sensor.location.coordinates[0]]}
                    radius={riskRadius}
                    pathOptions={{
                      color: riskColor,
                      weight: 1,
                      opacity: 0.15,
                      fill: true,
                      fillColor: riskColor,
                      fillOpacity: 0.08,
                    }}
                  />
                );
              })}
            </MapContainer>
          )}
        </div>

        {/* SIDE PANEL */}
        <div className="side-panel">
          <section className="status-header">
            <div className="status-chips">
              <div className="chip live">Live monitoring</div>
              <div className="chip">Updated {lastUpdated.toLocaleTimeString()}</div>
              <div className={`chip ${anomalies.length > 0 ? 'warning' : 'normal'}`}>
                {anomalies.length ? `${anomalies.length} alerts` : 'Normal'}
              </div>
            </div>
          </section>

          <section className="stats-panel">
            <h3>Microclimate Metrics</h3>
            <div className="metric-row">
              <div className="metric">
                <span className="metric-label">Sensors</span>
                <strong>{samples.length}</strong>
              </div>
              <div className="metric">
                <span className="metric-label">Avg Temp</span>
                <strong>{avgTemp}°C</strong>
              </div>
              <div className="metric">
                <span className="metric-label">Avg Humidity</span>
                <strong>{avgHumidity}%</strong>
              </div>
              <div className="metric danger">
                <span className="metric-label">Risk</span>
                <strong>{heatRisk}%</strong>
              </div>
            </div>
          </section>

          {selectedSensor && (
            <section className="selected-sensor">
              <h3>Selected Sensor</h3>
              <div className="sensor-detail">
                <strong className="sensor-id">{selectedSensor.sensor_id}</strong>
                <p><span>Temperature:</span> {selectedSensor.temperature_c.toFixed(1)}°C</p>
                <p><span>Humidity:</span> {selectedSensor.humidity_pct.toFixed(1)}%</p>
                <p><span>Pressure:</span> {selectedSensor.pressure_hpa.toFixed(1)} hPa</p>
                <p><span>Rainfall:</span> {selectedSensor.rainfall_mm.toFixed(2)} mm</p>
                <p><span>Location:</span> {selectedSensor.location.coordinates[1].toFixed(4)}, {selectedSensor.location.coordinates[0].toFixed(4)}</p>
              </div>
              <button className="close-btn" onClick={() => setSelectedSensor(null)}>Close</button>
            </section>
          )}

          <section className="alerts-section">
            <h3>Active Alerts</h3>
            {anomalies.length ? (
              <div className="alerts-list">
                {anomalies.map((anomaly, idx) => (
                  <div key={idx} className="alert-card">
                    <div className="alert-icon">⚠️</div>
                    <div className="alert-content">
                      <strong>{anomaly.metric}</strong>
                      <p>{anomaly.description}</p>
                      <small>{anomaly.sensor_id} • z={anomaly.z_score.toFixed(2)}</small>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-alerts">No anomalies detected</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

export default App;
