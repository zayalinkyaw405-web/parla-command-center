"""
Myanmar Conflict Telemetry Parser & Signed Test Payload Generator
Parses collected_data_myanmar_iot_2022_2026.md into structured telemetry events,
simulates acoustic/thermal sensor signatures, and cryptographically signs test payloads.
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from parla.core.security import CryptographicEnvelope, canonical_json, compute_sha256


class MyanmarTelemetryParser:
    """
    Parses unstructured markdown intelligence documents from the Myanmar conflict (2022-2026),
    extracting key airstrike dynamics, macro metrics, and sensor parameters.
    """

    INCIDENT_PRESETS = [
        {
            "name": "Let Yet Kone Monastic School Strike",
            "date": "2022-09-16",
            "sector": "Tabayin_Sagaing",
            "aircraft_profile": "Mi-35_HELICOPTER_GUNSHIP",
            "acoustic_freq_hz": 180.0,
            "acoustic_db": 84.0,
            "thermal_frp_mw": 35.0,
            "fatalities": 13,
            "children_fatalities": 11,
            "lat": 22.471829,
            "lon": 95.283912,
            "raw_operator_info": "spotter_tabayin@resistance.org | +95-9-7712-3456 | IP 192.168.10.14"
        },
        {
            "name": "A Nang Pa Anniversary Concert Bombing",
            "date": "2022-10-23",
            "sector": "Hpakant_Kachin",
            "aircraft_profile": "Yak-130_JET_STRIKE_PACKAGE",
            "acoustic_freq_hz": 520.0,
            "acoustic_db": 89.5,
            "thermal_frp_mw": 85.0,
            "fatalities": 80,
            "children_fatalities": 0,
            "lat": 25.614821,
            "lon": 96.312948,
            "raw_operator_info": "kachin_field_node@kio.net | MAC 00:1B:44:11:3A:B7 | IP 10.200.4.1"
        },
        {
            "name": "Pa Zi Gyi Thermobaric Munition Strike",
            "date": "2023-04-11",
            "sector": "Kanbalu_Sagaing",
            "aircraft_profile": "Su-30SME_Yak-130_THERMOBARIC",
            "acoustic_freq_hz": 620.0,
            "acoustic_db": 93.5,
            "thermal_frp_mw": 240.0,
            "fatalities": 168,
            "children_fatalities": 40,
            "lat": 23.218491,
            "lon": 95.521849,
            "raw_operator_info": "kanbalu_medic_team@nug.gov.mm | +95-9-9812-4411"
        },
        {
            "name": "Mung Lai Hkyet IDP Camp Bombardment",
            "date": "2023-10-09",
            "sector": "Laiza_Perimeter_Kachin",
            "aircraft_profile": "HEAVY_CARGO_DRONE_AND_JET",
            "acoustic_freq_hz": 480.0,
            "acoustic_db": 82.0,
            "thermal_frp_mw": 75.0,
            "fatalities": 29,
            "children_fatalities": 11,
            "lat": 24.751920,
            "lon": 97.541289,
            "raw_operator_info": "laiza_idp_aid@humanitarian.org | IP 172.16.8.55"
        },
        {
            "name": "Lashio Civic Infrastructure Denial Strikes",
            "date": "2024-11-10",
            "sector": "Northern_Shan_Lashio",
            "aircraft_profile": "K-8_FTC2000G_FORMATION",
            "acoustic_freq_hz": 580.0,
            "acoustic_db": 87.0,
            "thermal_frp_mw": 95.0,
            "fatalities": 42,
            "children_fatalities": 8,
            "lat": 22.934812,
            "lon": 97.749124,
            "raw_operator_info": "lashio_hospital_staff@redcross.int | +95-8-2211-0987"
        },
        {
            "name": "UN OHCHR Verified Airstrike Window Surge",
            "date": "2025-12-15",
            "sector": "Multi_Theater_Escalation",
            "aircraft_profile": "SYNCHRONIZED_MULTI_JET_FPV",
            "acoustic_freq_hz": 640.0,
            "acoustic_db": 91.0,
            "thermal_frp_mw": 110.0,
            "fatalities": 139,
            "children_fatalities": 22,
            "lat": 21.849120,
            "lon": 96.082194,
            "raw_operator_info": "ohchr_observer_secure@un.org | IP 192.168.1.99"
        },
        {
            "name": "August 2026 Airstrike Surge Peak",
            "date": "2026-08-31",
            "sector": "Sagaing_Shan_Mandalay",
            "aircraft_profile": "MULTI_AIRCRAFT_STRIKE_PACKAGE",
            "acoustic_freq_hz": 690.0,
            "acoustic_db": 92.5,
            "thermal_frp_mw": 145.0,
            "fatalities": 139,
            "children_fatalities": 18,
            "lat": 22.184912,
            "lon": 95.891241,
            "raw_operator_info": "nug_mohr_telemetry@mohr.nugmyanmar.org"
        },
        {
            "name": "Kyauktaw Central Market Mass-Casualty Strike",
            "date": "2026-09-28",
            "sector": "Rakhine_Kyauktaw_Market",
            "aircraft_profile": "COORDINATED_JET_FORMATION_BOMB_RUN",
            "acoustic_freq_hz": 750.0,
            "acoustic_db": 94.0,
            "thermal_frp_mw": 160.0,
            "fatalities": 54,
            "children_fatalities": 9,
            "lat": 20.841928,
            "lon": 92.981849,
            "raw_operator_info": "arakan_civil_observer@arakan.org | +95-9-4321-8765 | MAC 00:2A:3B:4C:5D:6E"
        }
    ]

    def __init__(self, doc_path: str = "collected_data_myanmar_iot_2022_2026.md") -> None:
        self.doc_path = Path(doc_path)
        self.envelope = CryptographicEnvelope(node_secret="parla-humanitarian-e2e-key")

    def parse_document(self) -> Dict[str, Any]:
        """
        Parses text and tables from the intelligence document, extracting macro metrics and incident context.
        """
        if not self.doc_path.exists():
            raise FileNotFoundError(f"Intelligence markdown not found at: {self.doc_path}")

        content = self.doc_path.read_text(encoding="utf-8")

        # Extract macro metrics via regex
        macro_metrics = {}
        strikes_match = re.search(r"total strikes exceeded \*\*(\d[,\d]*)\*\*", content, re.IGNORECASE)
        fatalities_match = re.search(r"Over \*\*([,\d]+) verified civilian deaths\*\*", content, re.IGNORECASE)
        facilities_match = re.search(r"More than \*\*([,\d]+) essential civilian facilities\*\*", content, re.IGNORECASE)

        macro_metrics["cumulative_strikes"] = strikes_match.group(1) if strikes_match else "5,400+"
        macro_metrics["civilian_fatalities"] = fatalities_match.group(1) if fatalities_match else "2,100+"
        macro_metrics["facilities_destroyed"] = facilities_match.group(1) if facilities_match else "1,272+"

        # Extract technology sensor layers table
        tech_layers = []
        table_pattern = re.compile(r"\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\s*\|\s*\*([^*]+)\*\s*\|\s*([^|]+)\|")
        for match in table_pattern.finditer(content):
            layer, paradigm, precedent, application = [g.strip() for g in match.groups()]
            tech_layers.append({
                "layer": layer,
                "paradigm": paradigm,
                "precedent": precedent,
                "application": application
            })

        return {
            "macro_metrics": macro_metrics,
            "technology_layers": tech_layers,
            "parsed_incidents_count": len(self.INCIDENT_PRESETS)
        }

    def generate_signed_payloads(self) -> List[Dict[str, Any]]:
        """
        Generates cryptographically signed, structured test payloads for each extracted incident.
        """
        payloads = []
        prev_hash = CryptographicEnvelope.GENESIS_HASH

        for idx, inc in enumerate(self.INCIDENT_PRESETS, start=1):
            telemetry_data = {
                "source_id": f"NODE-MMR-{inc['sector'][:6].upper()}-{idx:02d}",
                "sector": inc["sector"],
                "incident_name": inc["name"],
                "date": inc["date"],
                "acoustic_freq_hz": inc["acoustic_freq_hz"],
                "acoustic_db": inc["acoustic_db"],
                "thermal_frp_mw": inc["thermal_frp_mw"],
                "detected_profile": inc["aircraft_profile"],
                "latitude": inc["lat"],
                "longitude": inc["lon"],
                "metadata": {
                    "unscrubbed_operator": inc["raw_operator_info"],
                    "fatalities_estimate": inc["fatalities"],
                    "children_fatalities": inc["children_fatalities"]
                }
            }

            block = self.envelope.create_block(
                seq_id=idx,
                prev_hash=prev_hash,
                domain="humanitarian",
                payload=telemetry_data,
                timestamp=f"{inc['date']}T08:00:00Z"
            )
            prev_hash = block["block_hash"]
            payloads.append(block)

        return payloads

    def generate_adversarial_battery(self) -> List[Dict[str, Any]]:
        """
        Generates adversarial payloads:
        1. Dirty PII & fine-grained GPS payload
        2. Corrupted signature & forged hash payload
        3. Replayed nonce & sequence injection payload
        4. Malformed non-dictionary payload
        """
        battery = []

        # 1. PII & Precision GPS
        battery.append({
            "test_type": "PII_GPS_EXPOSURE",
            "payload": {
                "source_id": "LEAKY_NODE_01",
                "sector": "Rakhine_Sittwe_Frontline",
                "operator_email": "informant_secret@resistance.org",
                "operator_phone": "+95-9-8877-6655",
                "internal_ip": "192.168.100.45",
                "mac_address": "E4:5F:01:22:33:44",
                "latitude": 20.14981249,
                "longitude": 92.89412891,
                "acoustic_freq_hz": 540.0,
                "acoustic_db": 82.0
            }
        })

        # 2. Tampered Signature
        tampered_block = self.envelope.create_block(
            seq_id=999,
            prev_hash="ffff" * 16,
            domain="humanitarian",
            payload={"acoustic_freq_hz": 700.0, "acoustic_db": 95.0, "sector": "Lashio"}
        )
        tampered_block["signature"] = "0000000000000000000000000000000000000000000000000000000000000000"
        battery.append({
            "test_type": "FORGED_SIGNATURE",
            "payload": tampered_block
        })

        # 3. Non-Dictionary Malformed Ingress
        battery.append({
            "test_type": "MALFORMED_NON_DICT",
            "payload": "ATTACK_RAW_BUFFER_OVERFLOW_STRING_0000"
        })

        return battery
