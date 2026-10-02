"""
parla/domains/religious_dynamics_ingestor.py
Socio-Religious Dynamics, Sacred Site Monitoring, and IHL Violation Telemetry Engine.

Ingests multi-source reports on religious traditions, sacred infrastructure attacks,
monastic IDP sanctuaries, sectarian hate speech incitement, and military Yadaya rituals.
Applies zero-trust PII sanitization (protecting clergy/nuns/monks), GPS spatial coarsening,
and dispatches tamper-evident records to the Parla Offline Ledger.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from parla.core.knowledge_base import ReligiousDynamicsKnowledgeBase
from parla.core.ledger import OfflineLedger
from parla.core.security import PIIScrubber


class ReligiousDynamicsIngestor:
    """
    Autonomous ingestor for socio-religious telemetry, sacred site damage, and sectarian risk.
    Adheres to the Yin-Yang-Chaos-Harmony paradigm:
      - Yin: The "Light" sector—monastic sanctuaries, church relief networks, inter-faith solidarity.
      - Yang: International Humanitarian Law (IHL) damage accounting, demographic mapping, and legal evidence.
      - Chaos: The "Dark" sector—junta airstrikes on churches/monasteries, MaBaTha extremism, and Yadaya occultism.
      - Harmony: Zero-trust cryptographic ledgering, clergy identity shielding, and GPS spatial coarsening (~1.1 km).
    """

    def __init__(self, kb: Optional[ReligiousDynamicsKnowledgeBase] = None):
        self.kb = kb or ReligiousDynamicsKnowledgeBase()
        self.pii_scrubber = PIIScrubber()

    def normalize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes field aliases into standardized schema keys."""
        norm = dict(packet)
        if "site_name" not in norm and "sacred_site" in norm:
            norm["site_name"] = norm["sacred_site"]
        if "site_type" not in norm and "facility_type" in norm:
            norm["site_type"] = norm["facility_type"]
        if "damage_severity" not in norm and "severity" in norm:
            norm["damage_severity"] = norm["severity"]
        if "region_state" not in norm and "state" in norm:
            norm["region_state"] = norm["state"]
        if "township" not in norm and "district" in norm:
            norm["township"] = norm["district"]
        if "observer_notes" not in norm and "notes" in norm:
            norm["observer_notes"] = norm["notes"]
        if "observer_notes" not in norm and "description" in norm:
            norm["observer_notes"] = norm["description"]
        return norm

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that incoming packet contains required reporting fields."""
        norm = self.normalize_packet(packet)
        required = ["record_id", "record_type", "region_state"]
        for field in required:
            if field not in norm:
                return False, f"Missing required socio-religious field: '{field}'"

        rec_type = norm.get("record_type")
        if rec_type not in ["SACRED_SITE_ATTACK", "HUMANITARIAN_SANCTUARY", "SECTARIAN_INCITEMENT", "YADAYA_OCCULT_RECORD"]:
            return False, f"Unknown socio-religious record type: '{rec_type}'"

        # Coordinates validation if provided
        if "latitude" in norm and "longitude" in norm:
            try:
                lat = float(norm["latitude"])
                lon = float(norm["longitude"])
                if not (9.0 <= lat <= 29.0 and 92.0 <= lon <= 102.0):
                    return False, f"Coordinates ({lat}, {lon}) fall outside the Myanmar geographical bounding box."
            except (ValueError, TypeError):
                return False, "Coordinates must be valid floating point numbers."

        return True, "Valid socio-religious packet."

    def sanitize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies zero-trust privacy guardrails:
        1. Coarsens latitude/longitude to 2 decimal places (~1.1 km precision) to protect sanctuaries from artillery.
        2. Scrubs names of pastors, priests, monks, nuns, and civilian witnesses from text.
        3. Redacts direct informant IDs.
        """
        sanitized = dict(packet)

        # 1. Coarsen GPS coordinates if present
        if "latitude" in sanitized and "longitude" in sanitized:
            sanitized["latitude"] = round(float(sanitized["latitude"]), 2)
            sanitized["longitude"] = round(float(sanitized["longitude"]), 2)
            sanitized["spatial_grid_hash"] = f"GRID_{sanitized['latitude']:.2f}_{sanitized['longitude']:.2f}"
        else:
            sanitized["spatial_grid_hash"] = "GRID_REGIONAL_GENERAL"

        # 2. Scrub PII from textual notes and descriptions
        text_fields = ["observer_notes", "description", "incident_summary", "witness_testimony", "notes"]
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = self.pii_scrubber.scrub_text(sanitized[field])

        # 3. Redact sensitive field identifiers
        for sensitive_key in ["clergy_name", "pastor_name", "sayadaw_name", "nun_name", "informant_phone", "reporter_id"]:
            if sensitive_key in sanitized:
                sanitized[sensitive_key] = "[REDACTED_VULNERABLE_RELIGIOUS_ACTOR]"

        return sanitized

    def evaluate_religious_incident(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the legal severity under International Humanitarian Law (IHL),
        determines casualty impact, and generates warning advisories.
        """
        hazards: List[Dict[str, Any]] = []
        alerts: List[str] = []

        rec_type = packet.get("record_type")
        severity = packet.get("damage_severity", "MODERATE").upper()
        casualties = int(packet.get("civilian_casualties", 0))
        site_type = packet.get("site_type", "SACRED_FACILITY").upper()
        perpetrator = packet.get("perpetrator_entity", "ARMED_FORCES")

        ihl_status = "NOT_APPLICABLE"
        overall_level = "NORMAL"

        if rec_type == "SACRED_SITE_ATTACK":
            if severity in ["CRITICAL_TOTAL_DESTRUCTION", "CRITICAL"] or casualties >= 5:
                overall_level = "CRITICAL"
                ihl_status = "GRAVE_BREACH_GENEVA_CONVENTION_ART_53"
                hazards.append({
                    "hazard_type": "CATASTROPHIC_SACRED_SITE_DESTRUCTION",
                    "severity": "CRITICAL",
                    "value": f"{casualties} civilian casualties at {site_type}",
                    "action_required": "FILE_EVIDENCE_DOSSIER_WITH_IIMM_AND_UNHRC"
                })
                alerts.append(f"WAR CRIME ALERT: Direct lethal attack on {site_type} causing {casualties} casualties.")
            elif severity in ["MAJOR_STRUCTURAL_DAMAGE", "MAJOR"]:
                overall_level = "HIGH"
                ihl_status = "SERIOUS_IHL_VIOLATION_PROTECTED_PROPERTY"
                hazards.append({
                    "hazard_type": "MAJOR_SACRED_PROPERTY_SHELLING",
                    "severity": "HIGH",
                    "value": f"Heavy damage to {site_type} by {perpetrator}",
                    "action_required": "DISPATCH_EMERGENCY_TARPAULIN_AND_EVACUATE_SANCTUARY"
                })
                alerts.append(f"ALERT: Heavy structural attack against {site_type}; protected status breached.")
            else:
                overall_level = "WARNING"
                ihl_status = "VIOLATION_OF_SACRED_NEUTRALITY"
                hazards.append({
                    "hazard_type": "DESECRATION_OR_OCCUPATION_OF_WORSHIP_SITE",
                    "severity": "WARNING",
                    "value": f"Military intrusion into {site_type}",
                    "action_required": "MONITOR_CLERGY_SAFETY_AND_DOC_LOOTING"
                })

        elif rec_type == "SECTARIAN_INCITEMENT":
            overall_level = "HIGH"
            hazards.append({
                "hazard_type": "SECTARIAN_COMMUNAL_INCITEMENT_DETECTED",
                "severity": "HIGH",
                "value": packet.get("incitement_theme", "ANTI_MINORITY_HATE_SPEECH"),
                "action_required": "ACTIVATE_INTERFAITH_PEACE_BRIGADE_AND_COUNTER_DISINFO"
            })
            alerts.append("WARNING: Ethno-religious hate speech incitement flagged; high risk of orchestrated communal riot.")

        elif rec_type == "YADAYA_OCCULT_RECORD":
            overall_level = "WARNING"
            hazards.append({
                "hazard_type": "MILITARY_YADAYA_RITUAL_ACTIVITY",
                "severity": "WARNING",
                "value": packet.get("ritual_act", "ASTROLOGICAL_MANIPULATION"),
                "action_required": "CORRELATE_WITH_UPCOMING_MILITARY_OFFENSIVE_WINDOW"
            })
            alerts.append("NOTICE: State-level Yadaya occult operation observed; typically precedes major tactical offensive or currency purge.")

        return {
            "overall_severity": overall_level,
            "ihl_status": ihl_status,
            "hazards": hazards,
            "alerts": alerts
        }

    def process_and_record(
        self,
        packet: Dict[str, Any],
        ledger: Optional[OfflineLedger] = None
    ) -> Dict[str, Any]:
        """
        End-to-end ingestion pipeline:
        Validation -> Sanitization -> Legal/Hazard Evaluation -> Cryptographic Ledger Append.
        """
        norm_packet = self.normalize_packet(packet)
        valid, msg = self.validate_packet(norm_packet)
        if not valid:
            return {"status": "REJECTED", "error": msg}

        sanitized = self.sanitize_packet(norm_packet)
        assessment = self.evaluate_religious_incident(norm_packet)

        telemetry_payload = {
            "telemetry_type": "SOCIO_RELIGIOUS_CONFLICT_TELEMETRY",
            "record_id": sanitized.get("record_id"),
            "record_type": sanitized.get("record_type"),
            "region_state": sanitized.get("region_state"),
            "township": sanitized.get("township", "UNKNOWN"),
            "coarsened_coordinates": {
                "lat": sanitized.get("latitude"),
                "lon": sanitized.get("longitude"),
                "grid_hash": sanitized.get("spatial_grid_hash")
            },
            "site_profile": {
                "site_name": sanitized.get("site_name", "UNSPECIFIED_FACILITY"),
                "site_type": sanitized.get("site_type", "UNKNOWN"),
                "religion": sanitized.get("religion", "UNKNOWN"),
                "damage_severity": sanitized.get("damage_severity", "NONE"),
                "civilian_casualties": sanitized.get("civilian_casualties", 0),
                "attack_vector": sanitized.get("attack_vector", "UNKNOWN"),
                "perpetrator_entity": sanitized.get("perpetrator_entity", "UNKNOWN")
            },
            "legal_and_hazard_assessment": {
                "overall_severity": assessment["overall_severity"],
                "ihl_status": assessment["ihl_status"],
                "hazards": assessment["hazards"],
                "alerts": assessment["alerts"]
            },
            "observer_notes": sanitized.get("observer_notes", "")
        }

        block_result = None
        if ledger is not None:
            source_id = f"REL_NODE_{sanitized.get('record_id', 'UNKNOWN')}"
            success, ledger_msg, block = ledger.record_event(
                domain="socio_religious_telemetry",
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
            "severity": assessment["overall_severity"],
            "ihl_status": assessment["ihl_status"],
            "ledger_commit": block_result
        }
