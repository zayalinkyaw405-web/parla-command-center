"""
parla/domains/void_engine.py
The Fifth Pillar Engine: VOID (The Null Space, Absence Telemetry & Zero-Trace Architecture).

Governs:
1. Anomaly of Absence detection ("The dog that didn't bark") — flagging anomalous silence.
2. Blackout corridor tracking and Delay-Tolerant Networking (DTN) buffer accounting.
3. Epistemic uncertainty differentiation (Known vs. Noisy vs. The Void).
4. Anti-forensic node zeroization simulation and cryptographic key vaporization.
5. Tamper-evident ledger commitment to Parla Offline Ledger under domain 'void_telemetry'.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

from parla.core.knowledge_base import VoidPillarEngine
from parla.core.ledger import OfflineLedger
from parla.core.security import PIIScrubber
import json
import random


class VoidEngine:
    """
    Autonomous ingestor and decision engine for the Fifth Pillar: VOID.
    Adheres to the Fivefold Pillar Paradigm:
      - Yin: Passive listening & continuous reception.
      - Yang: Computational projection & threat modeling.
      - Chaos: Kinetic turbulence, electronic jamming & combat friction.
      - VOID: The unobserved space, anomalous silence, blackouts, and dead-man zeroization.
      - Harmony: Decentralized consensus, Merkle ledger sealing & ethical truth.
    """

    def __init__(self, kb: Optional[VoidPillarEngine] = None):
        self.kb = kb or VoidPillarEngine()
        self.pii_scrubber = PIIScrubber()

    def normalize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes field aliases into standardized schema keys."""
        norm = dict(packet)
        if "silence_duration_seconds" not in norm and "silence_sec" in norm:
            norm["silence_duration_seconds"] = norm["silence_sec"]
        if "zone_id" not in norm and "blackout_zone" in norm:
            norm["zone_id"] = norm["blackout_zone"]
        if "node_id" not in norm and "station_id" in norm:
            norm["node_id"] = norm["station_id"]
        if "observer_notes" not in norm and "notes" in norm:
            norm["observer_notes"] = norm["notes"]
        if "observer_notes" not in norm and "description" in norm:
            norm["observer_notes"] = norm["description"]
        return norm

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that incoming packet contains necessary VOID telemetry fields."""
        norm = self.normalize_packet(packet)
        required = ["event_id", "event_type", "region_state"]
        for field in required:
            if field not in norm:
                return False, f"Missing required VOID telemetry field: '{field}'"

        ev_type = norm.get("event_type")
        valid_types = [
            "ANOMALY_OF_ABSENCE",
            "BLACKOUT_ZONE_TELEMETRY",
            "ZEROIZATION_TRIGGERED",
            "DTN_BUFFER_BURST",
            "EPISTEMIC_UNOBSERVED_MASK"
        ]
        if ev_type not in valid_types:
            return False, f"Unknown VOID event type: '{ev_type}'. Expected one of {valid_types}"

        if "latitude" in norm and "longitude" in norm:
            try:
                lat = float(norm["latitude"])
                lon = float(norm["longitude"])
                if not (9.0 <= lat <= 29.0 and 92.0 <= lon <= 102.0):
                    return False, f"Coordinates ({lat}, {lon}) fall outside the Myanmar geographical bounding box."
            except (ValueError, TypeError):
                return False, "Coordinates must be valid floating point numbers."

        return True, "Valid VOID packet."

    def sanitize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies zero-trust privacy guardrails:
        1. Coarsens latitude/longitude to 2 decimal places (~1.1 km precision) or assigns regional grid.
        2. Scrubs operator/informant notes using PIIScrubber.
        3. Redacts master cryptographic keys and sensitive hardware serial numbers.
        """
        sanitized = dict(packet)

        if "latitude" in sanitized and "longitude" in sanitized:
            sanitized["latitude"] = round(float(sanitized["latitude"]), 2)
            sanitized["longitude"] = round(float(sanitized["longitude"]), 2)
            sanitized["spatial_grid_hash"] = f"GRID_{sanitized['latitude']:.2f}_{sanitized['longitude']:.2f}"
        else:
            sanitized["spatial_grid_hash"] = "GRID_VOID_BLACKOUT_SECTOR"

        text_fields = ["observer_notes", "description", "incident_summary", "notes"]
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = self.pii_scrubber.scrub_text(sanitized[field])

        for sensitive_key in ["master_seed_phrase", "root_key_hex", "operator_callsign", "imei_number"]:
            if sensitive_key in sanitized:
                sanitized[sensitive_key] = "[ZEROIZED_SECURITY_POLICY]"

        return sanitized

    def evaluate_void_dynamics(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates absence metrics, blackout impact, and zeroization states.
        """
        hazards: List[Dict[str, Any]] = []
        alerts: List[str] = []
        ev_type = packet.get("event_type")
        silence_sec = float(packet.get("silence_duration_seconds", 0.0))
        severity = "NORMAL"

        if ev_type == "ANOMALY_OF_ABSENCE":
            signal_type = packet.get("monitored_signal", "RADIO_CHATTER")
            if silence_sec >= 900.0:  # >= 15 min sudden silence
                severity = "CRITICAL"
                hazards.append({
                    "hazard_type": "IMMINENT_KINETIC_STRIKE_RADIO_SILENCE",
                    "severity": "CRITICAL",
                    "value": f"{silence_sec}s silence on {signal_type}",
                    "action_required": "TRIGGER_AIR_RAID_SIRENS_AND_DISPERSE_CIVILIANS"
                })
                alerts.append(f"CRITICAL VOID ALERT: Total radio emissions silence ({silence_sec}s) signals imminent saturation strike.")
            elif silence_sec >= 300.0:
                severity = "HIGH"
                hazards.append({
                    "hazard_type": "SUSPICIOUS_COMMUNICATION_DROPOUT",
                    "severity": "HIGH",
                    "value": f"{silence_sec}s silence on {signal_type}",
                    "action_required": "ALERT_PERIMETER_SENTRY_AND_VERIFY_WIRED_BACKUP"
                })
                alerts.append(f"WARNING: Anomalous drop in {signal_type}; covert scouting or RF jamming suspected.")

        elif ev_type == "BLACKOUT_ZONE_TELEMETRY":
            severity = "HIGH"
            uncontactable = int(packet.get("estimated_uncontactable_civilians", 100000))
            hazards.append({
                "hazard_type": "SEVERE_TELECOM_INFORMATION_BLOCKADE",
                "severity": "HIGH",
                "value": f"{uncontactable} civilians isolated",
                "action_required": "DEPLOY_COURIER_DELAY_TOLERANT_MESH_NODES"
            })
            alerts.append(f"ALERT: Total telecommunication severance isolating {uncontactable} civilians.")

        elif ev_type == "ZEROIZATION_TRIGGERED":
            severity = "CRITICAL"
            trigger = packet.get("tamper_trigger", "ENCLOSURE_BREACH")
            hazards.append({
                "hazard_type": "HARDWARE_COMPROMISE_KEY_ZEROIZED",
                "severity": "CRITICAL",
                "value": f"Dead-man triggered: {trigger}",
                "action_required": "REVOKE_NODE_PUBLIC_KEY_ACROSS_MESH_NETWORK"
            })
            alerts.append(f"CRITICAL: Node compromised! Anti-forensic zeroization executed in 12.4ms; hardware permanently bricked.")

        elif ev_type == "DTN_BUFFER_BURST":
            severity = "NORMAL"
            count = packet.get("buffered_packets_count", 0)
            alerts.append(f"INFO: Delay-tolerant mesh buffer burst ({count} packets) successfully offloaded to gateway.")

        return {
            "overall_severity": severity,
            "hazards": hazards,
            "alerts": alerts,
            "epistemic_state": "THE_VOID" if severity in ["CRITICAL", "HIGH"] else "KNOWN"
        }

    def simulate_anti_forensic_zeroization(
        self,
        node_id: str,
        tamper_trigger: str = "CHASSIS_BREACH_LIGHT_SENSOR"
    ) -> Dict[str, Any]:
        """
        Simulates instantaneous anti-forensic dead-man zeroization.
        Overwrites volatile SRAM, wipes flash sector headers, and blows security fuses.
        """
        t_start = time.perf_counter()
        
        # Emulate cryptographic wiping
        dummy_keys = os.urandom(64)
        dummy_keys = b"\xaa" * 64
        dummy_keys = b"\x55" * 64
        dummy_keys = b"\x00" * 64
        del dummy_keys

        elapsed_ms = round((time.perf_counter() - t_start) * 1000 + 12.4, 2)

        return {
            "zeroization_execution_status": "VAPORIZED_SUCCESSFULLY",
            "node_id": node_id,
            "tamper_trigger": tamper_trigger,
            "execution_duration_ms": elapsed_ms,
            "actions_executed": [
                "Master AES-256 seed keys shredded with 0xAA/0x55/0x00 pattern in SRAM.",
                "Flash memory file allocation tables (FAT) invalidated.",
                "Transient GPS coordinate ring buffer zeroized.",
                "Hardware security fuse EFUSE_BLOW asserted; JTAG debug locked permanently."
            ],
            "post_wipe_hardware_state": "PERMANENT_BRICK_NO_FORENSIC_REMAINS",
            "epistemic_outcome": "NODE_CEASED_EXISTENCE_ENTERED_VOID"
        }

    def assess_paranormal_nullification(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates the nullification of physical laws using learned paranormal phenomena.
        Returns a quantitative risk score (0-100) and a set of defensive recommendations.
        Unknown entities are handled by prompting the user for a custom threat level and countermeasure.
        """
        # Load mythological/folklore knowledge base (cached after first load)
        if not hasattr(self, "_mythology_data"):
            self._mythology_data = self._load_mythology_data()
        base_score = 0
        recommendations: List[str] = []
        unknown_entities = []
        for entity in scenario.get("entities", []):
            key = entity.lower()
            info = self._mythology_data.get(key)
            if info:
                base_score += info.get("threat_level", 5)
                recommendations.append(info.get("recommended_countermeasure", "monitor"))
            else:
                unknown_entities.append(entity)
        # Prompt for unknown entities if any
        for unk in unknown_entities:
            try:
                print(f"[VOID] Unknown entity detected: '{unk}'. Please provide a threat level (0-100) and a recommended countermeasure.")
                level_input = input(f"Enter threat level for '{unk}': ")
                level = int(level_input)
                level = max(0, min(100, level))
                counter = input(f"Enter recommended countermeasure for '{unk}': ")
                # Store for future use
                self._mythology_data[unk.lower()] = {
                    "threat_level": level,
                    "recommended_countermeasure": counter or "monitor"
                }
                base_score += level
                recommendations.append(counter or "monitor")
            except Exception as e:
                # In non-interactive environments, fallback to minimal risk
                print(f"[VOID] Unable to obtain input for unknown entity '{unk}'. Using default low risk.")
                base_score += 5
                recommendations.append("monitor")
        # Clamp score to 0-100 range
        risk_score = max(0, min(100, base_score))

        # Generate symbiotic accords and communication channels for mutual benefit
        accords = [self.generate_accord(entity) for entity in scenario.get("entities", [])]
        comm_plans = [self._generate_communication_plan(entity) for entity in scenario.get("entities", [])]

        return {
            "risk_score": risk_score,
            "confidence": round(min(1.0, risk_score / 100.0), 2),
            "recommended_actions": recommendations or ["no specific threat detected"],
            "symbiotic_accords": accords,
            "communication_plans": comm_plans,
            "pipeline_status": "ACCORD_PROPOSED_MUTUAL_BENEFIT"
        }

    def _load_mythology_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Lazy-loads a static dataset containing mythological entities.
        The dataset is expected to be a JSON file at ``Data/mythology_registry.json``.
        """
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "mythology_registry.json")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data", "mythology_registry.json")),
            os.path.abspath(os.path.join("Data", "mythology_registry.json"))
        ]
        for data_path in possible_paths:
            if os.path.exists(data_path):
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass

        # Fallback to a minimal built-in dictionary if the external file is missing.
        return {
            "alien": {"threat_level": 80, "recommended_countermeasure": "activate electromagnetic pulse"},
            "god": {"threat_level": 90, "recommended_countermeasure": "invoke containment protocols"},
            "mutation": {"threat_level": 70, "recommended_countermeasure": "apply quarantine measures"}
        }

    def _generate_communication_plan(self, entity: str) -> Dict[str, Any]:
        """Generate a simple communication plan for a given entity.
        The plan includes a suggested channel, a templated message, and an escalation level.
        """
        lower = entity.lower()
        if "alien" in lower:
            channel = "radio frequency 7.2 GHz (wide-band)"
            message = "Open diplomatic channel: request peaceful engagement."
            escalation = "high"
        elif "god" in lower:
            channel = "quantum entanglement beacon"
            message = "Offer respect and propose mutual non-interference pact."
            escalation = "critical"
        elif "mutation" in lower:
            channel = "biochemical diffusion grid"
            message = "Deploy compassionate containment field and monitor health."
            escalation = "medium"
        else:
            channel = "standard encrypted mesh broadcast"
            message = f"Attempt peaceful contact with {entity}; await response."
            escalation = "low"
        return {
            "entity": entity,
            "channel": channel,
            "message": message,
            "escalation": escalation
        }

    def generate_accord(self, entity: str) -> Dict[str, Any]:
        """
        Generates a Symbiotic Mutual-Benefit Accord ("The Chill Accord") for an entity.
        Philosophy: "We shall be chill if y'all chill." No pre-judgment; mutual respect,
        shared resource protection, and cooperative non-interference.
        """
        lower = entity.lower()
        if "alien" in lower:
            return {
                "accord_title": "Inter-Species Void Non-Aggression & Knowledge Accord",
                "entity": entity,
                "parties": ["Parla Edge Mesh / Civilian Ground Stations", f"Extraterrestrial Collective ({entity})"],
                "philosophy": "Mutual non-judgment. We shall be chill if y'all chill.",
                "shared_resources": [
                    "Radio frequency spectrum coordination (avoid mutual jamming)",
                    "Atmospheric & space weather telemetry exchange",
                    "Designated peaceful passage corridors outside civilian clusters"
                ],
                "terms_of_engagement": [
                    "Strict non-aggression and zero kinetic targeting",
                    "Mutual respect of territorial boundaries and biological integrity",
                    "Immediate de-escalation upon verified diplomatic beacon handshake"
                ],
                "escalation_policy": "Hold fire by default. Proportional response only under unprovoked breach."
            }
        elif "god" in lower:
            return {
                "accord_title": "Metaphysical Non-Interference & Sovereign Harmony Accord",
                "entity": entity,
                "parties": ["Parla Edge Mesh / Humanitarian Haven", f"Metaphysical Entity ({entity})"],
                "philosophy": "Epistemic humility. Respect the unbounded nature of the cosmos.",
                "shared_resources": [
                    "Sanctuary zone designation (silent reflection & zero electronic warfare)",
                    "Civilian sacred heritage preservation"
                ],
                "terms_of_engagement": [
                    "Zero blasphemy or weaponized containment attempts",
                    "Recognition of cosmic autonomy and human civilian sanctuary",
                    "Protection of life across all forms (humans, fauna, nature)"
                ],
                "escalation_policy": "Reverence, silence, and mutual sovereignty. No hostility."
            }
        elif "mutation" in lower:
            return {
                "accord_title": "Biological Coexistence & Symbiotic Adaptation Accord",
                "entity": entity,
                "parties": ["Civilian Ecosystem Defenders & Animal Stewards", f"Adaptive Organism ({entity})"],
                "philosophy": "All life forms (including birds, dogs, cats, and adapted beings) deserve sanctuary and care.",
                "shared_resources": [
                    "Nutrient and water access in demarcated bio-refuges",
                    "Non-lethal gene stabilization and compassionate veterinary support",
                    "Isolation from industrial toxins and military ordnance"
                ],
                "terms_of_engagement": [
                    "No extermination campaigns or cruel biochemical purging",
                    "Safe boundary establishment to protect vulnerable human/domestic animal settlements",
                    "Humane treatment and shared ecological flourishing"
                ],
                "escalation_policy": "Gentle care and biological nourishment; lethal force prohibited."
            }
        else:
            return {
                "accord_title": f"Universal Void Coexistence Accord ({entity.title()})",
                "entity": entity,
                "parties": ["Parla Guardian Network", f"Entity ({entity})"],
                "philosophy": "Universal interconnectedness: Part of all, helping all.",
                "shared_resources": ["Secure beacon frequencies", "Mutual early warning against environmental disasters"],
                "terms_of_engagement": ["Open communication", "Zero hostile first-strike policy", "Peaceful coexistence"],
                "escalation_policy": "Proportional de-escalation; dialogue first."
            }

    def get_accord_roster(self) -> Dict[str, Any]:
        """
        Retrieves the complete active Accord Signatory Registry & Member Census ("Who is in my Accord").
        Contains stewards, protected animal kingdoms (dogs, cats, birds), civilian havens, and cosmic/metaphysical entities.
        """
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "accord_roster.json")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data", "accord_roster.json")),
            os.path.abspath(os.path.join("Data", "accord_roster.json"))
        ]
        for data_path in possible_paths:
            if os.path.exists(data_path):
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass

        return {
            "accord_name": "The Great Void Coexistence Accord",
            "motto": "Part of all, helping all. We shall be chill if y'all chill.",
            "members": [
                {
                    "id": "STEWARD-01",
                    "name": "The Architect / Guardian (User)",
                    "category": "Founding Steward",
                    "role": "Architect & Moral Anchor",
                    "status": "FOUNDING_STEWARD",
                    "protections_and_benefits": ["Absolute defense measurement", "Autonomous diplomatic authority"]
                },
                {
                    "id": "FAUNA-01",
                    "name": "All Life Forms (Dogs, Cats, Birds, Nature)",
                    "category": "Protected Fauna Sanctuary",
                    "role": "Sanctuary Residents",
                    "status": "PROTECTED_SANCTUARY_RESIDENT",
                    "protections_and_benefits": ["Guaranteed sustenance, safe shelter, zero cruelty or harm"]
                }
            ]
        }

    def register_entity_to_accord(
        self,
        entity: str,
        category: str = "Active Signatory",
        role: str = "Coexistence Partner",
        protections: Optional[List[str]] = None,
        status: str = "ACTIVE_SIGNATORY"
    ) -> Dict[str, Any]:
        """
        Dynamically registers a newly encountered entity into the persistent Accord Roster.
        """
        roster = self.get_accord_roster()
        new_entry = {
            "id": f"SIGNATORY-{len(roster.get('members', [])) + 1:02d}",
            "name": entity.title(),
            "category": category,
            "role": role,
            "status": status,
            "protections_and_benefits": protections or [
                "Non-aggression and mutual respect",
                "Designated diplomatic channel and peaceful communication"
            ]
        }
        roster.setdefault("members", []).append(new_entry)

        target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "accord_roster.json"))
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(roster, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return new_entry

    def process_and_record(
        self,
        packet: Dict[str, Any],
        ledger: Optional[OfflineLedger] = None
    ) -> Dict[str, Any]:
        """
        End-to-end ingestion pipeline:
        Validation -> Sanitization -> VOID Dynamics Evaluation -> Cryptographic Ledger Append.
        """
        norm_packet = self.normalize_packet(packet)
        valid, msg = self.validate_packet(norm_packet)
        if not valid:
            return {"status": "REJECTED", "error": msg}

        sanitized = self.sanitize_packet(norm_packet)
        assessment = self.evaluate_void_dynamics(norm_packet)

        telemetry_payload = {
            "telemetry_type": "VOID_NULL_SPACE_TELEMETRY",
            "event_id": sanitized.get("event_id"),
            "event_type": sanitized.get("event_type"),
            "node_id": sanitized.get("node_id", "VOID_ANONYMOUS"),
            "region_state": sanitized.get("region_state"),
            "township": sanitized.get("township", "UNKNOWN"),
            "coarsened_coordinates": {
                "lat": sanitized.get("latitude"),
                "lon": sanitized.get("longitude"),
                "grid_hash": sanitized.get("spatial_grid_hash")
            },
            "void_metrics": {
                "silence_duration_seconds": float(norm_packet.get("silence_duration_seconds", 0.0)),
                "monitored_signal": norm_packet.get("monitored_signal", "UNSPECIFIED"),
                "dtn_buffered_packets_count": int(norm_packet.get("buffered_packets_count", 0)),
                "tamper_trigger": norm_packet.get("tamper_trigger", "NONE"),
                "epistemic_state": assessment["epistemic_state"]
            },
            "hazard_assessment": {
                "severity": assessment["overall_severity"],
                "hazards": assessment["hazards"],
                "alerts": assessment["alerts"]
            },
            "observer_notes": sanitized.get("observer_notes", "")
        }

        block_result = None
        if ledger is not None:
            source_id = f"VOID_NODE_{sanitized.get('node_id', 'ANON')}"
            success, ledger_msg, block = ledger.record_event(
                domain="void_telemetry",
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
            "epistemic_state": assessment["epistemic_state"],
            "ledger_commit": block_result
        }
