"""
parla/core/knowledge_base.py
Parla's Structured Domain Knowledge Base
Offline, local, referenceable by NLP and acoustic processors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ============================================================
# 1. ACOUSTIC THREAT SIGNATURES
# ============================================================

@dataclass
class AcousticSignature:
    threat_type: str
    min_freq_hz: float
    max_freq_hz: float
    min_db: float
    max_db: float
    micro_doppler_range: Tuple[float, float]
    description: str
    confidence_weight: float


class AcousticKnowledgeBase:
    def __init__(self):
        self.signatures: Dict[str, AcousticSignature] = {
            "JET_FIGHTER": AcousticSignature(
                threat_type="JET_FIGHTER",
                min_freq_hz=80.0,
                max_freq_hz=400.0,
                min_db=95.0,
                max_db=140.0,
                micro_doppler_range=(120.0, 250.0),
                description="High-bypass turbofan jet engine signature",
                confidence_weight=0.95
            ),
            "ATTACK_HELICOPTER": AcousticSignature(
                threat_type="ATTACK_HELICOPTER",
                min_freq_hz=15.0,
                max_freq_hz=80.0,
                min_db=85.0,
                max_db=120.0,
                micro_doppler_range=(20.0, 80.0),
                description="Rotor blade pass frequency with harmonic overtones",
                confidence_weight=0.90
            ),
            "TRANSPORT_AIRCRAFT": AcousticSignature(
                threat_type="TRANSPORT_AIRCRAFT",
                min_freq_hz=40.0,
                max_freq_hz=200.0,
                min_db=80.0,
                max_db=110.0,
                micro_doppler_range=(60.0, 150.0),
                description="Multi-engine propeller or turboprop signature",
                confidence_weight=0.75
            ),
            "UAV_DRONE": AcousticSignature(
                threat_type="UAV_DRONE",
                min_freq_hz=100.0,
                max_freq_hz=800.0,
                min_db=60.0,
                max_db=90.0,
                micro_doppler_range=(200.0, 600.0),
                description="Small electric motor with high-RPM propellers",
                confidence_weight=0.85
            ),
            "ARTILLERY": AcousticSignature(
                threat_type="ARTILLERY",
                min_freq_hz=20.0,
                max_freq_hz=500.0,
                min_db=110.0,
                max_db=160.0,
                micro_doppler_range=(0.0, 10.0),
                description="Impulsive broadband signature with shockwave",
                confidence_weight=0.88
            ),
            "SMALL_ARMS": AcousticSignature(
                threat_type="SMALL_ARMS",
                min_freq_hz=200.0,
                max_freq_hz=2000.0,
                min_db=90.0,
                max_db=130.0,
                micro_doppler_range=(0.0, 5.0),
                description="Rapid impulsive crack signatures",
                confidence_weight=0.70
            ),
            "EXPLOSION": AcousticSignature(
                threat_type="EXPLOSION",
                min_freq_hz=10.0,
                max_freq_hz=300.0,
                min_db=120.0,
                max_db=170.0,
                micro_doppler_range=(0.0, 5.0),
                description="Low-frequency shockwave with extended decay",
                confidence_weight=0.92
            )
        }
    
    def identify_threat(self, acoustic_db: float, doppler_hz: float, freq_hz: Optional[float] = None) -> List[Tuple[str, float]]:
        matches = []
        
        for sig_name, sig in self.signatures.items():
            confidence = 0.0
            
            if sig.min_db <= acoustic_db <= sig.max_db:
                confidence += 0.4
            elif acoustic_db > sig.max_db:
                confidence += 0.2
            
            if sig.micro_doppler_range[0] <= doppler_hz <= sig.micro_doppler_range[1]:
                confidence += 0.4
            elif doppler_hz > sig.micro_doppler_range[1]:
                confidence += 0.1
            
            if freq_hz is not None:
                if sig.min_freq_hz <= freq_hz <= sig.max_freq_hz:
                    confidence += 0.2
            
            final_confidence = confidence * sig.confidence_weight
            
            if final_confidence > 0.1:
                matches.append((sig_name, final_confidence))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def get_signature(self, threat_type: str) -> Optional[AcousticSignature]:
        return self.signatures.get(threat_type)


# ============================================================
# 2. OSINT CLASSIFICATION RULES
# ============================================================

@dataclass
class ClassificationRule:
    event_type: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    risk_weight: float
    response_protocol: str


class OSINTKnowledgeBase:
    def __init__(self):
        self.rules: Dict[str, ClassificationRule] = {
            "AIRSTRIKE": ClassificationRule(
                event_type="AIRSTRIKE",
                primary_keywords=["airstrike", "air raid", "bombing", "aerial attack", "air strike"],
                secondary_keywords=["jet", "aircraft", "fighter", "bomb", "missile", "munitions"],
                risk_weight=10.0,
                response_protocol="Immediate shelter warning. Pre-position medical teams. Monitor for secondary strikes."
            ),
            "GROUND_CONFLICT": ClassificationRule(
                event_type="GROUND_CONFLICT",
                primary_keywords=["ground fighting", "clashes", "military operation", "shelling", "artillery"],
                secondary_keywords=["infantry", "tanks", "armored", "artillery", "mortar"],
                risk_weight=7.0,
                response_protocol="Evacuation corridors. Medical aid staging. Displacement tracking."
            ),
            "DISPLACEMENT": ClassificationRule(
                event_type="DISPLACEMENT",
                primary_keywords=["displaced", "refugees", "evacuation", "fled", "migration", "IDP"],
                secondary_keywords=["camp", "shelter", "border", "crossing", "fleeing"],
                risk_weight=5.0,
                response_protocol="Aid distribution points. Medical screening. Family reunification tracking."
            ),
            "HUMANITARIAN_CRISIS": ClassificationRule(
                event_type="HUMANITARIAN_CRISIS",
                primary_keywords=["famine", "starvation", "medical shortage", "aid blocked", "siege"],
                secondary_keywords=["food insecurity", "water shortage", "disease", "malnutrition"],
                risk_weight=8.0,
                response_protocol="Emergency aid corridor negotiation. Medical supply airdrop consideration."
            ),
            "INFRASTRUCTURE_ATTACK": ClassificationRule(
                event_type="INFRASTRUCTURE_ATTACK",
                primary_keywords=["hospital hit", "school bombed", "power grid", "water supply"],
                secondary_keywords=["civilian infrastructure", "UN facility", "aid convoy"],
                risk_weight=9.0,
                response_protocol="Document for international reporting. Emergency rerouting of aid."
            )
        }
    
    def classify_text(self, text: str) -> List[Tuple[str, float]]:
        text_lower = text.lower()
        matches = []
        
        for event_type, rule in self.rules.items():
            score = 0.0
            
            primary_hits = sum(1 for kw in rule.primary_keywords if kw in text_lower)
            score += primary_hits * 0.3
            
            secondary_hits = sum(1 for kw in rule.secondary_keywords if kw in text_lower)
            score += secondary_hits * 0.1
            
            confidence = min(score, 1.0)
            
            if confidence > 0.1:
                matches.append((event_type, confidence))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def get_response_protocol(self, event_type: str) -> Optional[str]:
        rule = self.rules.get(event_type)
        return rule.response_protocol if rule else None
    
    def get_risk_weight(self, event_type: str) -> float:
        rule = self.rules.get(event_type)
        return rule.risk_weight if rule else 1.0


# ============================================================
# 3. MYANMAR REGIONAL CONTEXT (2022-2026)
# ============================================================

@dataclass
class RegionalContext:
    region_hash: str
    description: str
    historical_risk_level: str
    primary_threats: List[str]
    seasonal_patterns: Dict[str, str]
    humanitarian_access: str


class MyanmarRegionalContext:
    def __init__(self):
        self.contexts: Dict[str, RegionalContext] = {
            "8f7e6d5c4b3a2918": RegionalContext(
                region_hash="8f7e6d5c4b3a2918",
                description="Central region - high aerial activity zone",
                historical_risk_level="CRITICAL",
                primary_threats=["AIRSTRIKE", "GROUND_CONFLICT"],
                seasonal_patterns={
                    "dry_season": "Increased aerial activity due to visibility",
                    "monsoon": "Reduced aerial operations, increased ground movement"
                },
                humanitarian_access="RESTRICTED"
            ),
            "3a4b5c6d7e8f9012": RegionalContext(
                region_hash="3a4b5c6d7e8f9012",
                description="Northwestern region - ground conflict zone",
                historical_risk_level="HIGH",
                primary_threats=["GROUND_CONFLICT", "DISPLACEMENT"],
                seasonal_patterns={
                    "dry_season": "Active ground operations",
                    "monsoon": "Displacement increases due to flooding + conflict"
                },
                humanitarian_access="RESTRICTED"
            ),
            "9f8e7d6c5b4a3928": RegionalContext(
                region_hash="9f8e7d6c5b4a3928",
                description="Eastern region - mixed threat profile",
                historical_risk_level="HIGH",
                primary_threats=["AIRSTRIKE", "HUMANITARIAN_CRISIS"],
                seasonal_patterns={
                    "dry_season": "Airstrike campaigns",
                    "monsoon": "Humanitarian access challenges"
                },
                humanitarian_access="BLOCKED"
            ),
            "1b2c3d4e5f6a7b8c": RegionalContext(
                region_hash="1b2c3d4e5f6a7b8c",
                description="Southern region - displacement corridor",
                historical_risk_level="MEDIUM",
                primary_threats=["DISPLACEMENT"],
                seasonal_patterns={
                    "dry_season": "Population movement",
                    "monsoon": "Camp overcrowding"
                },
                humanitarian_access="OPEN"
            ),
            "4d5e6f7a8b9c0d1e": RegionalContext(
                region_hash="4d5e6f7a8b9c0d1e",
                description="Western region - aerial threat zone",
                historical_risk_level="CRITICAL",
                primary_threats=["AIRSTRIKE"],
                seasonal_patterns={
                    "dry_season": "Sustained aerial campaigns",
                    "monsoon": "Reduced but persistent"
                },
                humanitarian_access="RESTRICTED"
            ),
            "2c3d4e5f6a7b8c9d": RegionalContext(
                region_hash="2c3d4e5f6a7b8c9d",
                description="Central-east region - humanitarian crisis",
                historical_risk_level="HIGH",
                primary_threats=["HUMANITARIAN_CRISIS", "GROUND_CONFLICT"],
                seasonal_patterns={
                    "dry_season": "Aid access challenges",
                    "monsoon": "Disease outbreak risk"
                },
                humanitarian_access="BLOCKED"
            )
        }
    
    def get_context(self, region_hash: str) -> Optional[RegionalContext]:
        return self.contexts.get(region_hash)
    
    def get_seasonal_advisory(self, region_hash: str, season: str) -> Optional[str]:
        context = self.contexts.get(region_hash)
        if context and season in context.seasonal_patterns:
            return context.seasonal_patterns[season]
        return None


# ============================================================
# 4. HUMANITARIAN RESPONSE PROTOCOLS
# ============================================================

class HumanitarianProtocols:
    PROTOCOLS = {
        "IMMEDIATE_SHELTER": {
            "trigger": "AIRSTRIKE with confidence > 0.85",
            "actions": [
                "Activate local siren network immediately",
                "Broadcast shelter-in-place directive via LoRa mesh",
                "Notify pre-positioned medical teams",
                "Document event for humanitarian reporting"
            ],
            "time_window_minutes": 4
        },
        "EVACUATION": {
            "trigger": "GROUND_CONFLICT with confidence > 0.75",
            "actions": [
                "Identify safe evacuation corridors",
                "Coordinate with local community leaders",
                "Pre-position transport and medical aid",
                "Track displacement numbers"
            ],
            "time_window_minutes": 30
        },
        "AID_DELIVERY": {
            "trigger": "HUMANITARIAN_CRISIS with confidence > 0.70",
            "actions": [
                "Negotiate humanitarian access corridors",
                "Coordinate with UN agencies",
                "Pre-position medical supplies",
                "Establish distribution points"
            ],
            "time_window_minutes": 1440
        },
        "MONITOR": {
            "trigger": "Any event with confidence 0.50 - 0.75",
            "actions": [
                "Increase sensor sensitivity",
                "Cross-reference with satellite data",
                "Alert regional coordinators",
                "Prepare response teams"
            ],
            "time_window_minutes": 60
        }
    }
    
    @classmethod
    def get_protocol(cls, event_type: str, confidence: float) -> Optional[Dict]:
        if event_type == "AIRSTRIKE" and confidence > 0.85:
            return cls.PROTOCOLS["IMMEDIATE_SHELTER"]
        elif event_type == "GROUND_CONFLICT" and confidence > 0.75:
            return cls.PROTOCOLS["EVACUATION"]
        elif event_type == "HUMANITARIAN_CRISIS" and confidence > 0.70:
            return cls.PROTOCOLS["AID_DELIVERY"]
        elif confidence >= 0.50:
            return cls.PROTOCOLS["MONITOR"]
        return None


# ============================================================
# 5. UNIFIED KNOWLEDGE BASE
# ============================================================

class ParlaKnowledgeBase:
    def __init__(self):
        self.acoustic = AcousticKnowledgeBase()
        self.osint = OSINTKnowledgeBase()
        self.regional = MyanmarRegionalContext()
        self.protocols = HumanitarianProtocols()
    
    def analyze_acoustic(self, acoustic_db: float, doppler_hz: float, freq_hz: Optional[float] = None) -> Dict:
        matches = self.acoustic.identify_threat(acoustic_db, doppler_hz, freq_hz)
        return {
            "threat_matches": matches,
            "primary_threat": matches[0][0] if matches else "UNKNOWN",
            "confidence": matches[0][1] if matches else 0.0,
            "protocol": self.protocols.get_protocol(
                matches[0][0] if matches else "UNKNOWN",
                matches[0][1] if matches else 0.0
            )
        }
    
    def analyze_osint(self, text: str) -> Dict:
        matches = self.osint.classify_text(text)
        primary_event = matches[0][0] if matches else "UNKNOWN"
        confidence = matches[0][1] if matches else 0.0
        
        return {
            "event_matches": matches,
            "primary_event": primary_event,
            "confidence": confidence,
            "risk_weight": self.osint.get_risk_weight(primary_event),
            "response_protocol": self.osint.get_response_protocol(primary_event),
            "action_protocol": self.protocols.get_protocol(primary_event, confidence)
        }
    
    def get_regional_context(self, region_hash: str) -> Optional[Dict]:
        context = self.regional.get_context(region_hash)
        if not context:
            return None
        
        return {
            "description": context.description,
            "historical_risk": context.historical_risk_level,
            "primary_threats": context.primary_threats,
            "humanitarian_access": context.humanitarian_access,
            "seasonal_advisory_dry": context.seasonal_patterns.get("dry_season"),
            "seasonal_advisory_monsoon": context.seasonal_patterns.get("monsoon")
        }


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    kb = ParlaKnowledgeBase()
    
    print("=" * 70)
    print("📚 PARLA DOMAIN KNOWLEDGE BASE - SELF-TEST")
    print("=" * 70)
    
    print("\n[1] ACOUSTIC THREAT IDENTIFICATION")
    print("-" * 70)
    acoustic_result = kb.analyze_acoustic(acoustic_db=95.0, doppler_hz=180.0)
    print(f"  Input: 95dB, 180Hz Doppler")
    print(f"  Primary Threat: {acoustic_result['primary_threat']}")
    print(f"  Confidence: {acoustic_result['confidence']:.2f}")
    print(f"  Top 3 Matches:")
    for threat, conf in acoustic_result['threat_matches'][:3]:
        print(f"    • {threat}: {conf:.2f}")
    
    print("\n[2] OSINT TEXT CLASSIFICATION")
    print("-" * 70)
    test_text = "Multiple airstrikes reported in central region with civilian casualties"
    osint_result = kb.analyze_osint(test_text)
    print(f"  Input: '{test_text}'")
    print(f"  Primary Event: {osint_result['primary_event']}")
    print(f"  Confidence: {osint_result['confidence']:.2f}")
    print(f"  Risk Weight: {osint_result['risk_weight']}")
    print(f"  Response Protocol: {osint_result['response_protocol']}")
    
    print("\n[3] REGIONAL CONTEXT RETRIEVAL")
    print("-" * 70)
    region_hash = "8f7e6d5c4b3a2918"
    regional_result = kb.get_regional_context(region_hash)
    if regional_result:
        print(f"  Region Hash: {region_hash}")
        print(f"  Description: {regional_result['description']}")
        print(f"  Historical Risk: {regional_result['historical_risk']}")
        print(f"  Primary Threats: {regional_result['primary_threats']}")
        print(f"  Humanitarian Access: {regional_result['humanitarian_access']}")
        print(f"  Dry Season: {regional_result['seasonal_advisory_dry']}")
        print(f"  Monsoon: {regional_result['seasonal_advisory_monsoon']}")
    
    print("\n[4] HUMANITARIAN PROTOCOL SELECTION")
    print("-" * 70)
    protocol = kb.protocols.get_protocol("AIRSTRIKE", 0.90)
    if protocol:
        print(f"  Trigger: {protocol['trigger']}")
        print(f"  Time Window: {protocol['time_window_minutes']} minutes")
        print(f"  Actions:")
        for action in protocol['actions']:
            print(f"    • {action}")
    
    print("\n" + "=" * 70)
    print("✓ KNOWLEDGE BASE SELF-TEST COMPLETE")
    print("=" * 70)