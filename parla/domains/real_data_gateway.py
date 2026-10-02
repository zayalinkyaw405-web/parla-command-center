"""
parla/domains/real_data_gateway.py
Resilient Real-World Data Ingestion Gateway.
Supports REST APIs (OSINT), MQTT (IoT Edge Nodes), NASA FIRMS GEOINT, and ADS-B flight telemetry.
"""

import json
import logging
import time
import requests
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass

# Safe import for MQTT
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.warning("paho-mqtt not installed. MQTT ingestion disabled. Install via: pip install paho-mqtt")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NormalizedTelemetry:
    source_type: str  # "REST_API", "MQTT_IOT", "GEOINT_FIRMS", "SIGINT_ADSB"
    event_id: str
    timestamp: float
    raw_payload: Dict[str, Any]
    normalized_data: Dict[str, Any]

class RealDataGateway:
    """
    Ingests real-world data from external APIs, IoT brokers, satellite feeds,
    and signals telemetry, normalizing it for OSINT and Industrial processors.
    """

    def __init__(self):
        self.mqtt_client = None
        self.rest_session = requests.Session()
        self.rest_session.headers.update({"User-Agent": "Parla-Command-Center/1.0"})

    # =====================================================================
    # REST API INGESTION (OSINT / Webhooks)
    # =====================================================================
    def poll_rest_api(self, url: str, headers: Optional[Dict] = None, 
                      params: Optional[Dict] = None) -> List[NormalizedTelemetry]:
        """Polls a REST API endpoint and normalizes the response."""
        try:
            response = self.rest_session.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Normalize (Assuming a list of events)
            events = data if isinstance(data, list) else data.get("data", [data])
            normalized_events = []
            
            for i, item in enumerate(events):
                normalized_events.append(NormalizedTelemetry(
                    source_type="REST_API",
                    event_id=f"rest_{int(time.time())}_{i}",
                    timestamp=time.time(),
                    raw_payload=item,
                    normalized_data={
                        "text": item.get("description", item.get("text", "")),
                        "location": item.get("location", item.get("geo", "UNKNOWN")),
                        "timestamp_raw": item.get("event_date", item.get("timestamp", ""))
                    }
                ))
            logger.info(f"REST API: Successfully ingested {len(normalized_events)} events from {url}")
            return normalized_events
            
        except requests.exceptions.RequestException as e:
            logger.error(f"REST API Polling Failed: {e}")
            return []

    # =====================================================================
    # NASA FIRMS SATELLITE THERMAL INGESTION
    # =====================================================================
    def ingest_firms_records(self, records: List[Dict[str, Any]], firms_ingestor) -> int:
        """
        Parses list of NASA FIRMS thermal anomaly dictionaries into the GEOINT ingestor.
        """
        count = 0
        for item in records:
            lat = float(item.get("latitude", 0.0))
            lon = float(item.get("longitude", 0.0))
            brightness = float(item.get("brightness", item.get("bright_ti4", 330.0)))
            acq_time = item.get("acquisition_time", item.get("acq_date", "2026-01-01T00:00:00Z"))
            satellite = item.get("satellite", "VIIRS_NOAA20")
            confidence = item.get("confidence", "high")
            frp = float(item.get("frp", 15.0))
            
            firms_ingestor.add_anomaly(
                lat=lat,
                lon=lon,
                brightness_k=brightness,
                acq_time=acq_time,
                satellite=satellite,
                confidence=confidence,
                frp_mw=frp
            )
            count += 1
        logger.info(f"GEOINT FIRMS: Ingested {count} satellite thermal anomalies.")
        return count

    # =====================================================================
    # ADS-B FLIGHT RADAR TELEMETRY INGESTION
    # =====================================================================
    def ingest_adsb_telemetry(self, flight_records: List[Dict[str, Any]]) -> List[NormalizedTelemetry]:
        """
        Normalizes ADS-B flight transponder detections (military sorties, transports).
        """
        normalized = []
        for i, item in enumerate(flight_records):
            callsign = item.get("callsign", "UNKNOWN").strip()
            icao = item.get("icao24", "000000").upper()
            altitude = float(item.get("altitude_m", item.get("baro_altitude", 0.0)))
            velocity = float(item.get("velocity_mps", 0.0))
            lat = float(item.get("latitude", 0.0))
            lon = float(item.get("longitude", 0.0))
            
            normalized.append(NormalizedTelemetry(
                source_type="SIGINT_ADSB",
                event_id=f"adsb_{icao}_{int(time.time())}_{i}",
                timestamp=time.time(),
                raw_payload=item,
                normalized_data={
                    "icao24": icao,
                    "callsign": callsign,
                    "altitude_m": altitude,
                    "velocity_kmh": round(velocity * 3.6, 1),
                    "coordinates": (lat, lon),
                    "is_military_profile": (velocity > 180.0 and altitude > 1000.0) or ("MAF" in callsign or "SAC" in callsign)
                }
            ))
        return normalized

    # =====================================================================
    # MQTT INGESTION (IoT Edge Nodes)
    # =====================================================================
    def connect_mqtt(self, broker: str, port: int, topic: str, 
                     callback: Callable[[str, str], None]):
        """Connects to an MQTT broker for real-time IoT telemetry."""
        if not MQTT_AVAILABLE:
            logger.error("Cannot connect to MQTT: paho-mqtt library missing.")
            return

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"MQTT Connected to {broker}:{port}. Subscribing to {topic}")
                client.subscribe(topic)
            else:
                logger.error(f"MQTT Connection failed with code {rc}")

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                callback(msg.topic, payload)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received on topic {msg.topic}")

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        
        try:
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start() # Runs in background thread
        except Exception as e:
            logger.error(f"MQTT Connection Error: {e}")

    def disconnect_mqtt(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()