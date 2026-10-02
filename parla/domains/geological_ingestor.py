"""
parla/domains/geological_ingestor.py
Geological & Critical Mineral Telemetry Ingestion and Hazard Analysis Engine.

Ingests multi-modal geophysical sensing (geophones, borehole gamma), geochemical assays (pXRF),
InSAR ground displacement, and hydrochemical data across Myanmar's key mineral belts.
Sanitizes PII, coarsens GPS coordinates, evaluates slope/environmental hazards,
and dispatches sealed telemetry to the Parla Offline Ledger.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from parla.core.knowledge_base import GeologicalKnowledgeBase
from parla.core.ledger import OfflineLedger
from parla.core.security import PIIScrubber


class GeologicalIngestor:
    """
    Autonomous ingestor for geological, geophysical, and critical mineral telemetry.
    Adheres to the Yin-Yang-Chaos-Harmony paradigm:
      - Yin: Raw physical observations (geophone, pXRF, InSAR, pH).
      - Yang: Automated hazard detection and ore grade evaluation.
      - Chaos: Dynamic environmental instability and mine hazards.
      - Harmony: Cryptographic ledgering, GPS coarsening, and PII elimination.
    """

    def __init__(self, kb: Optional[GeologicalKnowledgeBase] = None):
        self.kb = kb or GeologicalKnowledgeBase()
        self.pii_scrubber = PIIScrubber()

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that incoming telemetry packet contains necessary physical fields."""
        required = ["station_id", "region_state", "latitude", "longitude"]
        for field in required:
            if field not in packet:
                return False, f"Missing required telemetry field: '{field}'"

        lat = packet["latitude"]
        lon = packet["longitude"]
        if not (9.0 <= lat <= 29.0 and 92.0 <= lon <= 102.0):
            return False, f"Coordinates ({lat}, {lon}) fall outside the Myanmar geographical bounding box."

        return True, "Valid geological telemetry packet."

    def sanitize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies zero-trust privacy guardrails:
        1. Coarsens latitude/longitude to 2 decimal places (~1.1 km precision).
        2. Scrubs operator identities, personal data, and local license tags.
        """
        sanitized = dict(packet)

        # 1. Coarsen GPS coordinates
        sanitized["latitude"] = round(float(packet["latitude"]), 2)
        sanitized["longitude"] = round(float(packet["longitude"]), 2)
        sanitized["spatial_grid_hash"] = f"GRID_{sanitized['latitude']:.2f}_{sanitized['longitude']:.2f}"

        # 2. Scrub PII from textual fields
        text_fields = ["notes", "observer_notes", "field_operator", "concession_info", "description"]
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                scrubbed_text = self.pii_scrubber.scrub_text(sanitized[field])
                sanitized[field] = scrubbed_text

        # Irreversibly drop sensitive operator IDs if present
        for sensitive_key in ["raw_operator_id", "operator_name", "concession_license_no"]:
            if sensitive_key in sanitized:
                sanitized[sensitive_key] = "[REDACTED_SECURITY_POLICY]"

        return sanitized

    def evaluate_hazards(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates physical sensor readings against safety and environmental thresholds:
        - InSAR ground displacement (>80 mm/yr: Critical slope risk, >40 mm/yr: Elevated warning).
        - Geophone peak particle velocity (>25 mm/s: Rockburst/blasting impact).
        - Hydrochemistry (pH < 4.5: Acid mine drainage).
        - Geochemical pXRF ore grades.
        """
        hazards: List[Dict[str, Any]] = []
        alerts: List[str] = []

        # 1. InSAR Ground Deformation
        insar_mm = packet.get("insar_displacement_mm_yr")
        if insar_mm is not None:
            if insar_mm >= 80.0:
                hazards.append({
                    "hazard_type": "CRITICAL_SLOPE_DISPLACEMENT",
                    "value": insar_mm,
                    "unit": "mm/yr",
                    "severity": "CRITICAL",
                    "action_required": "IMMEDIATE_PIT_EVACUATION_WARNING"
                })
                alerts.append(f"CRITICAL: Ground displacement velocity {insar_mm} mm/yr exceeds 80 mm/yr slope failure limit.")
            elif insar_mm >= 40.0:
                hazards.append({
                    "hazard_type": "ELEVATED_GROUND_SUBSIDENCE",
                    "value": insar_mm,
                    "unit": "mm/yr",
                    "severity": "WARNING",
                    "action_required": "INCREASE_GEOPHONE_SAMPLING"
                })

        # 2. Geophone Triaxial Vibration & Peak Particle Velocity (PPV)
        geophone_hz = packet.get("geophone_hz")
        ppv_mms = packet.get("peak_particle_velocity_mms")
        if ppv_mms is not None and ppv_mms >= 25.0:
            hazards.append({
                "hazard_type": "EXCESSIVE_BLAST_VIBRATION",
                "value": ppv_mms,
                "unit": "mm/s",
                "severity": "HIGH",
                "action_required": "INSPECT_TUNNEL_INTEGRITY"
            })
            alerts.append(f"WARNING: PPV of {ppv_mms} mm/s exceeds structural threshold (25 mm/s).")

        if geophone_hz is not None and 15.0 <= geophone_hz <= 45.0 and ppv_mms and ppv_mms > 8.0:
            hazards.append({
                "hazard_type": "CONTINUOUS_SLOPE_CREEP_TREMOR",
                "value": geophone_hz,
                "unit": "Hz",
                "severity": "HIGH",
                "action_required": "MONITOR_TAILINGS_DAM_SLOPE"
            })

        # 3. Hydrochemical / Acid Mine Drainage (AMD)
        ph_level = packet.get("water_ph")
        if ph_level is not None:
            if ph_level < 4.5:
                hazards.append({
                    "hazard_type": "ACID_MINE_DRAINAGE",
                    "value": ph_level,
                    "unit": "pH",
                    "severity": "CRITICAL" if ph_level < 3.5 else "HIGH",
                    "action_required": "CONTAIN_RUNOFF_NEUTRALIZE_LEACH_POND"
                })
                alerts.append(f"ALERT: Water pH {ph_level} indicates acute acid mine drainage.")

        # 4. Deposit Matching & pXRF Mineral Indicators
        pxrf = packet.get("pxrf_ppm", {})
        hz = geophone_hz or 0.0
        insar = insar_mm or 0.0
        kb_eval = self.kb.evaluate_telemetry(pXRF=pxrf, geophone_hz=hz, insar_mm=insar)

        # 5. Fault Proximity Check
        active_faults_near = []
        for fault in self.kb.list_faults():
            # Check if region or district corresponds
            for dist in fault.intersected_mining_districts:
                if dist.lower() in packet.get("region_state", "").lower() or dist.lower() in packet.get("district", "").lower():
                    active_faults_near.append({
                        "fault_id": fault.fault_id,
                        "name": fault.name,
                        "max_magnitude": fault.max_credible_magnitude,
                        "hazard_rating": fault.seismic_hazard_rating
                    })

        severity_rank = "NORMAL"
        if any(h["severity"] == "CRITICAL" for h in hazards):
            severity_rank = "CRITICAL"
        elif any(h["severity"] == "HIGH" for h in hazards):
            severity_rank = "HIGH"
        elif any(h["severity"] == "WARNING" for h in hazards):
            severity_rank = "WARNING"

        return {
            "overall_hazard_severity": severity_rank,
            "hazards": hazards,
            "alerts": alerts,
            "kb_matched_deposits": kb_eval.get("matched_deposits", []),
            "active_faults_proximate": active_faults_near
        }

    def process_and_record(
        self,
        packet: Dict[str, Any],
        ledger: Optional[OfflineLedger] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end ingestion pipeline:
        Validation -> Sanitization -> Hazard Evaluation -> Cryptographic Ledger Append.
        """
        valid, msg = self.validate_packet(packet)
        if not valid:
            return {"status": "REJECTED", "error": msg}

        sanitized = self.sanitize_packet(packet)
        hazard_assessment = self.evaluate_hazards(packet)

        telemetry_payload = {
            "telemetry_type": "GEOLOGICAL_CRITICAL_MINERAL_TELEMETRY",
            "station_id": sanitized.get("station_id"),
            "district": sanitized.get("district", "UNKNOWN"),
            "region_state": sanitized.get("region_state"),
            "coarsened_coordinates": {
                "lat": sanitized["latitude"],
                "lon": sanitized["longitude"],
                "grid_hash": sanitized["spatial_grid_hash"]
            },
            "sensor_readings": {
                "geophone_hz": packet.get("geophone_hz"),
                "peak_particle_velocity_mms": packet.get("peak_particle_velocity_mms"),
                "insar_displacement_mm_yr": packet.get("insar_displacement_mm_yr"),
                "water_ph": packet.get("water_ph"),
                "pxrf_ppm": packet.get("pxrf_ppm", {})
            },
            "hazard_assessment": hazard_assessment,
            "notes": sanitized.get("notes", "")
        }

        block_result = None
        if ledger is not None:
            source_id = f"GEOL_NODE_{sanitized.get('station_id', 'UNKNOWN')}"
            success, ledger_msg, block = ledger.record_event(
                domain="geological_telemetry",
                payload=telemetry_payload,
                source_id=source_id,
                coarsen_gps=False  # Coordinates are already coarsened and sanitized
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
            "ledger_commit": block_result
        }
