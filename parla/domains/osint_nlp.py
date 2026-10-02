"""
OSINT Text Mining & Event Extraction Module
Domain: Parla Autonomous Operations Research Node
Architecture: Offline-First NLP, Zero-Trust Cryptographic Ledger, Hard PII Redaction,
              Admiralty 6x6 Multi-INT Fusion, Tactical Fleet & Ordnance Knowledge Linking
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import re
import hmac
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple

import spacy
from spacy.language import Language

from parla.core.ledger import OfflineLedger
from parla.core.security import compute_sha256, canonical_json
from parla.core.feedback_loop import FeedbackLoop
from parla.domains.admiralty_evaluator import (
    AdmiraltyEvaluator,
    SourceReliability,
    InformationCredibility,
    AdmiraltyAssessment
)

# Default Zero-Trust Secret Key for Local Node Payload Signing
DEFAULT_OSINT_SECRET = b"parla-zero-trust-offline-root-key"

# Strict Regex Patterns for Pre-NLP PII Interception
REGEX_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b')
REGEX_IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
REGEX_IPV6 = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
REGEX_MAC = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b')
REGEX_PHONE = re.compile(r'(?:(?:\+|00)\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b')
REGEX_GOV_ID = re.compile(r'\b(?:NRC|ID|PASSPORT|EMP|OP)[-_#]?\d{5,12}\b', re.IGNORECASE)
REGEX_EXACT_COORDS = re.compile(r'[-+]?\d{1,2}\.\d{4,}\s*,\s*[-+]?\d{1,3}\.\d{4,}')

# Broad Region Lexicon for Safe Generalization
BROAD_REGIONS = {
    "SAGAING": ["sagaing", "tabayin", "kanbalu", "pa zi gyi", "let yet kone", "depayin"],
    "RAKHINE": ["rakhine", "arakan", "kyauktaw", "mrauk-u", "minbya", "sittwe", "paletwa", "maungdaw", "buthidaung"],
    "SHAN_NORTH": ["shan", "lashio", "laukkai", "kokang", "hsipaw", "kyaukme", "kutkai", "chinshwehaw"],
    "KACHIN": ["kachin", "hpakant", "laiza", "myitkyina", "bhamo", "a nang pa", "mung lai hkyet"],
    "CHIN": ["chin", "hakha", "mindat", "kanpetlet", "matupi", "tedim"],
    "KAYAH": ["kayah", "karenni", "demoso", "loikaw", "bawlake", "shadaw"],
    "KAYIN": ["kayin", "karen", "myawaddy", "kawkareik", "dupalaya"],
    "MAGWAY": ["magway", "pauk", "gangaw", "myaing", "yesagyo"],
    "MANDALAY": ["mandalay", "pyin oo lwin", "myingyan", "meiktila"],
    "YANGON": ["yangon", "insein", "hlaing"]
}

# Event Classification Lexicon
EVENT_TAXONOMY = {
    "AIRSTRIKE": [
        "airstrike", "air strike", "aerial attack", "bombing", "jet fighter", "su-30",
        "yak-130", "k-8", "ftc-2000g", "mi-35", "cluster munition", "thermobaric",
        "dropped bombs", "bombed", "air raid", "strike package"
    ],
    "ARTILLERY_SHELLING": [
        "artillery", "shelling", "mortar", "howitzer", "heavy weapons", "bombardment", "shelled"
    ],
    "GROUND_CONFLICT": [
        "clash", "firefight", "infantry assault", "skirmish", "raid", "ambush",
        "ground offensive", "military column", "junta soldiers"
    ],
    "DISPLACEMENT": [
        "displacement", "displaced", "idp", "fleeing", "refugee", "evacuation",
        "internally displaced", "camp bombarded", "villagers fled"
    ],
    "CIVIC_INFRASTRUCTURE_ATTACK": [
        "hospital", "clinic", "monastery", "church", "school", "central market",
        "power grid", "telecom tower", "civilian settlement"
    ]
}

# Tactical Knowledge Matrices Linked to Project Skills
TACTICAL_AIRCRAFT_MATRIX: Dict[str, Dict[str, Any]] = {
    "SU_30SME": {
        "keywords": ["su-30", "su30", "flanker"],
        "origin_bases": ["Naypyidaw (Ela)", "Tada-U (Mandalay)"],
        "acoustic_signature": "Twin turbofan AL-31FP roar (40-120 Hz), supersonic boom, 120-140 dB",
        "primary_ordnance": ["ODAB-500PM thermobaric", "FAB-500", "KAB-500Kr"],
        "threat_level": "EXTREME_STRATEGIC"
    },
    "YAK_130": {
        "keywords": ["yak-130", "yak130", "mitten"],
        "origin_bases": ["Tada-U", "Taungoo", "Meiktila"],
        "acoustic_signature": "Twin turbofan AI-222-25 whine (1.2-8.0 kHz), 110-125 dB",
        "primary_ordnance": ["FAB-250", "OFAB-100-120", "B-8M1 S-8 rockets", "23mm gun pod"],
        "threat_level": "HIGH_TACTICAL_CAS"
    },
    "MIG_29": {
        "keywords": ["mig-29", "mig29", "fulcrum"],
        "origin_bases": ["Tada-U", "Magway", "Yangon-Mingaladon"],
        "acoustic_signature": "RD-33 twin turbofan smoke roar (80-220 Hz), 115-135 dB",
        "primary_ordnance": ["FAB-500", "FAB-250", "S-8 rockets", "30mm GSh-30-1"],
        "threat_level": "HIGH_FAST_JET"
    },
    "K_8_KARAKORUM": {
        "keywords": ["k-8", "k8", "karakorum"],
        "origin_bases": ["Taungoo", "Meiktila", "Hmawbi"],
        "acoustic_signature": "Garrett TFE731 turbofan (high-pitch whistle 2.5-6.0 kHz), 100-115 dB",
        "primary_ordnance": ["57mm unguided rockets", "Type 23-1 gun pod", "250kg bombs"],
        "threat_level": "MEDIUM_LIGHT_ATTACK"
    },
    "MI_35P_HIND": {
        "keywords": ["mi-35", "mi35", "hind", "gunship helicopter"],
        "origin_bases": ["Meiktila", "Magway", "Myitkyina"],
        "acoustic_signature": "Rotor blade slap (18.5-23.0 Hz fundamental), twin Isotov TV3-117 whine, 115-130 dB",
        "primary_ordnance": ["GSh-30-2K twin 30mm cannon", "9M114/9M120 ATGM", "S-8 rockets"],
        "threat_level": "HIGH_GUNSHIP"
    },
    "FTC_2000G": {
        "keywords": ["ftc-2000g", "ftc2000g", "mountain eagle"],
        "origin_bases": ["Namhsan", "Tada-U"],
        "acoustic_signature": "WP-13 turbojet (piercing high-frequency shrieking), 120-135 dB",
        "primary_ordnance": ["250kg unguided bombs", "rocket pods", "PL-9/PL-8"],
        "threat_level": "MEDIUM_LIGHT_FIGHTER"
    }
}

TACTICAL_ORDNANCE_MATRIX: Dict[str, Dict[str, Any]] = {
    "THERMOBARIC_ODAB": {
        "keywords": ["thermobaric", "fuel-air explosive", "fae", "odab", "vacuum bomb"],
        "lethal_radius_m": 150,
        "hazard_type": "Overpressure blast wave and vacuum lung collapse",
        "humanitarian_flag": "MASS_CASUALTY_CIVILIAN_HAZARD"
    },
    "FAB_500_DEMOLITION": {
        "keywords": ["fab-500", "fab500", "500kg bomb", "500 kg bomb", "heavy bomb"],
        "lethal_radius_m": 120,
        "hazard_type": "Deep structural cratering and extreme fragmentation",
        "humanitarian_flag": "STRUCTURE_DEMOLITION"
    },
    "CLUSTER_MUNITIONS": {
        "keywords": ["cluster bomb", "cluster munition", "submunition", "bomblet", "unexploded bomblets"],
        "lethal_radius_m": 300,
        "hazard_type": "Wide-area bomblet saturation with delayed detonation risk",
        "humanitarian_flag": "UNEXPLODED_ORDNANCE_UXO"
    },
    "HEAVY_ARTILLERY_122MM": {
        "keywords": ["122mm", "howitzer", "d-30", "d30", "artillery battery"],
        "lethal_radius_m": 50,
        "hazard_type": "Kinetic fragmentation and indirect area shelling",
        "humanitarian_flag": "CIVILIAN_SHELLING"
    }
}


class OSINTEventExtractor:
    """
    Offline OSINT Text Mining and Structured Event Extraction Engine.
    Executes deep PII sanitization via spaCy NER and Regex, evaluates events,
    verifies cryptographic signatures, grades through NATO Admiralty 6x6,
    and seals records into the Merkle ledger.
    """

    def __init__(
        self,
        ledger: Optional[OfflineLedger] = None,
        secret_key: bytes = DEFAULT_OSINT_SECRET,
        spacy_model: str = "en_core_web_sm",
        admiralty_evaluator: Optional[AdmiraltyEvaluator] = None
    ) -> None:
        self.ledger: OfflineLedger = ledger or OfflineLedger()
        self.secret_key: bytes = secret_key
        self.nlp: Language = self._load_spacy_engine(spacy_model)
        self.feedback: FeedbackLoop = FeedbackLoop()
        self.admiralty: AdmiraltyEvaluator = admiralty_evaluator or AdmiraltyEvaluator()

    def _load_spacy_engine(self, model_name: str) -> Language:
        """Loads offline spaCy model with optimized disabled pipes for high-throughput processing."""
        try:
            return spacy.load(model_name, disable=["parser"])
        except Exception:
            return spacy.load(model_name)

    def _get_dynamic_threshold(self, event_type: str) -> float:
        """Get the dynamically adjusted confidence threshold for this event type."""
        thresholds = self.feedback.get_current_thresholds()
        return thresholds.get(event_type, 0.70)

    def verify_payload_signature(self, text: str, signature: str, timestamp: str = "") -> bool:
        """
        Zero-Trust Signature Verification:
        Recomputes HMAC-SHA256 signature over canonical message: timestamp|text
        and performs constant-time equality check.
        """
        if not signature:
            return False
        message: str = f"{timestamp}|{text}" if timestamp else text
        expected_sig: str = hmac.new(
            self.secret_key,
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature.strip(), expected_sig)

    @classmethod
    def redact_pii(cls, text: str, nlp_engine: Language) -> str:
        """
        Hard Constraint: Two-Tier PII Redaction
        Tier 1: High-entropy regex scrubbing (Emails, IPs, MACs, Phones, National IDs, Exact Coordinates).
        Tier 2: spaCy NER token substitution (PERSON entities and specific identifying locations).
        """
        if not text:
            return ""

        # --- Tier 1: Regex Interception ---
        scrubbed = REGEX_EMAIL.sub("[REDACTED_EMAIL]", text)
        scrubbed = REGEX_IPV4.sub("[REDACTED_IP]", scrubbed)
        scrubbed = REGEX_IPV6.sub("[REDACTED_IP]", scrubbed)
        scrubbed = REGEX_MAC.sub("[REDACTED_MAC]", scrubbed)
        scrubbed = REGEX_PHONE.sub("[REDACTED_PHONE]", scrubbed)
        scrubbed = REGEX_GOV_ID.sub("[REDACTED_ID]", scrubbed)
        scrubbed = REGEX_EXACT_COORDS.sub("[REDACTED_COORDINATES]", scrubbed)

        # --- Tier 2: spaCy Named Entity Recognition (NER) ---
        doc = nlp_engine(scrubbed)
        
        redaction_spans = []
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "FAC"):
                redaction_spans.append((ent.start_char, ent.end_char))

        redaction_spans.sort(key=lambda x: x[0], reverse=True)
        text_chars = list(scrubbed)
        for start, end in redaction_spans:
            text_chars[start:end] = list("[REDACTED]")

        final_clean = "".join(text_chars)
        return final_clean

    def _extract_tactical_entities(self, text_lower: str) -> Dict[str, Any]:
        """Extracts and enriches aircraft and ordnance from domain knowledge skills."""
        matched_aircraft = []
        for ac_id, data in TACTICAL_AIRCRAFT_MATRIX.items():
            if any(kw in text_lower for kw in data["keywords"]):
                matched_aircraft.append({
                    "aircraft_type": ac_id,
                    "origin_bases": data["origin_bases"],
                    "acoustic_signature": data["acoustic_signature"],
                    "primary_ordnance": data["primary_ordnance"],
                    "threat_level": data["threat_level"]
                })

        matched_ordnance = []
        for ord_id, data in TACTICAL_ORDNANCE_MATRIX.items():
            if any(kw in text_lower for kw in data["keywords"]):
                matched_ordnance.append({
                    "ordnance_type": ord_id,
                    "lethal_radius_m": data["lethal_radius_m"],
                    "hazard_type": data["hazard_type"],
                    "humanitarian_flag": data["humanitarian_flag"]
                })

        return {
            "aircraft": matched_aircraft,
            "ordnance": matched_ordnance
        }

    def _detect_contradictions(self, text_lower: str) -> List[str]:
        """Flags contradictory assertions within the source text."""
        contradictions = []
        has_destructive_claim = any(kw in text_lower for kw in ["airstrike", "bombing", "destroyed", "massacre", "heavy casualties"])
        has_peaceful_claim = any(kw in text_lower for kw in ["no damage", "no casualties", "routine patrol without incident", "completely peaceful"])
        if has_destructive_claim and has_peaceful_claim:
            contradictions.append("MUTUALLY_EXCLUSIVE_IMPACT_CLAIMS")
        return contradictions

    def _detect_event_type(self, text_lower: str) -> Tuple[str, float]:
        """Classifies primary event type and computes confidence score."""
        scores: Dict[str, int] = {}
        for event_name, keywords in EVENT_TAXONOMY.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                scores[event_name] = count

        if not scores:
            return "GENERAL_CONFLICT_REPORT", 0.40

        top_event = max(scores.items(), key=lambda x: x[1])
        confidence = min(0.50 + (top_event[1] * 0.12), 0.98)
        return top_event[0], round(confidence, 2)

    def _detect_broad_region(self, text_lower: str) -> str:
        """Identifies broad region without revealing micro-settlement coordinates."""
        for region_code, aliases in BROAD_REGIONS.items():
            for alias in aliases:
                if alias in text_lower:
                    return f"MYANMAR_REGION_{region_code}"
        return "MYANMAR_REGION_UNSPECIFIED"

    def _extract_timeframe(self, text: str, doc: Any) -> str:
        """Extracts timeframe via spaCy DATE entities or fallback ISO regex."""
        for ent in doc.ents:
            if ent.label_ == "DATE":
                clean_ent = ent.text.strip()
                if len(clean_ent) >= 4 and not clean_ent.isdigit() or len(clean_ent) == 4:
                    return clean_ent

        date_match = re.search(r'\b(202[1-6](?:-\d{2}(?:-\d{2})?)?)\b', text)
        if date_match:
            return date_match.group(1)

        return time.strftime("%Y-%m", time.gmtime())

    def process_osint_payload(
        self,
        raw_text: str,
        signature: str,
        timestamp: str = "",
        source_id: str = "OSINT_SOURCE_ANON",
        source_reliability: str = "C",
        base_credibility: int = 3,
        corroborating_evidence: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Full Zero-Trust OSINT Ingestion & Admiralty Multi-INT Triangulation Pipeline:
        1. Verify cryptographic HMAC signature. If invalid, drops and quarantines.
        2. Computes source text SHA-256 hash.
        3. Executes hard PII redaction using regex + spaCy NER.
        4. Extracts tactical entities (Aircraft, Ordnance) linking to domain skills.
        5. Evaluates NATO 6x6 Admiralty score with multi-INT elevation (FIRMS, ADS-B, etc.).
        6. Applies dynamic feedback thresholds.
        7. Seals sanitized event atomically into the Merkle offline ledger.
        """
        # Step 1: Zero-Trust Signature Verification
        if not self.verify_payload_signature(raw_text, signature, timestamp=timestamp):
            reason_msg = "INVALID_CRYPTOGRAPHIC_SIGNATURE"
            self.ledger._quarantine(
                domain="osint_nlp",
                source_id=source_id,
                reason=reason_msg,
                raw_payload=raw_text[:250]
            )
            return {
                "status": "DROPPED_AND_QUARANTINED",
                "reason": reason_msg,
                "ledger_hash": None,
                "event": None
            }

        # Step 2: Source Text Integrity Hash
        source_text_hash: str = compute_sha256(raw_text)

        # Step 3: Hard PII Redaction
        redacted_text: str = self.redact_pii(raw_text, self.nlp)

        # Step 4: NLP Event, Tactical Entity, and Region Extraction
        doc = self.nlp(redacted_text)
        text_lower = redacted_text.lower()

        event_type, raw_confidence = self._detect_event_type(text_lower)
        broad_region = self._detect_broad_region(text_lower)
        region_hash: str = compute_sha256(broad_region)
        timeframe: str = self._extract_timeframe(redacted_text, doc)
        tactical_intel = self._extract_tactical_entities(text_lower)
        contradictions = self._detect_contradictions(text_lower)

        # Step 5: Admiralty 6x6 Multi-INT Evaluation
        assessment = self.admiralty.evaluate(
            reliability=SourceReliability(source_reliability),
            credibility=InformationCredibility(base_credibility),
            corroborating_evidence=corroborating_evidence,
            contradiction_evidence=contradictions
        )

        # Step 6: Apply Dynamic Confidence Threshold & Tactical Action
        dynamic_threshold = self._get_dynamic_threshold(event_type)
        is_actionable = assessment.actionable_for_civilian_protection or (assessment.elevated_confidence >= dynamic_threshold)
        action = "ALERT" if is_actionable else "MONITOR"

        # If tactical aircraft or mass-casualty ordnance detected, escalate action description
        tactical_threats = [a["threat_level"] for a in tactical_intel.get("aircraft", [])]
        if "EXTREME_STRATEGIC" in tactical_threats or any(o.get("humanitarian_flag") == "MASS_CASUALTY_CIVILIAN_HAZARD" for o in tactical_intel.get("ordnance", [])):
            action = "URGENT_CIVILIAN_SHELTER_ALERT"

        structured_event: Dict[str, Any] = {
            "event_type": event_type,
            "region_hash": region_hash,
            "broad_region": broad_region,
            "timeframe": timeframe,
            "confidence": assessment.elevated_confidence,
            "base_confidence": raw_confidence,
            "admiralty_grade": assessment.elevated_grade,
            "admiralty_initial": assessment.initial_grade,
            "source_text_hash": source_text_hash,
            "dynamic_threshold": dynamic_threshold,
            "action": action,
            "tactical_intel": tactical_intel,
            "contradictions": contradictions,
            "corroborations": [c.get("modality") for c in (corroborating_evidence or [])]
        }

        # Step 7: Seal into Merkle Offline Ledger
        ledger_payload: Dict[str, Any] = {
            "source_id": source_id,
            "timestamp": timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "structured_event": structured_event,
            "redacted_text_snippet": redacted_text[:200]
        }

        success, err, block = self.ledger.record_event(
            domain="osint_nlp",
            payload=ledger_payload,
            source_id=source_id,
            coarsen_gps=True
        )

        ledger_hash: str = block["block_hash"] if (success and block) else "QUARANTINE_ERROR"

        return {
            "status": "SEALED",
            "ledger_hash": ledger_hash,
            "seq_id": block["seq_id"] if block else -1,
            "event": structured_event,
            "alert_id": f"OSINT-{block['seq_id']:06d}" if block else None
        }


def generate_osint_signature(text: str, timestamp: str = "", secret_key: bytes = DEFAULT_OSINT_SECRET) -> str:
    """Helper utility for legitimate edge nodes and feeds to sign payloads before transmission."""
    message = f"{timestamp}|{text}" if timestamp else text
    return hmac.new(secret_key, message.encode("utf-8"), hashlib.sha256).hexdigest()