"""
parla/domains/weather_ingestor.py
Meteorological & Environmental Telemetry Ingestion and Tactical Flight Analysis Engine.

Ingests multi-sensor weather telemetry (temperature, humidity, barometric pressure,
rain rate, wind speed, solar irradiance, particulate matter PM2.5/PM10).
Applies zero-trust PII sanitization, GPS spatial coarsening, tactical flight viability
evaluations (FPV drones vs. CAS jets), and dispatches sealed records to the Parla Offline Ledger.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from parla.core.knowledge_base import WeatherKnowledgeBase
from parla.core.ledger import OfflineLedger
from parla.core.security import PIIScrubber


class WeatherIngestor:
    """
    Autonomous ingestor for meteorological and environmental edge telemetry.
    Adheres to the Yin-Yang-Chaos-Harmony paradigm:
      - Yin: Raw physical atmospheric observations (temperature, pressure, humidity, rain, wind).
      - Yang: Tactical flight viability (FPV drone / hexacopter / CAS jet) and acoustic speed calculations.
      - Chaos: Tropical cyclones, monsoon flash floods, landslides, and extreme heatwaves.
      - Harmony: Zero-trust cryptographic ledgering, GPS coarsening (~1.1 km), and PII scrubbing.
    """

    def __init__(self, kb: Optional[WeatherKnowledgeBase] = None):
        self.kb = kb or WeatherKnowledgeBase()
        self.pii_scrubber = PIIScrubber()

    def normalize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes field aliases into standardized schema keys."""
        norm = dict(packet)
        if "humidity_pct" not in norm and "relative_humidity_pct" in norm:
            norm["humidity_pct"] = norm["relative_humidity_pct"]
        if "rain_rate_mm_hr" not in norm and "precipitation_rate_mmh" in norm:
            norm["rain_rate_mm_hr"] = norm["precipitation_rate_mmh"]
        if "pm25_ug_m3" not in norm and "pm25_ugm3" in norm:
            norm["pm25_ug_m3"] = norm["pm25_ugm3"]
        if "observer_notes" not in norm and "operator_notes" in norm:
            norm["observer_notes"] = norm["operator_notes"]
        if "region_state" not in norm and "climate_zone" in norm:
            norm["region_state"] = norm["climate_zone"]
        return norm

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that incoming environmental packet contains necessary physical fields."""
        norm = self.normalize_packet(packet)
        required = ["station_id", "region_state", "latitude", "longitude", "temperature_c", "humidity_pct", "wind_speed_ms"]
        for field in required:
            if field not in norm:
                return False, f"Missing required meteorological field: '{field}'"

        lat = float(norm["latitude"])
        lon = float(norm["longitude"])
        if not (9.0 <= lat <= 29.0 and 92.0 <= lon <= 102.0):
            return False, f"Coordinates ({lat}, {lon}) fall outside the Myanmar geographical bounding box."

        # Physical boundary checks
        if not (-10.0 <= float(norm["temperature_c"]) <= 55.0):
            return False, f"Unrealistic temperature value: {norm['temperature_c']} °C"
        if not (0.0 <= float(norm["humidity_pct"]) <= 100.0):
            return False, f"Invalid relative humidity percentage: {norm['humidity_pct']}%"

        return True, "Valid meteorological packet."

    def sanitize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies zero-trust privacy guardrails:
        1. Coarsens latitude/longitude to 2 decimal places (~1.1 km precision).
        2. Scrubs observer names, telephone numbers, and local node tags.
        """
        sanitized = dict(packet)

        # 1. Coarsen GPS coordinates
        sanitized["latitude"] = round(float(packet["latitude"]), 2)
        sanitized["longitude"] = round(float(packet["longitude"]), 2)
        sanitized["spatial_grid_hash"] = f"GRID_{sanitized['latitude']:.2f}_{sanitized['longitude']:.2f}"

        # 2. Scrub PII from textual fields
        text_fields = ["observer_notes", "field_operator", "station_notes", "description"]
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = self.pii_scrubber.scrub_text(sanitized[field])

        # Redact sensitive operator identifiers
        for sensitive_key in ["operator_phone", "operator_name", "station_mac_address"]:
            if sensitive_key in sanitized:
                sanitized[sensitive_key] = "[REDACTED_SECURITY_POLICY]"

        return sanitized

    def evaluate_hazards(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates physical atmospheric observations against safety, flight, and disaster thresholds.
        """
        hazards: List[Dict[str, Any]] = []
        alerts: List[str] = []

        temp = float(packet.get("temperature_c", 25.0))
        hum = float(packet.get("humidity_pct", 60.0))
        wind = float(packet.get("wind_speed_ms", 3.0))
        rain_rate = float(packet.get("rain_rate_mm_hr", 0.0))
        rain_24h = float(packet.get("accumulated_rain_24h_mm", rain_rate * 4))
        cloud_m = float(packet.get("cloud_ceiling_m", 1500.0))
        pm25 = float(packet.get("pm25_ug_m3", 20.0))

        # 1. Tactical Flight Viability Evaluation
        flight_eval = self.kb.evaluate_flight_conditions(
            wind_speed_ms=wind,
            rain_rate_mm_hr=rain_rate,
            cloud_ceiling_m=cloud_m
        )

        # 2. Extreme Weather & Natural Disaster Hazards
        # Flash Flood
        if rain_rate >= 25.0 or rain_24h >= 100.0:
            hazards.append({
                "hazard_type": "CRITICAL_FLASH_FLOOD_IMMINENT",
                "severity": "CRITICAL",
                "value": f"{rain_24h} mm/24h",
                "action_required": "ACTIVATE_COMMUNITY_FLOOD_SIRENS_AND_EVACUATION"
            })
            alerts.append(f"CRITICAL: 24h precipitation ({rain_24h} mm) exceeds 100 mm severe flood threshold.")
        elif rain_rate >= 12.0 or rain_24h >= 50.0:
            hazards.append({
                "hazard_type": "ELEVATED_FLOOD_WATCH",
                "severity": "WARNING",
                "value": f"{rain_rate} mm/hr",
                "action_required": "MONITOR_RIVER_CREST_LEVELS"
            })

        # Landslide / Slope Liquefaction
        terrain = packet.get("terrain_type", "").lower()
        if rain_24h >= 60.0 and any(t in terrain for t in ["mountain", "hill", "mine", "jade", "cliff"]):
            hazards.append({
                "hazard_type": "MONSOON_LANDSLIDE_SLOPE_FAILURE",
                "severity": "CRITICAL" if rain_24h >= 90.0 else "HIGH",
                "value": f"{rain_24h} mm/24h on {terrain}",
                "action_required": "TRIGGER_PIT_WALL_AND_MOUNTAIN_PASS_EVACUATION"
            })
            alerts.append(f"ALERT: Heavy precipitation on steep {terrain} elevates landslide hazard.")

        # Cyclone / Severe Gale Wind
        if wind >= 17.5:  # Gale Force (Beaufort 8+)
            hazards.append({
                "hazard_type": "CYCLONE_FORCE_GALE_WINDS",
                "severity": "CRITICAL",
                "value": f"{wind} m/s ({round(wind * 3.6)} km/h)",
                "action_required": "SECURE_IDP_SHELTERS_GROUND_ALL_AERIAL_OPERATIONS"
            })
            alerts.append(f"CRITICAL: Wind velocity {round(wind * 3.6)} km/h exceeds severe gale threshold.")

        # Heatwave / Dehydration Threat
        if temp >= 40.0:
            hazards.append({
                "hazard_type": "EXTREME_HEATWAVE_HEALTH_RISK",
                "severity": "CRITICAL" if temp >= 43.0 else "HIGH",
                "value": f"{temp} °C",
                "action_required": "DISPATCH_EMERGENCY_ELECTROLYTE_RESERVES_TO_IDP_CAMPS"
            })
            alerts.append(f"WARNING: Ambient temperature ({temp} °C) induces acute heat illness risk.")

        # Smoke Haze / Scorched-Earth Fire PM2.5
        if pm25 >= 150.0:
            hazards.append({
                "hazard_type": "HAZARDOUS_SMOKE_HAZE_AIR_QUALITY",
                "severity": "HIGH",
                "value": f"{pm25} µg/m³ PM2.5",
                "action_required": "DISTRIBUTE_RESPIRATORY_MASKS_CONFIRM_FIRE_LOCATIONS"
            })
            alerts.append(f"ALERT: Particulate matter PM2.5 ({pm25} µg/m³) indicates dense smoke/fire inversion.")

        # 3. Acoustic Atmospheric Propagation Adjustments
        acoustic_prop = self.kb.evaluate_acoustic_propagation(
            temperature_c=temp,
            relative_humidity_pct=hum,
            frequency_hz=3000.0,  # Jet compressor whine standard test
            distance_km=8.0
        )

        overall_severity = "NORMAL"
        if any(h["severity"] == "CRITICAL" for h in hazards):
            overall_severity = "CRITICAL"
        elif any(h["severity"] == "HIGH" for h in hazards):
            overall_severity = "HIGH"
        elif any(h["severity"] == "WARNING" for h in hazards):
            overall_severity = "WARNING"

        return {
            "overall_hazard_severity": overall_severity,
            "hazards": hazards,
            "alerts": alerts,
            "tactical_flight_conditions": {
                "fpv_drone_status": flight_eval.fpv_drone_status,
                "hexacopter_status": flight_eval.hexacopter_status,
                "cas_jet_strike_status": flight_eval.cas_jet_strike_status,
                "helicopter_status": flight_eval.helicopter_status,
                "limitations": flight_eval.critical_limitations
            },
            "atmospheric_acoustic_profile": acoustic_prop
        }

    def process_and_record(
        self,
        packet: Dict[str, Any],
        ledger: Optional[OfflineLedger] = None
    ) -> Dict[str, Any]:
        """
        End-to-end ingestion pipeline:
        Validation -> Sanitization -> Tactical & Hazard Evaluation -> Cryptographic Ledger Append.
        """
        norm_packet = self.normalize_packet(packet)
        valid, msg = self.validate_packet(norm_packet)
        if not valid:
            return {"status": "REJECTED", "error": msg}

        sanitized = self.sanitize_packet(norm_packet)
        hazard_assessment = self.evaluate_hazards(norm_packet)

        telemetry_payload = {
            "telemetry_type": "METEOROLOGICAL_TACTICAL_TELEMETRY",
            "station_id": sanitized.get("station_id"),
            "district": sanitized.get("district", "UNKNOWN"),
            "region_state": sanitized.get("region_state"),
            "coarsened_coordinates": {
                "lat": sanitized["latitude"],
                "lon": sanitized["longitude"],
                "grid_hash": sanitized["spatial_grid_hash"]
            },
            "weather_readings": {
                "temperature_c": norm_packet.get("temperature_c"),
                "humidity_pct": norm_packet.get("humidity_pct"),
                "pressure_hpa": norm_packet.get("pressure_hpa"),
                "wind_speed_ms": norm_packet.get("wind_speed_ms"),
                "rain_rate_mm_hr": norm_packet.get("rain_rate_mm_hr", 0.0),
                "accumulated_rain_24h_mm": norm_packet.get("accumulated_rain_24h_mm", 0.0),
                "cloud_ceiling_m": norm_packet.get("cloud_ceiling_m", 1500.0),
                "pm25_ug_m3": norm_packet.get("pm25_ug_m3", 20.0)
            },
            "tactical_flight_viability": hazard_assessment["tactical_flight_conditions"],
            "hazard_assessment": {
                "severity": hazard_assessment["overall_hazard_severity"],
                "hazards": hazard_assessment["hazards"],
                "alerts": hazard_assessment["alerts"]
            },
            "speed_of_sound_ms": hazard_assessment["atmospheric_acoustic_profile"]["speed_of_sound_ms"],
            "observer_notes": sanitized.get("observer_notes", "")
        }

        block_result = None
        if ledger is not None:
            source_id = f"MET_NODE_{sanitized.get('station_id', 'UNKNOWN')}"
            success, ledger_msg, block = ledger.record_event(
                domain="meteorological_telemetry",
                payload=telemetry_payload,
                source_id=source_id,
                coarsen_gps=False  # Already coarsened and sanitized
            )
            block_result = {
                "recorded": success,
                "message": ledger_msg,
                "block_seq": block.get("seq_id") if block else None,
                "block_hash": block.get("block_hash") if block else None
            }

        return {
            "status": "PROCESSED",
            "sanitized_payload": telemetry_payload,
            "hazard_level": hazard_assessment["overall_hazard_severity"],
            "flight_viability": hazard_assessment["tactical_flight_conditions"],
            "ledger_commit": block_result
        }
