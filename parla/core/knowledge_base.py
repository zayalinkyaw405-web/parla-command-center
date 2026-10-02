"""
parla/core/knowledge_base.py
Parla's Structured Domain Knowledge Base
Offline, local, referenceable by NLP and acoustic processors.
"""

from dataclasses import dataclass, field, asdict
import typing
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json
from pathlib import Path


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
    """
    Parla OSINT Knowledge Base:
    - Multi-category conflict & humanitarian taxonomy
    - Standardized NATO 6x6 Admiralty assessment
    - Tactical entity extraction (SAC aircraft, military ordnance, EAO factions)
    - IMINT / GEOINT space-time parameters (NASA FIRMS, Sentinel-2 spectral indices)
    - Contradiction & disinformation filtering
    """

    # NATO 6x6 Baseline Confidence Lookup Table
    BASE_ADMIRALTY_TABLE: Dict[Tuple[str, int], float] = {
        ("A", 1): 0.98, ("A", 2): 0.90, ("A", 3): 0.80, ("A", 4): 0.50, ("A", 5): 0.20, ("A", 6): 0.40,
        ("B", 1): 0.92, ("B", 2): 0.85, ("B", 3): 0.75, ("B", 4): 0.45, ("B", 5): 0.18, ("B", 6): 0.35,
        ("C", 1): 0.88, ("C", 2): 0.75, ("C", 3): 0.65, ("C", 4): 0.38, ("C", 5): 0.15, ("C", 6): 0.30,
        ("D", 1): 0.70, ("D", 2): 0.55, ("D", 3): 0.45, ("D", 4): 0.25, ("D", 5): 0.10, ("D", 6): 0.20,
        ("E", 1): 0.40, ("E", 2): 0.30, ("E", 3): 0.20, ("E", 4): 0.10, ("E", 5): 0.05, ("E", 6): 0.10,
        ("F", 1): 0.80, ("F", 2): 0.60, ("F", 3): 0.50, ("F", 4): 0.25, ("F", 5): 0.10, ("F", 6): 0.25,
    }

    # IMINT & GEOINT Space-Time Parameters
    GEOINT_PARAMETERS = {
        "firms_max_radius_km": 15.0,
        "firms_max_window_hours": 6.0,
        "sentinel2_nbr_burn_scar_threshold": 0.27,
        "sentinel2_ndvi_vegetation_drop_threshold": 0.20,
        "fuzzed_sector_grid_degrees": 0.1  # ~11 km bounding box for Void Pillar source OPSEC
    }

    def __init__(self):
        self.rules: Dict[str, ClassificationRule] = {
            "AIRSTRIKE": ClassificationRule(
                event_type="AIRSTRIKE",
                primary_keywords=["airstrike", "air raid", "bombing", "aerial attack", "air strike", "jet fighter", "dive-bombing"],
                secondary_keywords=["su-30", "yak-130", "mig-29", "k-8", "ftc-2000g", "mi-35", "dropped bombs", "strike package"],
                risk_weight=10.0,
                response_protocol="Immediate shelter warning. Pre-position medical teams. Monitor for secondary strikes."
            ),
            "CHEMICAL_THERMOBARIC_ATTACK": ClassificationRule(
                event_type="CHEMICAL_THERMOBARIC_ATTACK",
                primary_keywords=["thermobaric", "fuel-air explosive", "vacuum bomb", "odab", "chemical weapon", "asphyxiation"],
                secondary_keywords=["lung collapse", "massive overpressure", "white smoke", "toxic gas", "odab-500"],
                risk_weight=10.0,
                response_protocol="CRITICAL: Evacuate surface structures to deep underground bunkers. Seal air vents. Immediate trauma stabilization."
            ),
            "ARTILLERY_SHELLING": ClassificationRule(
                event_type="ARTILLERY_SHELLING",
                primary_keywords=["artillery", "shelling", "mortar", "howitzer", "heavy weapons", "bombardment", "shelled"],
                secondary_keywords=["122mm", "155mm", "d-30", "mam-01", "shrapnel", "crater"],
                risk_weight=8.5,
                response_protocol="Reinforce overhead cover. Maintain acoustic perimeter monitoring. Prepare casualty transport corridors."
            ),
            "DRONE_WARFARE": ClassificationRule(
                event_type="DRONE_WARFARE",
                primary_keywords=["fpv drone", "kamikaze drone", "hexacopter", "drone strike", "drone drop bomb"],
                secondary_keywords=["ch-4", "rainbow uav", "quadcopter", "jamming backpack", "servo drop"],
                risk_weight=8.0,
                response_protocol="Deploy RF frequency scanning and directional jammers. Scatter outdoor personnel. Move under dense canopy."
            ),
            "GROUND_CONFLICT": ClassificationRule(
                event_type="GROUND_CONFLICT",
                primary_keywords=["ground fighting", "clashes", "military operation", "firefight", "skirmish", "infantry assault"],
                secondary_keywords=["infantry", "tanks", "armored column", "ambush", "military column", "junta soldiers"],
                risk_weight=7.0,
                response_protocol="Establish civilian evacuation corridors. Stage medical aid outside kinetic zones. Track displaced populations."
            ),
            "DISPLACEMENT": ClassificationRule(
                event_type="DISPLACEMENT",
                primary_keywords=["displaced", "refugees", "evacuation", "fled", "migration", "idp", "fleeing"],
                secondary_keywords=["camp bombarded", "border crossing", "villagers fled", "temporary shelter", "forest hideout"],
                risk_weight=5.0,
                response_protocol="Set up aid distribution points. Deploy mobile water purification. Register arrivals under zero-trace privacy."
            ),
            "HUMANITARIAN_CRISIS": ClassificationRule(
                event_type="HUMANITARIAN_CRISIS",
                primary_keywords=["famine", "starvation", "medical shortage", "aid blocked", "siege", "humanitarian blockade"],
                secondary_keywords=["food insecurity", "water shortage", "cholera", "malnutrition", "medicines depleted"],
                risk_weight=8.0,
                response_protocol="Negotiate cross-border emergency humanitarian corridors. Coordinate localized solar-powered cold chains."
            ),
            "INFRASTRUCTURE_ATTACK": ClassificationRule(
                event_type="INFRASTRUCTURE_ATTACK",
                primary_keywords=["hospital hit", "school bombed", "power grid", "water supply", "monastery bombed", "church shelled"],
                secondary_keywords=["telecom tower", "central market", "bridge blown", "civilian infrastructure", "clinic destroyed"],
                risk_weight=9.0,
                response_protocol="Document damage hashes on Merkle ledger for international evidentiary reporting. Reroute essential power and comms."
            ),
            "NAVAL_SHELLING": ClassificationRule(
                event_type="NAVAL_SHELLING",
                primary_keywords=["naval shelling", "gunboat", "coastal bombardment", "naval vessel", "frigate firing"],
                secondary_keywords=["river gunboat", "76mm naval gun", "offshore bombardment", "landing craft"],
                risk_weight=7.5,
                response_protocol="Evacuate coastal and riverbank settlements inland beyond naval direct-fire range (>12 km)."
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
                matches.append((event_type, round(confidence, 2)))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def get_response_protocol(self, event_type: str) -> Optional[str]:
        rule = self.rules.get(event_type)
        return rule.response_protocol if rule else None
    
    def get_risk_weight(self, event_type: str) -> float:
        rule = self.rules.get(event_type)
        return rule.risk_weight if rule else 1.0

    def evaluate_admiralty(
        self,
        reliability: str = "C",
        credibility: int = 3,
        corroborating_evidence: Optional[List[Dict[str, Any]]] = None,
        contradiction_evidence: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        NATO 6x6 Admiralty Intelligence Rating System:
        Evaluates source reliability (A-F) and information credibility (1-6).
        Elevates score with multi-INT corroborations (GEOINT, SIGINT, Acoustic, SOCMINT).
        """
        rel_clean = str(reliability).upper()[:1]
        if rel_clean not in ("A", "B", "C", "D", "E", "F"):
            rel_clean = "C"
        cred_clean = int(credibility) if 1 <= int(credibility) <= 6 else 3

        initial_grade = f"{rel_clean}{cred_clean}"
        base_confidence = self.BASE_ADMIRALTY_TABLE.get((rel_clean, cred_clean), 0.65)

        corroborations = corroborating_evidence or []
        contradictions = contradiction_evidence or []

        bonus = 0.0
        modalities = []
        for item in corroborations:
            modality = item.get("modality", "UNKNOWN")
            modalities.append(modality)
            if modality == "GEOINT_THERMAL":
                bonus += 0.18
            elif modality == "SIGINT_FLIGHT":
                bonus += 0.14
            elif modality == "ACOUSTIC_EDGE":
                bonus += 0.16
            elif modality == "INDEPENDENT_SOCMINT":
                bonus += 0.10
            else:
                bonus += 0.05

        penalty = len(contradictions) * 0.25
        elevated_conf = max(0.05, min(0.99, base_confidence + bonus - penalty))
        elevated_conf = round(elevated_conf, 2)

        elevated_rel = rel_clean
        elevated_cred = cred_clean

        if len(modalities) >= 2 and not contradictions:
            elevated_cred = 1
            if elevated_rel in ("B", "C", "F"):
                elevated_rel = "A" if "GEOINT_THERMAL" in modalities or "ACOUSTIC_EDGE" in modalities else "B"
        elif len(modalities) == 1 and not contradictions:
            if elevated_cred > 2:
                elevated_cred = 2

        if contradictions:
            elevated_cred = max(elevated_cred, 4)

        elevated_grade = f"{elevated_rel}{elevated_cred}"
        actionable = (elevated_conf >= 0.70) and (elevated_cred <= 3) and (not contradictions)

        return {
            "initial_grade": initial_grade,
            "elevated_grade": elevated_grade,
            "initial_confidence": base_confidence,
            "elevated_confidence": elevated_conf,
            "corroboration_count": len(corroborations),
            "modalities": modalities,
            "contradictions": contradictions,
            "actionable_for_civilian_protection": actionable
        }

    def extract_tactical_entities(self, text: str) -> Dict[str, Any]:
        """Extracts tactical entities for cross-referencing with other domains."""
        text_lower = text.lower()
        
        aircraft_map = {
            "SU_30SME": ["su-30", "su30", "flanker"],
            "YAK_130": ["yak-130", "yak130", "mitten"],
            "MIG_29": ["mig-29", "mig29", "fulcrum"],
            "K_8": ["k-8", "k8", "karakorum"],
            "MI_35P": ["mi-35", "mi35", "hind"],
            "FTC_2000G": ["ftc-2000g", "ftc2000g", "mountain eagle"],
            "Y_12": ["y-12", "y12", "transport bomber"]
        }
        
        ordnance_map = {
            "THERMOBARIC_ODAB": ["thermobaric", "fuel-air explosive", "odab", "vacuum bomb"],
            "FAB_500": ["fab-500", "fab500", "500kg bomb", "500 kg bomb"],
            "CLUSTER_MUNITION": ["cluster bomb", "cluster munition", "submunition", "bomblet"],
            "ARTILLERY_122MM": ["122mm", "d-30", "d30", "howitzer"]
        }
        
        factions_map = {
            "AA": ["arakan army", " aa ", "ula/aa"],
            "MNDAA": ["mndaa", "kokang army", "myanmar national democratic alliance"],
            "TNLA": ["tnla", "ta'ang", "palaung"],
            "KNU_KNLA": ["knu", "knla", "karen national union"],
            "KIA": ["kia", "kio", "kachin independence army"],
            "KNDF": ["kndf", "karenni nationalities defense force"],
            "PDF": ["pdf", "peoples defense force", "people's defense force"]
        }
        
        found_ac = [ac for ac, kws in aircraft_map.items() if any(kw in text_lower for kw in kws)]
        found_ord = [ord_id for ord_id, kws in ordnance_map.items() if any(kw in text_lower for kw in kws)]
        found_factions = [f for f, kws in factions_map.items() if any(kw in text_lower for kw in kws)]
        
        return {
            "aircraft": found_ac,
            "ordnance": found_ord,
            "factions": found_factions
        }

    def detect_contradictions(self, text: str) -> List[str]:
        """Flags contradictory assertions in raw OSINT reports."""
        text_lower = text.lower()
        contradictions = []
        has_destruction = any(kw in text_lower for kw in ["airstrike", "bombing", "destroyed", "massacre", "heavy casualties"])
        has_peaceful = any(kw in text_lower for kw in ["no damage", "no casualties", "routine patrol without incident", "completely peaceful"])
        if has_destruction and has_peaceful:
            contradictions.append("MUTUALLY_EXCLUSIVE_IMPACT_CLAIMS")
        return contradictions


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
# 4.5. MYANMAR EAO CONFLICT DYNAMICS (2023-2025) - 10X EXPANDED
# ============================================================

@dataclass
class EAOOperation:
    op_id: str
    name: str
    theater: str
    state_region: str
    timeframe: str
    primary_forces: str
    actors: List[str]
    opposing_force: str
    key_milestones: List[str]
    strategic_impact: str
    tactical_innovations: List[str]
    captured_installations: List[str]
    civilian_risk_profile: str
    risk_level: str


@dataclass
class EAOFaction:
    faction_id: str
    name: str
    full_name: str
    primary_state: str
    headquarters: str
    estimated_strength: str
    command_structure: str
    governance_body: str
    alliance: str
    foreign_relations: str
    tactical_posture: str
    primary_weaponry: List[str]
    controlled_townships: List[str]


@dataclass
class TheaterAnalytics:
    theater_id: str
    name: str
    geographical_scope: str
    dominant_actors: List[str]
    eao_territory_pct: float
    junta_garrisons_status: str
    key_border_gates: List[str]
    strategic_infrastructure: List[str]
    humanitarian_crisis_level: str


class RelationshipType(Enum):
    STRATEGIC_ALLIANCE = "STRATEGIC_ALLIANCE"          # Sworn military alliance (e.g. 3BA)
    COALITION_PARTNER = "COALITION_PARTNER"            # Broad consultative coalition (e.g. FPNCC)
    ARMS_SUPPLIER_RECIPIENT = "ARMS_SUPPLIER_RECIPIENT"# Weapons/ordnance pipeline (e.g. UWSA -> 3BA/KIA)
    TACTICAL_COOPERATION = "TACTICAL_COOPERATION"      # Joint battlefield actions (e.g. KNDF + KNU 5th Brigade)
    NON_AGGRESSION_PACT = "NON_AGGRESSION_PACT"        # Demarcated non-aggression (e.g. SSPP & SAC, UWSA & SAC)
    ARMED_NEUTRALITY = "ARMED_NEUTRALITY"              # Armed neutral buffer (e.g. UWSA, DKBA)
    TERRITORIAL_FRICTION = "TERRITORIAL_FRICTION"      # Overlapping border disputes (e.g. TNLA vs SSPP)
    HISTORICAL_RIVALRY = "HISTORICAL_RIVALRY"          # Longstanding ethnic rivalry (e.g. SSPP vs RCSS)
    PROXY_ANTAGONIST = "PROXY_ANTAGONIST"              # Junta-armed proxy conflict (e.g. PNLA vs PNA, AA vs ARSA)
    ACTIVE_HOSTILITY = "ACTIVE_HOSTILITY"              # Active armed conflict (e.g. EAOs vs SAC)


@dataclass
class FactionRelationship:
    source_faction: str
    target_faction: str
    rel_type: str
    affinity_score: float  # -1.0 (hostile) to +1.0 (allied)
    coalition: Optional[str]
    historical_context: str
    joint_operations: List[str]
    friction_points: List[str]
    arms_flow: str


class MyanmarEAO2023_2025Context:
    def __init__(self):
        # 1. EXPANDED FACTIONS (28 Factions across all States/Divisions)
        self.factions: Dict[str, EAOFaction] = {
            # --- SHAN STATE THEATER ---
            "MNDAA": EAOFaction(
                faction_id="MNDAA",
                name="Myanmar National Democratic Alliance Army",
                full_name="Myanmar National Truth and Justice Party / MNDAA (Kokang Special Region 1)",
                primary_state="Northern Shan State",
                headquarters="Laukkai / Chinshwehaw",
                estimated_strength="8,000 - 10,000 combatants",
                command_structure="Peng Deren (Commander-in-Chief); Kokang Military Commission",
                governance_body="Kokang Special Region Administrative Committee",
                alliance="Three Brotherhood Alliance (3BA); Federal Political Negotiation and Consultative Committee (FPNCC)",
                foreign_relations="Extensive cultural, linguistic, and border ties with Yunnan, China; subject to Chinese cross-border border pressure.",
                tactical_posture="Offensive shock-doctrine; urban siege mastery; captured Laukkai (Jan 2024) and Lashio RMC (Aug 2024).",
                primary_weaponry=["Type 56/81 Assault Rifles", "107mm Type 63 Rocket Launchers", "Commercial Heavy Drop Hexacopters", "WMA-301 Tank Destroyers (Captured)", "BTR-3U APCs (Captured)"],
                controlled_townships=["Laukkai", "Chinshwehaw", "Konkyan", "Hsenwi", "Kunlong", "Kutkai", "Lashio (Shared/Contested Admin)"]
            ),
            "TNLA": EAOFaction(
                faction_id="TNLA",
                name="Ta'ang National Liberation Army",
                full_name="Palaung State Liberation Front / TNLA",
                primary_state="Northern Shan State & Mandalay Border",
                headquarters="Namhsan / Kyaukme",
                estimated_strength="10,000 - 14,000 combatants",
                command_structure="Lt. Gen. Tar Aik Bong (President), Maj. Gen. Tar Bone Kyaw (General Secretary)",
                governance_body="PSLF Central Administrative Committee (Civilian District Councils)",
                alliance="Three Brotherhood Alliance (3BA); FPNCC",
                foreign_relations="China border liaison; trade regulation along Ruili-Muse-Mandalay corridor.",
                tactical_posture="Mountain-jungle infiltration leading to fortified town cordons; strict anti-narcotics enforcement.",
                primary_weaponry=["Type 81/M16 rifles", "RPG-7", "60mm/82mm Mortars", "UAV FPV Kamikaze Drones", "12.7mm DShK Anti-Aircraft Guns"],
                controlled_townships=["Namhsan", "Mantong", "Namkham", "Mongngaw", "Kyaukme", "Nawnghkio", "Mongmit", "Mogok (Ruby Belt)"]
            ),
            "UWSA": EAOFaction(
                faction_id="UWSA",
                name="United Wa State Army",
                full_name="United Wa State Party / UWSA (Special Region 2)",
                primary_state="Shan State (Wa Self-Administered Division & Southern Wa)",
                headquarters="Panghsang (Pangkham) / Mong Yawn",
                estimated_strength="30,000 - 35,000 regular personnel (Heaviest armed non-state military in Asia)",
                command_structure="Bao Youxiang (Supreme Commander); Politburo & Military Affairs Commission",
                governance_body="Wa State People's Government (Independent ministries, courts, currency, schools)",
                alliance="FPNCC Chair & Leading Hegemon",
                foreign_relations="Direct strategic interface with Beijing; Yunnan border infrastructure links; acts as diplomatic and military buffer.",
                tactical_posture="Armed neutrality; defensive deterrence; primary arms supplier and ammunition fabricator for allied EAOs.",
                primary_weaponry=["Type 96 MBTs", "ZFB-05 Armored Vehicles", "HN-5 / FN-6 MANPADS", "122mm Howitzers", "Heavy MLRS Systems", "Indigenous Assault Rifles (Type 09)"],
                controlled_townships=["Panghsang", "Mongmao", "Pangwaun", "Hopang (Transferred Jan 2024)", "Panlong", "Mong Yawn command along Thai border"]
            ),
            "SSPP": EAOFaction(
                faction_id="SSPP",
                name="Shan State Progress Party",
                full_name="Shan State Progress Party / Shan State Army-North (SSPP/SSA-N)",
                primary_state="Northern & Central Shan State",
                headquarters="Wan Hai (Kehsi Township)",
                estimated_strength="8,000 - 10,000 active troops",
                command_structure="Lt. Gen. Pang Fa (Patron), Sao Khun Hseng (Vice-Chairman)",
                governance_body="SSPP Administrative Council",
                alliance="FPNCC; non-aggression coordination with UWSA and 3BA",
                foreign_relations="Maintains multi-channel dialogues with China and transactional truces with SAC central regime.",
                tactical_posture="Territorial protection and border trade regulation; combatting cross-border telecom scam syndicates; contested zones with RCSS.",
                primary_weaponry=["Type 81", "AK-47", "Mortars", "Light Anti-Air Systems"],
                controlled_townships=["Wan Hai sector", "Monghsu corridors", "Kyethi", "Tangyan perimeter"]
            ),
            "RCSS": EAOFaction(
                faction_id="RCSS",
                name="Restoration Council of Shan State",
                full_name="Restoration Council of Shan State / Shan State Army-South (RCSS/SSA-S)",
                primary_state="Southern Shan State",
                headquarters="Loi Tai Leng (Fortified mountain base on Thai border)",
                estimated_strength="8,000 - 10,000 troops",
                command_structure="Gen. Yawd Serk (Chairman)",
                governance_body="RCSS Central Committee",
                alliance="Signatory to 2015 Nationwide Ceasefire Agreement (NCA); historic rival of SSPP and TNLA",
                foreign_relations="Cross-border ties with Northern Thailand; dialogue with Naypyidaw consultative councils.",
                tactical_posture="Consolidation of Southern Shan redoubts; withdrawal from Northern Shan following 2022 clashes.",
                primary_weaponry=["M16A2", "M4 Carbines", "Type 56", "M79 Grenade Launchers", "Heavy Mortars"],
                controlled_townships=["Loi Tai Leng corridor", "Mongton", "Monghsat", "Mawkmai frontier sectors"]
            ),
            "DPLA": EAOFaction(
                faction_id="DPLA",
                name="Danu People's Liberation Army",
                full_name="Danu People's Liberation Front / Danu People's Liberation Army",
                primary_state="Southern Shan & Mandalay borderland",
                headquarters="Danu Self-Administered Zone outskirts",
                estimated_strength="1,500 - 2,500 fighters",
                command_structure="Danu Revolutionary Command",
                governance_body="DPLF Civilian Council",
                alliance="Allied with TNLA and MDY-PDF during Operation 1027 Phase 2",
                foreign_relations="Local ethnic solidarity network.",
                tactical_posture="Active guerrilla assaults along Nawnghkio-Ywangan mountain axis.",
                primary_weaponry=["Automatic rifles", "Modified drone mortars", "Anti-materiel rifles"],
                controlled_townships=["Rural Ywangan", "Pindaya mountain corridors"]
            ),

            # --- KACHIN & SAGAING BORDER THEATER ---
            "KIA": EAOFaction(
                faction_id="KIA",
                name="Kachin Independence Army",
                full_name="Kachin Independence Organization / KIA",
                primary_state="Kachin State, Northern Shan & Upper Sagaing",
                headquarters="Laiza (China border redoubt)",
                estimated_strength="18,000 - 25,000 regular troops (Brigades 1 to 10 + 2 Mobile Brigades)",
                command_structure="Gen. N'Ban La (Chairman), Lt. Gen. Stephen Gun Maw (Vice Chairman), Lt. Gen. Rawng San (C-in-C)",
                governance_body="KIO Central Committee (Health, Education, Mining, Justice Departments)",
                alliance="K7 Revolutionary Alliance; principal strategic trainer, ordnance supplier, and joint-op coordinator for Northern PDFs",
                foreign_relations="Direct border negotiations with Yunnan authorities; critical supplier of rare-earths to global markets.",
                tactical_posture="Operation 0307 offensive; heavy artillery interdiction; air-defense ambush tactics; liberated rare-earth and jade mining hubs.",
                primary_weaponry=["Indigenous K-09 / K-10 rifles", "Type 81", "120mm Heavy Mortars", "FN-6 MANPADS", "Captured 122mm D-30 Howitzers", "Heavy FPV Attack Drones"],
                controlled_townships=["Laiza", "Mai Ja Yang", "Lweje", "Sumprabum", "Injangyang", "Momauk outskirts", "Mansi", "Sadung", "Pangwa (Chipwi)", "Hpakant jade basin"]
            ),
            "NDA_K_BGF": EAOFaction(
                faction_id="NDA_K_BGF",
                name="New Democratic Army - Kachin (Border Guard Forces 1001-1003)",
                full_name="NDA-K BGF (Zahkung Ting Ying pro-SAC warlord network)",
                primary_state="Special Region 1, Kachin State",
                headquarters="Pangwa / Chipwi",
                estimated_strength="1,500 - 2,500 militia personnel (Overrun by KIA in late 2024)",
                command_structure="Zahkung Ting Ying (Warlord founder); SAC Directorate of People's Militias",
                governance_body="Pro-regime border administration",
                alliance="Direct auxiliary militia of SAC Myanmar Military",
                foreign_relations="Controlled illicit heavy rare-earth transit routes into Yunnan until KIA defeat.",
                tactical_posture="Defensive border policing; routed by KIA Operation 0307/1018 in September-October 2024.",
                primary_weaponry=["MA-1 / MA-2 rifles", "Type 56", "Light artillery"],
                controlled_townships=["Pangwa (Lost Oct 2024)", "Chipwi (Lost Sep 2024)", "Hsawlaw (Lost Oct 2024)"]
            ),
            "SNA": EAOFaction(
                faction_id="SNA",
                name="Shanni Nationalities Army",
                full_name="Tai-Leng Nationalities Development Party / SNA",
                primary_state="Kachin-Sagaing borderland (Homalin, Mohnyin)",
                headquarters="Homalin rural sector",
                estimated_strength="3,000 - 5,000 personnel",
                command_structure="Gen. Saw Htun",
                governance_body="Shanni Ethnic Council",
                alliance="Complex local non-aggression; periodic clashes with KIA and local PDFs over territorial control",
                foreign_relations="Independent regional focus.",
                tactical_posture="Guarding Shanni ethnic populated corridors; controlling gold and timber transit routes.",
                primary_weaponry=["Type 81", "M16", "RPG-7", "Light mortars"],
                controlled_townships=["Rural Homalin", "Mohnyin frontier", "Katha river sectors"]
            ),

            # --- RAKHINE & WESTERN FRONTIER ---
            "AA": EAOFaction(
                faction_id="AA",
                name="Arakan Army",
                full_name="United League of Arakan / Arakan Army (ULA/AA)",
                primary_state="Rakhine State & Paletwa (Chin State)",
                headquarters="Mrauk-U (Administrative) / Mobile Command Center",
                estimated_strength="38,000 - 45,000 active combatants (Highly disciplined light infantry)",
                command_structure="Maj. Gen. Twan Mrat Naing (Commander-in-Chief), Brig. Gen. Nyo Twan Awng (Vice C-in-C)",
                governance_body="Arakan People's Revolutionary Government (Complete taxation, police, judiciary, civil administration)",
                alliance="Three Brotherhood Alliance (3BA); FPNCC; informal tactical liaison with NUG",
                foreign_relations="Direct strategic diplomacy with China (protecting Kyaukphyu SEZ/pipelines) and India (Kaladan Multi-Modal Project); border relations with Bangladesh.",
                tactical_posture="Total theater dominance; overran 14 of 17 Rakhine townships; coastal amphibious operations; siege of Western Command.",
                primary_weaponry=["Type 81", "QBZ-97", "Type 85 HMG", "120mm Heavy Mortars", "122mm Howitzers (Captured)", "Armed Reconnaissance Drones", "Fast Attack Riverine Boats"],
                controlled_townships=["Paletwa", "Kyauktaw", "Mrauk-U", "Minbya", "Ponnagyun", "Rathedaung", "Buthidaung", "Maungdaw", "Myebon", "Pauktaw", "Ramree", "Thandwe", "Taungup", "Gwa", "Kyeintali"]
            ),
            "CNF_CNA": EAOFaction(
                faction_id="CNF_CNA",
                name="Chin National Front / Chin National Army",
                full_name="Chin National Front / CNA (Chinland Council)",
                primary_state="Chin State",
                headquarters="Camp Victoria (Thantlang Township on India border)",
                estimated_strength="4,000 - 6,000 regular troops",
                command_structure="Pu Zing Cung (President), Maj. Gen. Lian Bawi (C-in-C)",
                governance_body="Chinland Council / Government of Chinland",
                alliance="K7 Alliance; core NUG partner; allied with Chinland Defense Forces (CDF)",
                foreign_relations="Deep ethnic and refugee links with Mizoram State, India; cross-border humanitarian conduit.",
                tactical_posture="High-altitude mountain warfare; overran border garrisons (Rihkhawdar, Thantlang); besieged Hakha.",
                primary_weaponry=["M16A4", "M4 Carbines", "Sniper Systems", "RPG-7", "Commercial Drop Drones"],
                controlled_townships=["Thantlang", "Rihkhawdar border gate", "Camp Victoria sector", "Rural Hakha & Falam"]
            ),
            "CHIN_BROTHERHOOD": EAOFaction(
                faction_id="CHIN_BROTHERHOOD",
                name="Chin Brotherhood Alliance",
                full_name="Chin Brotherhood (CDF-Mindat, CDF-Kanpetlet, CDF-Matupi, Maraland, ZFU)",
                primary_state="Southern and Central Chin State",
                headquarters="Mindat / Matupi",
                estimated_strength="4,000 - 5,000 combatants",
                command_structure="Joint Military Committee (CB)",
                governance_body="Local Township Councils",
                alliance="Allied closely with Arakan Army (AA) and Yaw Defense Force; rival to Chinland Council over administrative authority",
                foreign_relations="Mizoram border connectivity.",
                tactical_posture="Captured Matupi, Kyindwe, Mindat perimeter with direct AA artillery and close coordination.",
                primary_weaponry=["M16", "Bolt-action hunting rifles", "Mortar drop drones", "Captured junta arms"],
                controlled_townships=["Mindat rural corridor", "Matupi", "Kanpetlet", "Kyindwe enclave"]
            ),

            # --- KARENNI (KAYAH) THEATER ---
            "KNDF": EAOFaction(
                faction_id="KNDF",
                name="Karenni Nationalities Defence Force",
                full_name="Karenni Nationalities Defence Force (22+ Battalions, 7 Strategic Brigades)",
                primary_state="Kayah (Karenni) State, Southern Shan & Naypyidaw Border",
                headquarters="Demoso / Loikaw Mobile HQ",
                estimated_strength="10,000 - 14,000 combatants (One of the most battle-hardened post-coup forces)",
                command_structure="Khun Bedu (Chairman), Marwi (Commander-in-Chief)",
                governance_body="Karenni State Interim Executive Council (IEC)",
                alliance="K7 Alliance; strategic partner to KNPP, KNU, and KIA; leading partner to Central PDFs",
                foreign_relations="Cross-border Mae Hong Son (Thailand) humanitarian link.",
                tactical_posture="Pioneers of decentralized mesh drone strikes, urban combat (Operation 1111), and combined-arms ambushes.",
                primary_weaponry=["M16 / M4", "Type 81", "Indigenous Falcon Drone Drop Systems", "60mm/81mm Mortars", "RPG-7", "Captured 120mm Mortars"],
                controlled_townships=["Demoso", "Bawlake", "Shadaw", "Mese border gate", "Hpasawng", "70%+ of Loikaw perimeter", "Mawchi mineral belt"]
            ),
            "KNPP_KA": EAOFaction(
                faction_id="KNPP_KA",
                name="Karenni Army / KNPP",
                full_name="Karenni National Progressive Party / Karenni Army (KA)",
                primary_state="Kayah (Karenni) State",
                headquarters="Nyamo (Thai border)",
                estimated_strength="2,500 - 3,500 regular troops",
                command_structure="Khu Oo Reh (Chairman), Gen. Bee Htoo (C-in-C)",
                governance_body="KNPP Central Committee / IEC Cabinet",
                alliance="Historic leadership of Karenni revolution; K7 Alliance; mentor force to KNDF",
                foreign_relations="Thai border diplomacy.",
                tactical_posture="Deep jungle tracking; cross-border logistics protection; artillery support for KNDF.",
                primary_weaponry=["M16", "HK33", "Type 56", "M79", "Light air-defense weapons"],
                controlled_townships=["Southern Karenni borderlands", "Salween River corridor"]
            ),
            "KNPLF": EAOFaction(
                faction_id="KNPLF",
                name="Karenni National People's Liberation Front",
                full_name="KNPLF (Former BGF 1004 & 1005 - Defected June 2023)",
                primary_state="Kayah State & Southern Shan",
                headquarters="Phaung Taw",
                estimated_strength="1,500 - 2,000 fighters",
                command_structure="Tun Kyaw (Patron)",
                governance_body="KNPLF Executive Council",
                alliance="Joined anti-SAC revolutionary coalition in June 2023; operates with KNDF and KA",
                foreign_relations="Regional ethnic trade.",
                tactical_posture="Turned their weapons against SAC outposts in June 2023; liberated eastern Salween sectors.",
                primary_weaponry=["MA-series rifles", "Type 81", "Heavy machine guns"],
                controlled_townships=["Mese", "Eastern Salween River basin"]
            ),

            # --- PA-O & SOUTHERN SHAN ---
            "PNLA": EAOFaction(
                faction_id="PNLA",
                name="Pa-O National Liberation Army",
                full_name="Pa-O National Liberation Organization / PNLA",
                primary_state="Southern Shan & Karenni border",
                headquarters="Hsihseng / Mawkmai border",
                estimated_strength="2,500 - 3,500 combatants",
                command_structure="Col. Khun Okker (Adviser), Khun Thurein (Chairman)",
                governance_body="PNLO Executive Committee",
                alliance="Broke 2015 NCA in January 2024 to join the anti-junta revolution; allied with KNDF and Southern PDFs",
                foreign_relations="Southern Shan diaspora.",
                tactical_posture="Battle of Hsihseng (Jan-May 2024); direct clashes with SAC and PNA proxy militia.",
                primary_weaponry=["Type 81", "M16", "Drop drones", "Mortars"],
                controlled_townships=["Hsihseng perimeter", "Hopong hill tracts", "Mawkmai northern corridor"]
            ),
            "PNA": EAOFaction(
                faction_id="PNA",
                name="Pa-O National Army (PNA / PNO Militia)",
                full_name="Pa-O National Organization / PNA (Aung Kham Hti Militia)",
                primary_state="Pa-O Self-Administered Zone, Southern Shan",
                headquarters="Taunggyi / Hopong",
                estimated_strength="3,000 - 4,500 armed militia personnel",
                command_structure="Aung Kham Hti (Patron); SAC Eastern Command",
                governance_body="Pa-O SAZ Administration",
                alliance="Pro-SAC regime auxiliary militia",
                foreign_relations="Business and real estate ties in Taunggyi and Yangon.",
                tactical_posture="Armed by SAC in early 2024 to fight PNLA; enforces junta conscription in Pa-O villages.",
                primary_weaponry=["MA-1 / MA-2", "Type 56", "Light artillery provided by SAC Eastern Command"],
                controlled_townships=["Taunggyi perimeter", "Hopong town", "Pinlaung"]
            ),

            # --- KAYIN (KAREN), MON & TANINTHARYI ---
            "KNU_KNLA": EAOFaction(
                faction_id="KNU_KNLA",
                name="Karen National Liberation Army",
                full_name="Karen National Union / KNLA (Brigades 1 to 7)",
                primary_state="Kayin (Karen) State, Mon, Bago & Tanintharyi",
                headquarters="Mu Traw (Brigade 5) / Dooplaya (Brigade 6)",
                estimated_strength="20,000 - 25,000 active troops",
                command_structure="Padoh Saw Kwe Htoo Win (President), Gen. Saw Johnny (C-in-C)",
                governance_body="Kawthoolei Central Government (7 Administrative Districts)",
                alliance="K7 Alliance; core NUG partner; joint operations with BPLA, Cobra Column, Federal Wings",
                foreign_relations="Longstanding border relations with Thailand along Tak and Mae Sot; international humanitarian interface.",
                tactical_posture="Interdiction of Asian Highway 1; siege of Myawaddy; ambushing reinforcements along Dawna Range.",
                primary_weaponry=["M16A1/A2/A4", "M4A1", "Steyr AUG", "RPG-7", "Heavy Drop Drones (Federal Wings)", "120mm Mortars"],
                controlled_townships=["Hpapun (Mu Traw)", "Myawaddy rural corridors", "Kawkareik hill tracts", "Kyaukkyi (Nyaunglebin)", "Thaton hinterland"]
            ),
            "KNDO": EAOFaction(
                faction_id="KNDO",
                name="Karen National Defence Organisation",
                full_name="Karen National Defence Organisation (KNU Village & Territorial Guard)",
                primary_state="Kayin State",
                headquarters="Kawthoolei sector",
                estimated_strength="4,000 - 6,000 personnel",
                command_structure="Saw Shee Lay (C-in-C)",
                governance_body="KNU Central Defense Department",
                alliance="Direct armed branch of KNU alongside KNLA",
                foreign_relations="Thai border communities.",
                tactical_posture="Special forces commando operations (Venom Commando, Lion Battalion); front-line base assaults.",
                primary_weaponry=["M4 Carbines", "M16", "Custom sniper rifles", "Anti-materiel rifles"],
                controlled_townships=["Waw Ray district", "Dooplaya frontline"]
            ),
            "KNA_BGF": EAOFaction(
                faction_id="KNA_BGF",
                name="Karen National Army (Saw Chit Thu BGF)",
                full_name="Karen Border Guard Force / Rebranded Karen National Army (KNA)",
                primary_state="Kayin State (Myawaddy / Shwe Kokko)",
                headquarters="Shwe Kokko / Myaing Gyi Ngu",
                estimated_strength="7,000 - 9,000 armed combatants",
                command_structure="Col. Saw Chit Thu (General Secretary), Maj. Saw Tin Win",
                governance_body="KNA Military Command",
                alliance="Split from SAC command in January 2024; declared neutrality to protect casino enclaves from conflict",
                foreign_relations="Direct control of massive telecom fraud and casino developments (KK Park, Shwe Kokko) with Chinese transnational criminal syndicates.",
                tactical_posture="Pragmatic armed neutrality; refused to fight KNU on behalf of SAC during Myawaddy siege in April 2024.",
                primary_weaponry=["MA-series rifles", "Type 81", "Armored SUVs", "Heavy Machine Guns"],
                controlled_townships=["Shwe Kokko special zone", "Myawaddy northern peri-urban belt", "Myaing Gyi Ngu"]
            ),
            "DKBA": EAOFaction(
                faction_id="DKBA",
                name="Democratic Karen Benevolent Army",
                full_name="Democratic Karen Benevolent Army (Kloh Htoo Baw)",
                primary_state="Kayin State",
                headquarters="Sone See Myaing",
                estimated_strength="2,000 - 3,000 combatants",
                command_structure="Gen. Saw Steel (C-in-C)",
                governance_body="DKBA Supreme Council",
                alliance="Signatory to 2015 NCA; maintains neutral buffer stance while granting transit to anti-junta fighters",
                foreign_relations="Thai border trade.",
                tactical_posture="Defensive local protection; mediating between KNU and junta forces in Myawaddy.",
                primary_weaponry=["M16", "Type 56", "Light mortars"],
                controlled_townships=["Walley corridor", "Sone See Myaing cantonment"]
            ),
            "RMA": EAOFaction(
                faction_id="RMA",
                name="Ramonnya Mon Army",
                full_name="Ramonnya Mon Army (Unified NMSP-AD + MLA + MLF)",
                primary_state="Mon State & Tanintharyi Region",
                headquarters="Ye / Mawlamyine hinterland",
                estimated_strength="3,500 - 4,500 combatants",
                command_structure="Nai Zeya (General Secretary), Nai Hongsar Jr. (Military Command)",
                governance_body="Mon State Revolutionary Council",
                alliance="Allied with KNU 4th Brigade and Southern PDFs; part of Steering Council for Federal Democratic Union (SCEF)",
                foreign_relations="Mon diaspora networks in Thailand and Western nations.",
                tactical_posture="Formed in May 2025 by unifying Mon splinter armies; guerrilla interdiction along Mawlamyine-Ye-Dawei highway.",
                primary_weaponry=["M16", "Type 81", "RPG-7", "Drone drop munitions"],
                controlled_townships=["Rural Ye", "Thanbyuzayat corridors", "Yebyu borderlands"]
            ),
            "NMSP": EAOFaction(
                faction_id="NMSP",
                name="New Mon State Party (Traditional Faction)",
                full_name="New Mon State Party (Ceasefire Faction)",
                primary_state="Southern Mon State",
                headquarters="Ye Chaung Phya",
                estimated_strength="1,500 - 2,000 personnel",
                command_structure="Nai Han Thar (Chairman)",
                governance_body="NMSP Executive Committee",
                alliance="Maintains adherence to 2015 NCA framework; suffered major split when NMSP-AD defected in Feb 2024",
                foreign_relations="Border trade with Kanchanaburi, Thailand.",
                tactical_posture="Passive ceasefire posture; participating in periodic regime consultations.",
                primary_weaponry=["M16", "HK33", "Light support weapons"],
                controlled_townships=["Ye Chaung Phya cantonment"]
            ),

            # --- CENTRAL REVOLUTIONARY FORCES & BAMAR ALLIANCES ---
            "MDY_PDF": EAOFaction(
                faction_id="MDY_PDF",
                name="Mandalay People's Defence Force",
                full_name="Mandalay PDF (NUG Central Military Region Command)",
                primary_state="Mandalay Region & Northern Shan Border",
                headquarters="Singu / Thabeikkyin liberated sectors",
                estimated_strength="5,000 - 7,000 regular troops",
                command_structure="Mon Tway (Commander), Soe Thuya Zaw (Operations Commander)",
                governance_body="NUG Ministry of Defence",
                alliance="Core vanguard force of NUG; fought as embedded frontline strike force in Operation 1027 Phase 1 & 2 with TNLA/MNDAA",
                foreign_relations="NUG diplomatic missions.",
                tactical_posture="Operation Kanaung; liberated Singu, Thabeikkyin, Mogok (co-administered with TNLA); advancing toward Mandalay city.",
                primary_weaponry=["Type 81", "M16", "Captured 120mm / 81mm Mortars", "Heavy Drone Strike Units", "Anti-Tank Guided Munitions"],
                controlled_townships=["Singu", "Thabeikkyin", "Natogyi corridors", "Shared governance in Mogok"]
            ),
            "BPLA": EAOFaction(
                faction_id="BPLA",
                name="Bamar People's Liberation Army",
                full_name="Bamar People's Liberation Army (Founded April 2021)",
                primary_state="Shan, Karenni, Kayin & Central Myanmar",
                headquarters="Mobile Operational Brigades",
                estimated_strength="3,000 - 4,500 combatants",
                command_structure="Maung Saungkha (Commander-in-Chief)",
                governance_body="BPLA Political Wing",
                alliance="Trained by KIO/KIA; fought alongside MNDAA/TNLA in Operation 1027 and KNDF in Karenni; bridge between Bamar youth and ethnic EAOs",
                foreign_relations="International civil society and diaspora solidarity.",
                tactical_posture="High-mobility strike units; spearhead assault battalions in Operation 1027 Phase 1.",
                primary_weaponry=["Type 81", "M16", "Captured MA-series rifles", "Specialized Drone Recon Units"],
                controlled_townships=["Co-operational presence in Northern Shan and Karenni"]
            ),
            "PLA_CPB": EAOFaction(
                faction_id="PLA_CPB",
                name="People's Liberation Army (CPB)",
                full_name="People's Liberation Army (Armed wing of Communist Party of Burma)",
                primary_state="Northern Shan & Upper Sagaing",
                headquarters="Northern Shan borderlands",
                estimated_strength="1,000 - 1,500 combatants",
                command_structure="CPB Central Military Commission",
                governance_body="Communist Party of Burma Central Committee",
                alliance="Allied with Three Brotherhood Alliance in Operation 1027",
                foreign_relations="Historical ideological ties.",
                tactical_posture="Guerrilla operations; tactical coordination with MNDAA.",
                primary_weaponry=["Type 81", "AK-47", "Mortars"],
                controlled_townships=["Northern Shan border pockets"]
            ),
            "NUG_PDF_CENTRAL": EAOFaction(
                faction_id="NUG_PDF_CENTRAL",
                name="People's Defence Force (Central & Anyar Divisions)",
                full_name="People's Defence Force (Sagaing, Magway, Bago & Tanintharyi Military Commands)",
                primary_state="Sagaing, Magway, Bago & Mandalay Regions",
                headquarters="Decentralized District Commands (Pa-Ah-Pha)",
                estimated_strength="60,000 - 80,000 active personnel nationwide (Battalions + Local PDFs)",
                command_structure="Yee Mon (NUG Defence Minister), Northern/Central/Southern Bureau Commanders",
                governance_body="National Unity Government (NUG) / Local People's Administration (Pa-Ah-Ya)",
                alliance="Strategic partnerships with KIA, KNU, KNDF, AA, and Chinland Council (K7 Framework)",
                foreign_relations="ASEAN, US, EU, and international multilateral representation.",
                tactical_posture="Asymmetric attrition; ambushes of regime riverine flotillas (Chindwin/Irrawaddy); rural administrative control over >60% of Sagaing/Magway.",
                primary_weaponry=["Modified hunting rifles", "Captured MA-1/2/3", "Locally machined 'Tumee' mortars", "Commercial UAV drone drop units", "IED ambush arrays"],
                controlled_townships=["Kawlin (Contested)", "Ayadaw", "Taze", "Yinmabin", "Pale", "Gangaw", "Pauk", "Myaing", "Yesagyo", "Katha hinterland"]
            )
        }

        # 2. EXPANDED OPERATIONS (16 Comprehensive 2023-2025 Operations)
        self.operations: Dict[str, EAOOperation] = {
            "OP_1027_PHASE1": EAOOperation(
                op_id="OP_1027_PHASE1",
                name="Operation 1027 (Phase 1)",
                theater="Northern Shan State",
                state_region="Shan State (North)",
                timeframe="2023-10-27 to 2024-01-11",
                primary_forces="Chaos -> Harmony (Three Brotherhood Alliance strategic blitz)",
                actors=["MNDAA", "TNLA", "AA", "MDY-PDF", "BPLA", "PLA"],
                opposing_force="SAC Northeast Regional Military Command (Lashio, Laukkai, Hsenwi garrisons)",
                key_milestones=[
                    "Oct 27, 2023: Dawn synchronized strikes on over 100 SAC bases across Northern Shan",
                    "Captured key China border gates: Chinshwehaw, Mongko, Kyukok-Pangsang, Hsenwi bridge",
                    "Dec 2023: Surrounded Kokang capital Laukkai; eliminated key casino fraud compounds",
                    "Jan 5, 2024: Complete surrender of Laukkai Regional Operations Command (2,389 military personnel, including 6 Brigadier Generals)",
                    "Jan 11, 2024: Haigeng Ceasefire negotiated in Kunming, China, temporarily freezing frontlines"
                ],
                strategic_impact="Overthrew 15 years of junta dominance in Kokang; shattered military morale; captured >400 military installations; severed $1.5B+ annual border trade route.",
                tactical_innovations=["Integrated commercial hexacopter drone swarm strikes (25,000+ drone bombs dropped)", "Simultaneous highway interdiction cutting all reinforcement columns"],
                captured_installations=["Laukkai Regional Command HQ", "Chinshwehaw Customs Gate", "Kunlong Suspension Bridge base", "Mongko Border Post"],
                civilian_risk_profile="Massive displacement across Kokang into Wa State; heavy junta retaliatory airstrikes on civilian markets.",
                risk_level="CRITICAL"
            ),
            "OP_1027_PHASE2": EAOOperation(
                op_id="OP_1027_PHASE2",
                name="Operation 1027 (Phase 2)",
                theater="Northern Shan & Mandalay Frontier",
                state_region="Northern Shan State & Mandalay Region",
                timeframe="2024-06-25 to 2024-08-15",
                primary_forces="Yang -> Chaos (Decisive urban decapitation offensive)",
                actors=["TNLA", "MNDAA", "MDY-PDF", "DPLA"],
                opposing_force="SAC Northeastern Regional Military Command (RMC Lashio) & Division 99",
                key_milestones=[
                    "Jun 25, 2024: Offensive resumed after junta repeatedly broke Haigeng truce with aerial bombings",
                    "Jul 2024: TNLA seized Nawnghkio, Kyaukme, Mongmit, and liberated Mogok ruby mines",
                    "Jul 2024: MNDAA breached Lashio perimeter defenses; intense urban close-quarters warfare",
                    "Aug 3, 2024: Overran Lashio Northeastern Regional Command HQ; captured Commander Maj. Gen. Soe Tint",
                    "Historic first: An active Regional Military Command headquarters fell to resistance forces"
                ],
                strategic_impact="Decapitated junta operational authority in northeastern Myanmar; prompted regime to declare conscription enforcement; prompted Beijing to impose economic border blockades on Kokang and Wa.",
                tactical_innovations=["Urban anti-drone jamming arrays", "Tunneling and precision mortar triangulation in built-up city sectors"],
                captured_installations=["Northeastern Regional Military Command (RMC) HQ (Lashio)", "Lashio Military Hospital", "Mogok Central Gem Mines", "Kyaukme Military Base"],
                civilian_risk_profile="Destruction of Lashio civilian sectors; hundreds of civilian airstrike casualties; emergency flight of 80,000+ residents.",
                risk_level="CRITICAL"
            ),
            "OP_1107_KARENNI": EAOOperation(
                op_id="OP_1107_KARENNI",
                name="Operation 1107 (Border Liberation)",
                theater="Eastern Frontier",
                state_region="Kayah (Karenni) State & Thai Border",
                timeframe="2023-11-07 to 2023-11-20",
                primary_forces="Yin -> Yang (Decisive border enclave clearing)",
                actors=["KNDF", "KA", "KNPLF"],
                opposing_force="SAC Border Battalions & Infantry Battalions 428/430",
                key_milestones=[
                    "Nov 7, 2023: Launched across southern Karenni borderlands",
                    "Overran fortified military camps along Thai frontier in Mese Township",
                    "Downed a SAC K-8W light attack jet near Loikaw (Nov 11, 2023)"
                ],
                strategic_impact="Secured the entire Thailand-Karenni border corridor; opened international supply lines.",
                tactical_innovations=["Shoulder-fired anti-aircraft MANPADS ambush against close-support aircraft"],
                captured_installations=["Mese Border Garrison", "Point 1107 Hilltop Base", "Phaung Taw Command"],
                civilian_risk_profile="Cross-border artillery shells landing in Thailand; evacuation of border villages.",
                risk_level="HIGH"
            ),
            "OP_1111_KARENNI": EAOOperation(
                op_id="OP_1111_KARENNI",
                name="Operation 1111 (Siege of Loikaw)",
                theater="Karenni Mountain & Urban Basin",
                state_region="Kayah (Karenni) State & Southern Shan",
                timeframe="2023-11-11 to 2025-10-01",
                primary_forces="Yin -> Harmony (Protracted urban resistance and civic governance)",
                actors=["KNDF", "KA", "KNPLF", "Southern PDFs"],
                opposing_force="SAC Regional Operations Command (ROC Loikaw) & 55th Light Infantry Division",
                key_milestones=[
                    "Nov 11, 2023: Multi-axis dawn assault on state capital Loikaw",
                    "Captured Loikaw University campus after intense 3-day battle; rescued trapped students",
                    "Captured Loikaw District Police HQ, Prison complex, and surrounding artillery bases",
                    "Pushed regime forces into isolated bunker redoubts around Regional Command HQ",
                    "Interim Executive Council (IEC) established governance across >85% of Kayah State"
                ],
                strategic_impact="Immobilized regime in eastern central sector; created a direct threat vector against Naypyidaw (~90 miles away).",
                tactical_innovations=["Falcon Drone Unit coordinated pinpoint thermite drops on fortified artillery bunkers", "LoRa mesh network tactical communication"],
                captured_installations=["Loikaw University base", "Demoso Police Station", "Shadaw Base Camp", "Mawchi Tin-Tungsten Mining Complex"],
                civilian_risk_profile="Loikaw evacuated of 80% civilian population; daily Su-30 and Mi-35 airstrikes leveled entire urban wards.",
                risk_level="CRITICAL"
            ),
            "OP_0307_KACHIN": EAOOperation(
                op_id="OP_0307_KACHIN",
                name="Operation 0307 (Kachin Frontier Offensive)",
                theater="Northern Mountain & China Borderland",
                state_region="Kachin State & Northern Shan",
                timeframe="2024-03-07 to 2024-07-30",
                primary_forces="Yang (Aggressive heavy artillery and outpost rollback)",
                actors=["KIA", "KPDF", "ABSDF"],
                opposing_force="SAC Northern Command & Division 88",
                key_milestones=[
                    "Mar 7, 2024: Synchronized offensive targeting SAC mountain artillery outposts around Laiza",
                    "Overran strategic Hka Ya Bum and Bum Re Bum mountain artillery fortresses",
                    "Captured Lweje border trade gate with China (Apr 2024)",
                    "Liberated Sumprabum, Injangyang, and Sinbo townships",
                    "Surrounded regime garrison in Bhamo and cut Myitkyina resupply roads"
                ],
                strategic_impact="Permanently eliminated artillery threat to KIO headquarters; secured key China land port.",
                tactical_innovations=["Sustained heavy 122mm counter-battery bombardment", "Jungle tunnel infiltration bypassing minefields"],
                captured_installations=["Hka Ya Bum artillery base", "Lweje Customs Port", "Sumprabum Township Police HQ", "Sinbo Base"],
                civilian_risk_profile="IDP camps near Laiza subject to artillery and drone shelling (e.g. Mung Lai Hkyet tragedy precedent).",
                risk_level="HIGH"
            ),
            "OP_1018_PANGWA": EAOOperation(
                op_id="OP_1018_PANGWA",
                name="Operation 1018 (Liberation of Rare-Earth Mining Hubs)",
                theater="Sino-Burmese High Frontier",
                state_region="Kachin State (Special Region 1)",
                timeframe="2024-09-20 to 2024-10-25",
                primary_forces="Yang -> Harmony (Control of global critical mineral choke points)",
                actors=["KIA (Brigades 7 & 1)"],
                opposing_force="NDA-K BGF Battalions 1001, 1002, 1003 & SAC Army elements",
                key_milestones=[
                    "Sep 2024: KIA advanced into Chipwi town, overrunning BGF headquarters",
                    "Oct 2024: Advanced to Pangwa border city, defeating Zahkung Ting Ying's proxy militia",
                    "Oct 21, 2024: Full liberation of Pangwa; took control of global dysprosium and terbium extraction cluster"
                ],
                strategic_impact="Stripped regime of hundreds of millions of dollars in mineral taxes; gave KIO control of over 60% of China's heavy rare-earth raw imports.",
                tactical_innovations=["High-altitude alpine warfare in freezing terrain; coordinated encirclement of border posts"],
                captured_installations=["Chipwi BGF Headquarters", "Pangwa Border Station", "Rare-earth processing facilities"],
                civilian_risk_profile="Disruption of Chinese mining technician operations; border trade gate seal by Yunnan customs.",
                risk_level="HIGH"
            ),
            "OP_RAKHINE_PALETWA": EAOOperation(
                op_id="OP_RAKHINE_PALETWA",
                name="Battle of Paletwa (Kaladan Corridor Liberation)",
                theater="Western Riverine & Mountain Choke Point",
                state_region="Chin State / Rakhine Border",
                timeframe="2023-11-13 to 2024-01-15",
                primary_forces="Yin -> Yang (Decisive riverine and highland interdiction)",
                actors=["Arakan Army (AA)"],
                opposing_force="SAC Western Command (Tactical Operations Command Meewa)",
                key_milestones=[
                    "Nov 2023: AA attacked the heavily fortified Meewa mountain redoubt overlooking Kaladan River",
                    "Overcame 70+ days of relentless airstrikes and nerve-gas munition allegations",
                    "Jan 15, 2024: Complete capture of Paletwa and Samee towns"
                ],
                strategic_impact="Liberated all of Paletwa District; secured Indian Kaladan Multi-Modal gateway; isolated Northern Rakhine from mainland.",
                tactical_innovations=["Sub-surface river supply infiltration under night thermal blackout"],
                captured_installations=["Meewa Hill Strategic Base", "Paletwa Tactical Operations Command (TOC)"],
                civilian_risk_profile="Severe food and medical blockades along Kaladan River; widespread displacement.",
                risk_level="CRITICAL"
            ),
            "OP_RAKHINE_CENTRAL": EAOOperation(
                op_id="OP_RAKHINE_CENTRAL",
                name="Central Rakhine Heartland Liberation",
                theater="Ancient Historical Core & Naval Estuaries",
                state_region="Rakhine State (Central)",
                timeframe="2024-01-15 to 2024-04-01",
                primary_forces="Yang (Total conventional territorial rollback)",
                actors=["Arakan Army (AA)"],
                opposing_force="SAC Western Command (Light Infantry Battalions 540, 377, 378)",
                key_milestones=[
                    "Feb 2024: Captured ancient capital Mrauk-U; rescued priceless archaeological treasures",
                    "Feb 2024: Captured Kyauktaw and Minbya towns; seized dozens of naval landing craft and howitzers",
                    "Mar 2024: Captured Ponnagyun (just 15 miles from state capital Sittwe); captured Myebon port"
                ],
                strategic_impact="Confined SAC Western Command in northern Rakhine strictly to Sittwe island; established Arakan People's Revolutionary Government civil courts.",
                tactical_innovations=["Sinking and capturing SAC naval landing craft using recoilless rifles and rocket artillery"],
                captured_installations=["Kyauktaw Military Base (LIB 376)", "Mrauk-U Police HQ", "Myebon Naval Pier"],
                civilian_risk_profile="Naval gunboats shelled civilian riverbanks; historical pagodas struck by junta airstrikes.",
                risk_level="CRITICAL"
            ),
            "OP_RAKHINE_NORTH": EAOOperation(
                op_id="OP_RAKHINE_NORTH",
                name="Northern Rakhine & Border Gates Liberation",
                theater="Mayu River & Bangladesh Frontier",
                state_region="Rakhine State (North)",
                timeframe="2024-04-01 to 2024-12-15",
                primary_forces="Chaos -> Harmony (Combating proxy insurgencies and securing borders)",
                actors=["Arakan Army (AA)"],
                opposing_force="SAC Military Operations Command (MOC 15) + ARSA/ARA proxy fighters",
                key_milestones=[
                    "May 18, 2024: Captured Buthidaung and headquarters of Military Operations Command 15",
                    "Exposed regime recruitment of Rohingya youths armed to fight AA",
                    "Dec 2024: Captured Maungdaw border town after grueling siege of Battalion 5"
                ],
                strategic_impact="AA controls entire 168-mile Bangladesh frontier; eliminated regime presence in Mayu peninsula.",
                tactical_innovations=["Thermal drone spotting in monsoon mangrove swamps"],
                captured_installations=["MOC-15 Headquarters", "Border Guard Police Battalion 5 (Maungdaw)"],
                civilian_risk_profile="Severe intercommunal tension; arson of Buthidaung residential wards; refugee flows to Cox's Bazar.",
                risk_level="CRITICAL"
            ),
            "OP_RAKHINE_SOUTH": EAOOperation(
                op_id="OP_RAKHINE_SOUTH",
                name="Southern Rakhine Coastal & Airport Campaign",
                theater="Bay of Bengal Deep Water Axis",
                state_region="Rakhine State (South)",
                timeframe="2024-04-15 to 2024-09-30",
                primary_forces="Yang (Deep maritime penetration)",
                actors=["Arakan Army (AA)"],
                opposing_force="SAC Navy, Air Force & LIB 566 / LIB 55",
                key_milestones=[
                    "Apr 2024: Captured Ramree Island after 3-month battle protecting Kyaukphyu corridor",
                    "Jul 2024: Captured Thandwe and the famous Ngapali Beach Mazin Airport",
                    "Aug-Sep 2024: Captured Taungup university and Kyeintali town, pushing toward Ayeyarwady Region"
                ],
                strategic_impact="Deprived junta of all coastal tourism and sea-resupply airfields; directly threatened Ayeyarwady Delta.",
                tactical_innovations=["Amphibious shoreline flanking maneuvers around mangrove estuaries"],
                captured_installations=["Ngapali Mazin Airport", "Ramree Island garrison", "Taungup University outpost"],
                civilian_risk_profile="Airstrikes on Ngapali luxury hotels and residential villages; naval blockade starving coastal populations.",
                risk_level="HIGH"
            ),
            "OP_ANN_WESTERN_CMD": EAOOperation(
                op_id="OP_ANN_WESTERN_CMD",
                name="Siege of SAC Western Command Headquarters (Ann)",
                theater="Arakan Mountains Gateway",
                state_region="Rakhine State (Central Mountain Pass)",
                timeframe="2024-10-01 to 2025-10-01",
                primary_forces="Chaos -> Yang (Strategic headquarters decapitation)",
                actors=["Arakan Army (AA)"],
                opposing_force="SAC Western Command HQ (Ann) & Allied Garrison Divisions",
                key_milestones=[
                    "Oct 2024: AA cut off the Minbu-Ann highway across Arakan Yoma pass",
                    "Overran outer defense rings, military hospital, and Ann airfield perimeter",
                    "Surrounded headquarters bunker complex of Western Command"
                ],
                strategic_impact="Imminent collapse of entire regime command infrastructure in western Myanmar; seals complete liberation of Rakhine.",
                tactical_innovations=["Heavy artillery concentration on command bunkers; cutting emergency air-drop supply corridors"],
                captured_installations=["Ann Airfield", "Military Medical Depot", "Myeik Hill base"],
                civilian_risk_profile="Ann township under total blackout; mass civilian flight across mountains into Magway.",
                risk_level="CRITICAL"
            ),
            "OP_HSIHSENG_PAO": EAOOperation(
                op_id="OP_HSIHSENG_PAO",
                name="Battle of Hsihseng & Hopong",
                theater="Pa-O Homeland & Inle Lake Frontier",
                state_region="Shan State (South)",
                timeframe="2024-01-22 to 2024-05-30",
                primary_forces="Chaos (Fratricidal militia clashes and regime retaliation)",
                actors=["PNLA", "KNDF", "Southern PDFs"],
                opposing_force="SAC Eastern Command & PNA Proxy Militia",
                key_milestones=[
                    "Jan 22, 2024: Clashes erupted after regime intercepted PNLA arms convoy in Sam Hka",
                    "PNLA and allies captured Hsihseng town; broke decade-long ceasefire",
                    "Regime deployed toxic gas/thermobaric munitions and air raids to contest town"
                ],
                strategic_impact="Opened a southern Shan resistance corridor linking Karenni directly to northern Shan.",
                tactical_innovations=["Urban barricade defense resisting FAB-500 aerial drops"],
                captured_installations=["Hsihseng Police Headquarters", "Sam Hka Bridge outpost"],
                civilian_risk_profile="Over 100,000 Pa-O civilians displaced; historic Buddhist monasteries damaged by airstrikes.",
                risk_level="HIGH"
            ),
            "OP_MYAWADDY_AH1": EAOOperation(
                op_id="OP_MYAWADDY_AH1",
                name="Battle of Myawaddy & Asian Highway 1",
                theater="Thai Borderland & Trade Superhighway",
                state_region="Kayin State",
                timeframe="2024-03-10 to 2024-05-15",
                primary_forces="Yang -> Harmony (Cross-border economic leverage)",
                actors=["KNU/KNLA Brigade 6", "KNDO", "Cobra Column", "Federal Wings"],
                opposing_force="SAC Infantry Battalion 275 & Aung Zeya Operation Reinforcement Column",
                key_milestones=[
                    "Mar 2024: Overran Thingannyinaung base (Strategic TOC guarding Dawna mountain)",
                    "Apr 11, 2024: KNLA captured Infantry Battalion 275 in Myawaddy; regime soldiers fled to Thai border Bridge No. 2",
                    "Apr-May 2024: Defeated the massive SAC 'Aung Zeya' mechanized relief column on Dawna mountains",
                    "Saw Chit Thu's BGF maintained tactical neutrality, preventing urban destruction"
                ],
                strategic_impact="Choked regime's most lucrative overland customs port ($1B+); demonstrated junta inability to project ground armor through mountain passes.",
                tactical_innovations=["Precision drone strikes on armored columns traversing mountain serpentine curves"],
                captured_installations=["Thingannyinaung Tactical Command Base", "Infantry Battalion 275", "Asian Highway 1 Toll Gate"],
                civilian_risk_profile="10,000+ civilians sheltered temporarily in Mae Sot, Thailand; trade temporarily paralyzed.",
                risk_level="HIGH"
            ),
            "OP_KANAUNG_MANDALAY": EAOOperation(
                op_id="OP_KANAUNG_MANDALAY",
                name="Operation Kanaung & Mandalay North Liberation",
                theater="Upper Irrawaddy River Corridor",
                state_region="Mandalay Region",
                timeframe="2024-06-25 to 2024-09-30",
                primary_forces="Yang (Central heartland encroachment)",
                actors=["MDY-PDF", "TNLA", "Local LPDFs"],
                opposing_force="SAC Central Command (Mandalay Airbase & Division 99)",
                key_milestones=[
                    "Jun 2024: Coordinated with Operation 1027 Phase 2",
                    "Captured Singu township on the Irrawaddy riverbanks (Jul 2024)",
                    "Captured Thabeikkyin township and overran gold mining outposts (Aug 2024)",
                    "Advanced within 35 miles of Mandalay Royal Palace"
                ],
                strategic_impact="First permanent liberation of urban townships inside the Bamar ethnic heartland (Mandalay Region).",
                tactical_innovations=["Combined riverine boat and motorcycle blitz tactics"],
                captured_installations=["Singu Police HQ", "Thabeikkyin Military Camp", "Mogok-Mandalay Highway checkpoints"],
                civilian_risk_profile="Intense airstrikes by Yak-130 and Su-30 launched from Tada-U Airbase on Irrawaddy villages.",
                risk_level="HIGH"
            ),
            "OP_RIHKHAWDAR_CHIN": EAOOperation(
                op_id="OP_RIHKHAWDAR_CHIN",
                name="Liberation of Indo-Myanmar Border Gates",
                theater="Chin Hills & Mizoram Border",
                state_region="Chin State",
                timeframe="2023-11-13 to 2024-02-28",
                primary_forces="Yin -> Yang (International border gate liberation)",
                actors=["CNA / Chinland Council", "CDF-Zoland"],
                opposing_force="SAC Infantry Battalions 268 & 269",
                key_milestones=[
                    "Nov 13, 2023: Assault on Rihkhawdar border town and customs gate opposite Zokhawthar, Mizoram",
                    "Overran junta military camp; soldiers fled across border into India",
                    "Raised Chin National Flag over international border bridge"
                ],
                strategic_impact="Provided Chinland Government with direct customs revenue and sovereign border access to India.",
                tactical_innovations=["Mountain ridge encirclement cutting off resupply flights"],
                captured_installations=["Rihkhawdar Border Customs Gate", "Camp 268 Outpost"],
                civilian_risk_profile="Hundreds of refugees crossed into Mizoram; regime fighter jets dropped bombs within 500 meters of Indian border.",
                risk_level="HIGH"
            ),
            "OP_KAWLIN_SAGAING": EAOOperation(
                op_id="OP_KAWLIN_SAGAING",
                name="Battle of Kawlin (Anyar District Capital)",
                theater="Northern Dry Zone & Railway Axis",
                state_region="Sagaing Region",
                timeframe="2023-11-03 to 2024-02-15",
                primary_forces="Chaos -> Harmony (Urban defense against massed airstrikes)",
                actors=["Kachin Independence Army (KIA)", "NUG PDF Battalions"],
                opposing_force="SAC Northwestern Command & 33rd Light Infantry Division",
                key_milestones=[
                    "Nov 6, 2023: Captured Kawlin district capital—first district-level city captured by NUG/allies",
                    "Established NUG public administration, banks, and community police for 90 days",
                    "Feb 2024: Faced massive 3-pronged junta counter-offensive with heavy armor and airstrikes; tactical withdrawal to rural sectors"
                ],
                strategic_impact="Demonstrated NUG capability to administer urban districts while exposing vulnerabilities to uncontested regime air supremacy.",
                tactical_innovations=["Rapid establishment of interim civilian banking and civil protection"],
                captured_installations=["Kawlin District Administration Office", "Myanma Economic Bank Kawlin Branch"],
                civilian_risk_profile="Regime scorched-earth burning of 80% of Kawlin town upon re-entry; 50,000 civilians displaced.",
                risk_level="CRITICAL"
            )
        }

        # 3. EXPANDED THEATER ANALYTICS (6 Core Theaters)
        self.theaters: Dict[str, TheaterAnalytics] = {
            "THEATER_SHAN_NORTH": TheaterAnalytics(
                theater_id="THEATER_SHAN_NORTH",
                name="Northern Shan State Theater",
                geographical_scope="Kokang, Wa, Ta'ang regions, Lashio corridor to China border",
                dominant_actors=["MNDAA", "TNLA", "UWSA", "SSPP"],
                eao_territory_pct=78.5,
                junta_garrisons_status="Collapsed; restricted strictly to southern highway pockets and airbases",
                key_border_gates=["Chinshwehaw", "Mongko", "Kyukok (Pangsai)", "Nansan"],
                strategic_infrastructure=["Lashio Airport (Captured)", "Kunlong Suspension Bridge", "Oil/Gas Pipelines to Yunnan"],
                humanitarian_crisis_level="CRITICAL (Telecom/power cuts, Chinese trade embargoes)"
            ),
            "THEATER_WESTERN": TheaterAnalytics(
                theater_id="THEATER_WESTERN",
                name="Western Coastal & Mountain Theater (Rakhine & Chin)",
                geographical_scope="Rakhine State (17 Townships) and Chin State borderland",
                dominant_actors=["Arakan Army (AA)", "Chinland Council (CNA)", "Chin Brotherhood"],
                eao_territory_pct=88.5,
                junta_garrisons_status="Besieged in Sittwe enclave, Kyaukphyu naval port, and Ann Western Command bunker",
                key_border_gates=["Maungdaw (Bangladesh)", "Rihkhawdar (India)", "Paletwa River Port"],
                strategic_infrastructure=["Kaladan Multi-Modal Project", "Kyaukphyu Deep-Sea Port (China)", "Ngapali Beach Mazin Airport"],
                humanitarian_crisis_level="CATASTROPHIC (Total regime medical/food blockade, risk of regional famine)"
            ),
            "THEATER_KACHIN_NORTH": TheaterAnalytics(
                theater_id="THEATER_KACHIN_NORTH",
                name="Northern Mountain & Jade/Rare-Earth Theater",
                geographical_scope="Kachin State frontier, Laiza HQ to Putao and Hpakant",
                dominant_actors=["KIA", "KPDF"],
                eao_territory_pct=76.0,
                junta_garrisons_status="Confined to Myitkyina, Bhamo, and isolated airport redoubts",
                key_border_gates=["Lweje", "Pangwa", "Mai Ja Yang", "Kanpiketi"],
                strategic_infrastructure=["Pangwa Rare-Earth Mines", "Hpakant Jade Mines", "Mali/N'Mai Hka dams"],
                humanitarian_crisis_level="HIGH (Persistent airstrikes on IDP camps along Laiza perimeter)"
            ),
            "THEATER_KARENNI_EAST": TheaterAnalytics(
                theater_id="THEATER_KARENNI_EAST",
                name="Karenni Highland & Southern Shan Theater",
                geographical_scope="Kayah State, Southern Shan (Hsihseng/Pekon), Naypyidaw border",
                dominant_actors=["KNDF", "KA", "KNPLF", "PNLA"],
                eao_territory_pct=84.0,
                junta_garrisons_status="Confined to ROC Loikaw and fortified artillery hilltops",
                key_border_gates=["Mese (Thailand BP-13, BP-14)"],
                strategic_infrastructure=["Balu Chaung Lawpita Hydropower Plant", "Mawchi Mines", "Loikaw Airport"],
                humanitarian_crisis_level="CRITICAL (Over 250,000 IDPs in jungle camps, unexploded cluster munitions)"
            ),
            "THEATER_KAYIN_MON": TheaterAnalytics(
                theater_id="THEATER_KAYIN_MON",
                name="Southeastern Border & Coastal Trade Theater",
                geographical_scope="Kayin State, Mon State, Tanintharyi corridor",
                dominant_actors=["KNU/KNLA", "KNDO", "RMA", "KNA/BGF"],
                eao_territory_pct=68.0,
                junta_garrisons_status="Interdicted along mountain corridors; relying on coastal naval resupply",
                key_border_gates=["Myawaddy Asian Highway 1", "Payathonzu (Three Pagodas Pass)"],
                strategic_infrastructure=["Asian Highway 1", "Yadana Gas Pipeline", "Dawei Deep-Sea Port Road"],
                humanitarian_crisis_level="HIGH (Cross-border displacement into Tak/Mae Sot provinces)"
            ),
            "THEATER_ANYAR_CENTRAL": TheaterAnalytics(
                theater_id="THEATER_ANYAR_CENTRAL",
                name="Central Dry Zone (Anyar) Heartland",
                geographical_scope="Sagaing, Magway, and Northern Mandalay Regions",
                dominant_actors=["NUG PDFs", "MDY-PDF", "BPLA", "Local LPDFs"],
                eao_territory_pct=52.0,
                junta_garrisons_status="Controlling urban garrison centers, major airbases, and river flotillas",
                key_border_gates=["Internal riverine transit hubs (Chindwin & Irrawaddy)"],
                strategic_infrastructure=["Letpadaung Copper Mine", "Tada-U / Shwebo Airbases", "Mandalay Railway"],
                humanitarian_crisis_level="CRITICAL (Retaliatory junta arson of 80,000+ homes, aerial thermobaric strikes)"
            )
        }

        # 4. GEOPOLITICAL & TACTICAL DYNAMICS
        self.geopolitical_vectors: Dict[str, Any] = {
            "BEIJING_HAIGENG_TALKS": {
                "rounds": ["Round 1 (Dec 2023)", "Round 2 (Jan 2024 - Haigeng Agreement)", "Round 3 (Mar 2024)", "Round 4 (May 2024)", "Round 5 (Aug 2024)"],
                "broker": "Chinese Ministry of Foreign Affairs (Special Envoy Deng Xijun / Yunnan Provincial Authorities)",
                "strategic_goals": ["Safeguard China-Myanmar Oil & Gas Pipelines", "Eradicate Kokang telecom scam centers", "Reopen Muse-Ruili and Chinshwehaw border trade"],
                "breakdown_cause": "SAC air raids violating Haigeng truce led to Operation 1027 Phase 2 and fall of Lashio."
            },
            "CHINESE_BORDER_INTERVENTIONS_2024_2025": {
                "tactics": [
                    "Complete closure of border customs gates in Wanding, Kyin San Kyawt, and Chinshwehaw",
                    "Cutoff of electricity, internet, and banking to Kokang (MNDAA) and Wa (UWSA) regions (Aug-Oct 2024)",
                    "Live-fire PLA border military exercises opposite Muse and Laukkai",
                    "Pressure on UWSA to halt arms and fuel transfers to allied EAOs"
                ]
            },
            "CONSCRIPTION_LAW_CRISIS": {
                "date_enacted": "2024-02-10",
                "provisions": "Forced conscription of men aged 18-35 and women aged 18-27 for up to 5 years",
                "impact": [
                    "Exodus of over 300,000 young professionals to Thailand, India, and overseas",
                    "Tens of thousands of youth fled to EAO liberated territories (KNU, KIA, KNDF) for military training",
                    "Collapse of urban industrial workforce and hyperinflation of Myanmar Kyat (reaching >4,500 MMK/USD in late 2024)"
                ]
            },
            "FPV_DRONE_AND_AERIAL_TAXONOMY": {
                "resistance_drone_tactics": [
                    "Custom 3D-printed hexacopters with servo-triggered 60mm/81mm mortar fin releases",
                    "FPV Kamikaze Drones with RPG-7 warheads striking armored vehicles and bunker slits",
                    "Signal-hopping radio links overcoming junta portable GPS/RF jammer backpacks"
                ],
                "junta_aerial_retaliation": [
                    "FAB-500 M-62 high-explosive unguided bombs dropped from transport planes and FTC-2000G jets",
                    "ODAB-500PM thermobaric fuel-air explosive bombs targeting civilian village centers",
                    "Mi-35P Hind attack helicopters conducting low-level 23mm cannon strafing",
                    "Chinese-supplied CH-4 and Rainbow reconnaissance-strike UAVs"
                ]
            }
        }

        # 5. COALITIONS & MULTILATERAL TREATIES
        self.coalitions: Dict[str, Dict[str, Any]] = {
            "3BA": {
                "name": "Three Brotherhood Alliance",
                "members": ["MNDAA", "TNLA", "AA"],
                "established": "2019",
                "nature": "Offensive & Defensive Military Alliance",
                "joint_operations": ["Operation 1027 Phase 1", "Operation 1027 Phase 2"],
                "strategic_doctrine": "Coordinated multi-theater distraction, combined-arms urban sieges, synchronized border trade capture.",
                "cohesion_level": "VERY_HIGH"
            },
            "FPNCC": {
                "name": "Federal Political Negotiation and Consultative Committee",
                "members": ["UWSA", "MNDAA", "TNLA", "AA", "KIA", "SSPP", "NDAA_MONG_LA"],
                "established": "2017",
                "nature": "Northern Hegemonic Consultative Coalition (Chaired by UWSA)",
                "strategic_doctrine": "Collective bargaining with Naypyidaw and Beijing; maintaining ethnic autonomy without central state subjugation.",
                "cohesion_level": "MODERATE_HIGH"
            },
            "K7": {
                "name": "K7 Revolutionary Alliance (Core EAO-NUG Coalition)",
                "members": ["KIA", "KNU_KNLA", "KNDF", "KNPP_KA", "CNF_CNA", "NUG_PDF_CENTRAL"],
                "established": "2021",
                "nature": "Federal Democratic Armed Coalition against the Military Dictatorship",
                "strategic_doctrine": "Nationwide synchronized multi-front war; joint training and weapons distribution for Bamar resistance youth.",
                "cohesion_level": "HIGH"
            },
            "CHIN_BROTHERHOOD": {
                "name": "Chin Brotherhood Alliance (CB)",
                "members": ["CHIN_BROTHERHOOD", "AA", "YDF"],
                "established": "2023",
                "nature": "Regional Southern/Central Chin Military Pact",
                "strategic_doctrine": "Joint operations with Arakan Army; counterweight to the Chinland Council.",
                "cohesion_level": "HIGH"
            },
            "SCEF": {
                "name": "Steering Committee for the Emergence of a Federal Democratic Union",
                "members": ["KNU_KNLA", "KNPP_KA", "CNF_CNA", "RMA"],
                "established": "2024",
                "nature": "Southern & Eastern Political-Military Coordination",
                "strategic_doctrine": "Consolidation of federal governance across Karen, Karenni, Chin, and Mon liberated sectors.",
                "cohesion_level": "MODERATE"
            }
        }

        # 6. INTER-FACTIONAL RELATIONAL MATRIX
        self.relationships: Dict[Tuple[str, str], FactionRelationship] = {}
        self._init_relationship_matrix()

    def _add_rel(
        self,
        f1: str,
        f2: str,
        rel_type: RelationshipType,
        affinity: float,
        coalition: Optional[str],
        history: str,
        ops: List[str],
        frictions: List[str],
        arms: str
    ):
        r1 = FactionRelationship(
            source_faction=f1, target_faction=f2, rel_type=rel_type.value,
            affinity_score=affinity, coalition=coalition, historical_context=history,
            joint_operations=ops, friction_points=frictions, arms_flow=arms
        )
        r2 = FactionRelationship(
            source_faction=f2, target_faction=f1, rel_type=rel_type.value,
            affinity_score=affinity, coalition=coalition, historical_context=history,
            joint_operations=ops, friction_points=frictions, arms_flow=arms
        )
        self.relationships[(f1, f2)] = r1
        self.relationships[(f2, f1)] = r2

    def _init_relationship_matrix(self):
        # --- 3BA CORE TRIAD ---
        self._add_rel(
            "MNDAA", "TNLA", RelationshipType.STRATEGIC_ALLIANCE, 0.95, "3BA",
            "Co-founders of Three Brotherhood Alliance; fought side-by-side across Northern Shan.",
            ["Operation 1027 Phase 1", "Operation 1027 Phase 2", "Fall of Lashio"],
            ["Minor administrative demarcation in Kutkai and Hsenwi fringe villages."],
            "Shared munitions and joint drone strike command."
        )
        self._add_rel(
            "TNLA", "AA", RelationshipType.STRATEGIC_ALLIANCE, 0.95, "3BA",
            "TNLA hosted AA battalions in Northern Shan during AA's formative years; deep mutual trust.",
            ["Operation 1027 Phase 1", "Battle of Namkham", "Kyaukme Offensive"],
            ["None significant; highly complementary theater roles."],
            "Joint procurement and tactical cross-training."
        )
        self._add_rel(
            "MNDAA", "AA", RelationshipType.STRATEGIC_ALLIANCE, 0.95, "3BA",
            "AA elite commandos deployed inside Kokang to spearhead the siege of Laukkai in Jan 2024.",
            ["Operation 1027 Phase 1", "Siege of Laukkai", "Fall of Lashio"],
            ["None; unbreakable tactical solidarity."],
            "Direct battlefield logistics integration."
        )

        # --- UWSA (WA) HEGEMONIC RELATIONS ---
        self._add_rel(
            "UWSA", "MNDAA", RelationshipType.ARMS_SUPPLIER_RECIPIENT, 0.75, "FPNCC",
            "Wa provided refuge and arms to Peng Deren's forces after 2009 Kokang expulsion; shared CPB heritage.",
            ["Hopang handover to UWSA (Jan 2024)", "Border trade security coordination"],
            ["UWSA under Chinese pressure halted official ammunition transfers in late 2024."],
            "UWSA is primary supplier of Type 81 ammunition, 12.7mm rounds, and heavy mortars to MNDAA."
        )
        self._add_rel(
            "UWSA", "TNLA", RelationshipType.ARMS_SUPPLIER_RECIPIENT, 0.70, "FPNCC",
            "FPNCC partners; Wa supplies ammunition and small arms; non-aggression across boundaries.",
            ["Northern Shan border defense coordination"],
            ["Periodic concerns over Ta'ang expansion towards Tangyan/Monghsu border."],
            "Weapons and ammunition sales via Panghsang arsenals."
        )
        self._add_rel(
            "UWSA", "AA", RelationshipType.ARMS_SUPPLIER_RECIPIENT, 0.75, "FPNCC",
            "Wa supplied AA with heavy MANPADS, machine guns, and ammunition for the Rakhine theater.",
            ["FPNCC diplomatic sessions"],
            ["None; distant geographical theaters prevent friction."],
            "Heavy weapons pipelines via maritime and riverine smuggling routes."
        )
        self._add_rel(
            "UWSA", "SSPP", RelationshipType.COALITION_PARTNER, 0.80, "FPNCC",
            "Longstanding strategic alliance; UWSA troops stationed in Wan Hai to deter SAC and RCSS.",
            ["Joint anti-RCSS offensives in central Shan (2021-2022)", "Tangyan security cordon (2024)"],
            ["Minor disagreements on joint administrative control in Tangyan and Kehsi."],
            "Wa supplies heavy artillery and small arms to SSPP."
        )
        self._add_rel(
            "UWSA", "RCSS", RelationshipType.HISTORICAL_RIVALRY, -0.65, None,
            "Decades-long rivalry along Thai border (Southern Wa vs RCSS Loi Tai Leng).",
            ["Periodic border skirmishes in Mong Hsat and Mong Ton"],
            ["Unresolved territorial boundaries along the Thailand-Shan frontier."],
            "Hostile buffer; no arms flow."
        )

        # --- SHAN STATE INTER-ETHNIC FLASHPOINTS ---
        self._add_rel(
            "TNLA", "SSPP", RelationshipType.TERRITORIAL_FRICTION, -0.35, "FPNCC",
            "Both claim administrative authority over post-junta liberated towns in Northern Shan.",
            ["Haigeng ceasefire stabilization"],
            ["Hsipaw town administration standoff (2024)", "Kyaukme taxation overlapping disputes", "Namkham village control"],
            "Independent arms pipelines; sporadic localized standoffs."
        )
        self._add_rel(
            "SSPP", "RCSS", RelationshipType.HISTORICAL_RIVALRY, -0.85, None,
            "Intense fratricidal Shan civil war post-2015; SSPP partnered with TNLA/Wa to drive RCSS south.",
            ["Clashes in Kyethi, Monghsu, and Hsipaw (2018-2022)"],
            ["Competition for leadership of the Shan nation", "Southern corridor control"],
            "Direct military confrontation; strict armed barriers."
        )

        # --- KACHIN STATE RELATIONS ---
        self._add_rel(
            "KIA", "MNDAA", RelationshipType.COALITION_PARTNER, 0.80, "FPNCC",
            "KIA provided sanctuary and initial regrouping training to MNDAA in Laiza after 2009.",
            ["Operation 1027 joint frontlines in Kutkai", "Northern corridor interdiction"],
            ["Border trade route precedence around Muse and Mongko."],
            "Mutual ammunition trade and repair facilities."
        )
        self._add_rel(
            "KIA", "MDY_PDF", RelationshipType.STRATEGIC_ALLIANCE, 0.90, "K7",
            "KIA armed, trained, and equipped the Mandalay People's Defence Force from inception.",
            ["Operation 1027 Phase 1 & 2", "Liberation of Singu and Thabeikkyin"],
            ["None; exemplary model of EAO-PDF operational integration."],
            "KIA directly supplies indigenous K-09 rifles, mortars, and explosives to MDY-PDF."
        )
        self._add_rel(
            "KIA", "BPLA", RelationshipType.STRATEGIC_ALLIANCE, 0.90, None,
            "KIO hosted and trained Maung Saungkha's Bamar People's Liberation Army in Laiza.",
            ["Operation 1027 Phase 1", "Northern Shan campaigns"],
            ["None; deep political and military trust."],
            "KIA provided arms, uniforms, and tactical field radios."
        )
        self._add_rel(
            "KIA", "SNA", RelationshipType.HISTORICAL_RIVALRY, -0.60, None,
            "Territorial dispute over Shanni ethnic lands in Mohnyin, Mogaung, and Homalin.",
            ["Armed clashes in Homalin gold mining regions (2022-2024)"],
            ["SNA accuses KIA of Bamar-like dominance over Shanni populations; KIA views SNA as SAC collaborator."],
            "Hostile competition."
        )
        self._add_rel(
            "KIA", "NDA_K_BGF", RelationshipType.ACTIVE_HOSTILITY, -1.00, None,
            "Decades-long feud with Zahkung Ting Ying's pro-junta proxy border guard battalions.",
            ["Operation 0307 / 1018 (Chipwi & Pangwa liberation Sep-Oct 2024)"],
            ["Eliminated NDA-K BGF; KIA captured all rare-earth mining zones."],
            "War of annihilation; KIA captured all BGF depots."
        )

        # --- KAREN, KARENNI & MON RELATIONS ---
        self._add_rel(
            "KNU_KNLA", "KNDF", RelationshipType.STRATEGIC_ALLIANCE, 0.90, "K7",
            "KNU 2nd & 5th Brigades provide logistics, drone technology, and rear sanctuaries to Karenni forces.",
            ["Southern Shan & Karenni highway interdictions", "Federal Wings drone deployments"],
            ["Minor coordination challenges in Taungoo borderland."],
            "Drone technology exchange and joint mortar procurement."
        )
        self._add_rel(
            "KNDF", "KNPP_KA", RelationshipType.STRATEGIC_ALLIANCE, 0.95, "K7",
            "KNDF was founded under the mentorship of KNPP; operates as unified Karenni defense arm.",
            ["Operation 1107", "Operation 1111 (Siege of Loikaw)", "Mawchi liberation"],
            ["None; unified cabinet under Karenni State IEC."],
            "Integrated weapons arsenals and joint frontline command."
        )
        self._add_rel(
            "KNDF", "KNPLF", RelationshipType.TACTICAL_COOPERATION, 0.85, None,
            "Former BGF defected in June 2023 to fight alongside KNDF against junta.",
            ["Operation 1107 Mese border offensive", "Salween River defense"],
            ["Integrating legacy militia fighters into revolutionary discipline."],
            "Shared captured junta weapons."
        )
        self._add_rel(
            "KNU_KNLA", "RMA", RelationshipType.TACTICAL_COOPERATION, 0.85, "SCEF",
            "KNU 4th Brigade operates jointly with the Ramonnya Mon Army along the Mawlamyine-Ye-Dawei axis.",
            ["Ye-Thanbyuzayat highway ambushes (2024-2025)"],
            ["Boundary delineation in mixed Karen-Mon villages in Ye and Yebyu."],
            "Joint ammunition supply and medical aid."
        )
        self._add_rel(
            "KNU_KNLA", "KNA_BGF", RelationshipType.ARMED_NEUTRALITY, 0.10, None,
            "Saw Chit Thu broke from SAC in Jan 2024; maintains uneasy armed truce with KNU to protect Shwe Kokko casinos.",
            ["Battle of Myawaddy (Saw Chit Thu refused to fight KNU on SAC's behalf)"],
            ["KNU opposition to cross-border telecom scam syndicates and human trafficking compounds."],
            "No formal arms trade; mutual non-aggression along Myawaddy peri-urban border."
        )

        # --- WESTERN FRONT & CHIN STATE FLASHPOINTS ---
        self._add_rel(
            "AA", "CHIN_BROTHERHOOD", RelationshipType.STRATEGIC_ALLIANCE, 0.90, "CHIN_BROTHERHOOD",
            "AA provides heavy artillery, drone strikes, and tactical command to Chin Brotherhood forces.",
            ["Liberation of Matupi (June 2024)", "Kyindwe offensive", "Mindat perimeter operations"],
            ["Friction with Chinland Council (CNF) over regional administrative hegemony."],
            "AA is the primary arms and heavy munition supplier to Chin Brotherhood."
        )
        self._add_rel(
            "AA", "CNF_CNA", RelationshipType.TERRITORIAL_FRICTION, -0.40, None,
            "Rivalry between Arakan Army expansion in Southern Chin (Paletwa/Matupi) and Chinland Council's claims.",
            ["Paletwa liberation", "Battle of Matupi (June 2024 standoffs)"],
            ["AA control of Paletwa (traditionally claimed by Chin); CNA-CB clashes in Matupi requiring NUG mediation."],
            "Tense non-belligerence with periodic proxy clashes."
        )
        self._add_rel(
            "CNF_CNA", "CHIN_BROTHERHOOD", RelationshipType.TERRITORIAL_FRICTION, -0.55, None,
            "Split within the Chin revolution: Chinland Council (allied with NUG) vs Chin Brotherhood (allied with AA).",
            ["Clashes in Matupi town administration (June 2024)"],
            ["Constitutional legitimacy dispute over Chinland Government vs local township self-rule."],
            "Competes for Western weapons and Mizoram border crossing revenue."
        )
        self._add_rel(
            "AA", "ARSA_ROHINGYA", RelationshipType.PROXY_ANTAGONIST, -0.95, None,
            "Junta armed and conscripted Rohingya ARSA/ARA fighters in Buthidaung/Maungdaw to battle AA in 2024.",
            ["Battles of Buthidaung and Maungdaw (April-Dec 2024)"],
            ["ARSA accused of burning Rakhine and Hindu homes; AA accused of forced displacement and harsh crackdowns."],
            "Active proxy warfare; zero cooperation."
        )

        # --- PA-O CIVIL WAR ---
        self._add_rel(
            "PNLA", "PNA", RelationshipType.PROXY_ANTAGONIST, -0.95, None,
            "Pa-O fratricidal civil war: Revolutionary PNLA vs regime-backed PNA (Aung Kham Hti) militia.",
            ["Battle of Hsihseng (Jan-May 2024)", "Hopong clashes"],
            ["PNA enforces junta conscription on Pa-O villages; PNLA attacks junta-PNA supply columns."],
            "Active armed warfare."
        )
        self._add_rel(
            "PNLA", "KNDF", RelationshipType.TACTICAL_COOPERATION, 0.85, None,
            "KNDF sent veteran assault battalions and drone teams to assist PNLA in Hsihseng.",
            ["Battle of Hsihseng", "Inle Lake southern perimeter operations"],
            ["None; close anti-junta revolutionary solidarity."],
            "Joint mortar munitions and drone technology sharing."
        )

    # --- LOOKUP AND ANALYTICS APIS ---

    def get_bilateral_relationship(self, faction_a: str, faction_b: str) -> Optional[FactionRelationship]:
        return self.relationships.get((faction_a.upper().strip(), faction_b.upper().strip()))

    def get_allies(self, faction_id: str) -> List[FactionRelationship]:
        fid = faction_id.upper().strip()
        allies = [r for (f1, f2), r in self.relationships.items() if f1 == fid and r.affinity_score > 0.3]
        allies.sort(key=lambda x: x.affinity_score, reverse=True)
        return allies

    def get_adversaries(self, faction_id: str) -> List[FactionRelationship]:
        fid = faction_id.upper().strip()
        adv = [r for (f1, f2), r in self.relationships.items() if f1 == fid and r.affinity_score < 0.0]
        adv.sort(key=lambda x: x.affinity_score)
        return adv

    def get_friction_points(self, faction_id: str) -> List[FactionRelationship]:
        fid = faction_id.upper().strip()
        frictions = [r for (f1, f2), r in self.relationships.items() if f1 == fid and len(r.friction_points) > 0]
        return frictions

    def get_coalition(self, coalition_id: str) -> Optional[Dict[str, Any]]:
        return self.coalitions.get(coalition_id.upper().strip())

    def list_coalitions(self) -> List[str]:
        return list(self.coalitions.keys())

    def get_operation(self, op_id: str) -> Optional[EAOOperation]:
        return self.operations.get(op_id)

    def get_faction(self, faction_id: str) -> Optional[EAOFaction]:
        return self.factions.get(faction_id)

    def get_theater(self, theater_id: str) -> Optional[TheaterAnalytics]:
        return self.theaters.get(theater_id)

    def list_operations(self) -> List[EAOOperation]:
        return list(self.operations.values())

    def list_factions(self) -> List[EAOFaction]:
        return list(self.factions.values())

    def list_theaters(self) -> List[TheaterAnalytics]:
        return list(self.theaters.values())

    def list_operations_by_theater(self, theater_name: str) -> List[EAOOperation]:
        q = theater_name.lower()
        return [op for op in self.operations.values() if q in op.theater.lower() or q in op.state_region.lower()]

    def list_factions_by_state(self, state_name: str) -> List[EAOFaction]:
        q = state_name.lower()
        return [f for f in self.factions.values() if q in f.primary_state.lower()]

    def search_intel(self, query: str) -> Dict[str, Any]:
        """Deep multi-dimensional search across factions, operations, and theaters."""
        q = query.lower().strip()
        matched_ops = [op for op in self.operations.values() if q in op.name.lower() or q in op.strategic_impact.lower() or any(q in a.lower() for a in op.actors)]
        matched_factions = [f for f in self.factions.values() if q in f.name.lower() or q in f.full_name.lower() or q in f.tactical_posture.lower()]
        matched_theaters = [t for t in self.theaters.values() if q in t.name.lower() or q in t.geographical_scope.lower()]
        
        return {
            "query": query,
            "matched_operations_count": len(matched_ops),
            "matched_factions_count": len(matched_factions),
            "matched_theaters_count": len(matched_theaters),
            "operations": matched_ops,
            "factions": matched_factions,
            "theaters": matched_theaters
        }

    def get_macro_summary(self) -> Dict[str, Any]:
        return {
            "period": "2023-2025",
            "operations_tracked": len(self.operations),
            "factions_tracked": len(self.factions),
            "theaters_tracked": len(self.theaters),
            "macro_territorial_split": {
                "eao_and_resistance_control": "52% - 58%",
                "junta_sac_control": "20% - 28%",
                "contested_active_combat": "18% - 24%"
            },
            "pivotal_events": [
                "Operation 1027 Phase 1: Capitulation of Kokang Laukkai (Jan 2024)",
                "Operation 1027 Phase 2: Historic fall of Lashio Regional Command HQ (Aug 2024)",
                "Arakan Army: Capture of 14/17 townships and siege of Western Command Ann",
                "Operation 0307: Liberation of Pangwa rare-earth mining complexes by KIA (Oct 2024)",
                "Operation 1111: Karenni IEC control of >85% of Kayah State",
                "Enactment of junta Conscription Law and nationwide economic contraction"
            ],
            "geopolitical_framework": "Chinese multi-vector border diplomacy (Haigeng talks + trade blockades) vs resistance momentum"
        }


# ============================================================
# ============================================================
# 4.8. GEOLOGICAL & CRITICAL MINERAL TELEMETRY KNOWLEDGE BASE
# ============================================================

@dataclass
class MineralDeposit:
    deposit_id: str
    name: str
    region_state: str
    host_formation: str
    target_commodities: List[str]
    extraction_method: str
    controlling_actor: str
    geophysical_signature: Dict[str, Any]
    environmental_hazards: List[str]
    economic_significance: str


@dataclass
class TectonicFault:
    fault_id: str
    name: str
    fault_type: str
    length_km: float
    slip_rate_mm_yr: float
    max_credible_magnitude: float
    intersected_mining_districts: List[str]
    seismic_hazard_rating: str


class GeologicalKnowledgeBase:
    def __init__(self):
        self.deposits: Dict[str, MineralDeposit] = {
            "DEP_PANGWA_HREO": MineralDeposit(
                deposit_id="DEP_PANGWA_HREO",
                name="Pangwa-Chipwi Heavy Rare Earth District",
                region_state="Kachin State (Special Region 1)",
                host_formation="Deeply weathered biotite-granite regolith (Ion-Adsorption Clays)",
                target_commodities=["Dysprosium (Dy)", "Terbium (Tb)", "Neodymium (Nd)", "Praseodymium (Pr)"],
                extraction_method="In-situ chemical leaching with ammonium sulfate injection ponds",
                controlling_actor="Kachin Independence Army (KIA / KIO)",
                geophysical_signature={
                    "pXRF_indicators": ["Dy > 150 ppm", "Tb > 40 ppm", "Y > 400 ppm"],
                    "geophone_hz_range": [15.0, 120.0],
                    "insar_displacement_threshold_mm_yr": 45.0
                },
                environmental_hazards=[
                    "Severe groundwater acidification (pH < 4.5)",
                    "Ammonium sulfate chemical runoff into N'Mai Hka watershed",
                    "Slope destabilization and alpine mudslides"
                ],
                economic_significance="Supplies >60% of China's heavy rare-earth raw feedstocks for electric vehicle and defense permanent magnets."
            ),
            "DEP_HPAKANT_JADE": MineralDeposit(
                deposit_id="DEP_HPAKANT_JADE",
                name="Hpakant-Tawmaw Jadeite Tract",
                region_state="Kachin State (Uru River Basin)",
                host_formation="Serpentinite-hosted ophiolite complex jadeitite dikes",
                target_commodities=["High-grade Imperial Jadeite (NaAlSi2O6)", "Omphacite"],
                extraction_method="Heavy mechanical open-pit strip mining and artisanal hand scavenging (Yemase)",
                controlling_actor="KIA & Allied Mining Cooperatives",
                geophysical_signature={
                    "pXRF_indicators": ["Cr > 1200 ppm", "Fe > 1.5%", "Ni > 800 ppm"],
                    "geophone_hz_range": [5.0, 80.0],
                    "insar_displacement_threshold_mm_yr": 120.0
                },
                environmental_hazards=[
                    "Catastrophic monsoon waste-dump landslides (e.g. 2020 Wai Khar disaster)",
                    "River siltation and toxic open-pit lake formation"
                ],
                economic_significance="World's largest jadeite extraction hub ($15B-$30B estimated annual gross trade value)."
            ),
            "DEP_MOGOK_GEMS": MineralDeposit(
                deposit_id="DEP_MOGOK_GEMS",
                name="Mogok Stone Tract (Mogok Metamorphic Belt)",
                region_state="Mandalay Region & Shan Border",
                host_formation="Marble-hosted skarns, gneiss, and granitic pegmatites",
                target_commodities=["Pigeon's Blood Ruby", "Royal Blue Sapphire", "Spinel", "Peridot"],
                extraction_method="Hard-rock deep tunneling and alluvial gravel washing",
                controlling_actor="TNLA & Mandalay People's Defence Force (MDY-PDF)",
                geophysical_signature={
                    "pXRF_indicators": ["Al2O3 > 98%", "Cr > 500 ppm", "Ti > 300 ppm"],
                    "geophone_hz_range": [20.0, 300.0],
                    "insar_displacement_threshold_mm_yr": 25.0
                },
                environmental_hazards=[
                    "Underground tunnel cave-ins and unventilated gas hazards",
                    "Unregulated artisanal dynamite blasting"
                ],
                economic_significance="Historic global benchmark for high-value untreated gemstones and rubies."
            ),
            "DEP_MAWCHI_TIN_W": MineralDeposit(
                deposit_id="DEP_MAWCHI_TIN_W",
                name="Mawchi Tin-Tungsten Lode Complex",
                region_state="Kayah (Karenni) State",
                host_formation="Hydrothermal quartz-cassiterite-wolframite veins in Mesozoic granites",
                target_commodities=["Cassiterite (Tin - Sn)", "Wolframite (Tungsten - W)"],
                extraction_method="Underground adit mining and gravity separation sluicing",
                controlling_actor="Karenni Nationalities Defence Force (KNDF / IEC)",
                geophysical_signature={
                    "pXRF_indicators": ["Sn > 0.8%", "W > 0.5%", "As > 200 ppm"],
                    "geophone_hz_range": [10.0, 150.0],
                    "insar_displacement_threshold_mm_yr": 35.0
                },
                environmental_hazards=[
                    "Arsenic and heavy metal tailings leaching into Kemapyu / Salween river",
                    "Acid rock drainage and soil degradation"
                ],
                economic_significance="Historic primary tin/tungsten supplier in Southeast Asia, vital for electronics soldering and hardened alloys."
            ),
            "DEP_MONYWA_COPPER": MineralDeposit(
                deposit_id="DEP_MONYWA_COPPER",
                name="Monywa-Letpadaung Porphyry Copper Complex",
                region_state="Sagaing Region",
                host_formation="High-sulfidation epithermal/porphyry copper volcanic intrusive",
                target_commodities=["Copper Cathodes (Cu - 99.99%)"],
                extraction_method="Open-pit extraction with sulfuric acid heap leaching and SX-EW processing",
                controlling_actor="SAC Military / Myanmar Wanbao Mining Joint Venture",
                geophysical_signature={
                    "pXRF_indicators": ["Cu > 0.6%", "Fe > 4.0%", "S > 2.5%"],
                    "geophone_hz_range": [8.0, 100.0],
                    "insar_displacement_threshold_mm_yr": 60.0
                },
                environmental_hazards=[
                    "Sulfuric acid leakage from pregnant leach solution ponds",
                    "Airborne copper dust and agricultural land degradation"
                ],
                economic_significance="Myanmar's largest industrial copper mine producing >100,000 tonnes of cathode copper annually."
            )
        }

        self.faults: Dict[str, TectonicFault] = {
            "FAULT_SAGAING": TectonicFault(
                fault_id="FAULT_SAGAING",
                name="Sagaing Fault System",
                fault_type="Right-Lateral Strike-Slip Continental Plate Boundary",
                length_km=1200.0,
                slip_rate_mm_yr=20.0,
                max_credible_magnitude=8.0,
                intersected_mining_districts=["Hpakant Jade Tract", "Mogok Metamorphic Belt", "Monywa Copper Belt"],
                seismic_hazard_rating="CRITICAL_EXTREME"
            ),
            "FAULT_KYAUKKYAN": TectonicFault(
                fault_id="FAULT_KYAUKKYAN",
                name="Kyaukkyan Fault Zone",
                fault_type="Left-Lateral Strike-Slip Intraplate Fault",
                length_km=320.0,
                slip_rate_mm_yr=3.5,
                max_credible_magnitude=7.7,
                intersected_mining_districts=["Bawdwin Lead-Zinc-Silver", "Northern Shan Plateau Mining Hubs"],
                seismic_hazard_rating="ELEVATED"
            ),
            "FAULT_KABAW": TectonicFault(
                fault_id="FAULT_KABAW",
                name="Kabaw Fault Segment",
                fault_type="Oblique Reverse Splay Fault",
                length_km=420.0,
                slip_rate_mm_yr=4.5,
                max_credible_magnitude=7.4,
                intersected_mining_districts=["Upper Chindwin Placer Gold", "Kale-Kabaw Valley"],
                seismic_hazard_rating="MODERATE_HIGH"
            )
        }

        self.multispectral_indices: Dict[str, Dict[str, Any]] = {
            "hydroxyl_clay_index": {
                "formula": "SWIR1 / SWIR2",
                "bands": ["B11", "B12"],
                "target_alterations": ["Al-OH", "Kaolinite", "Alunite", "Pyrophyllite"],
                "threshold": 1.25
            },
            "ferrous_iron_index": {
                "formula": "SWIR1 / NIR",
                "bands": ["B11", "B8A"],
                "target_alterations": ["Fe2+", "Chlorite", "Epidote", "Amphibole"],
                "threshold": 1.15
            },
            "iron_oxide_gossan_index": {
                "formula": "Red / Green",
                "bands": ["B4", "B3"],
                "target_alterations": ["Fe-Oxide", "Hematite", "Goethite", "Jarosite"],
                "threshold": 1.30
            }
        }

    def get_deposit(self, dep_id: str) -> Optional[MineralDeposit]:
        return self.deposits.get(dep_id.upper().strip())

    def list_deposits(self) -> List[MineralDeposit]:
        return list(self.deposits.values())

    def get_fault(self, fault_id: str) -> Optional[TectonicFault]:
        return self.faults.get(fault_id.upper().strip())

    def list_faults(self) -> List[TectonicFault]:
        return list(self.faults.values())

    def evaluate_spectral_alteration(self, band_reflectance: Dict[str, float]) -> Dict[str, Any]:
        """Calculates satellite multispectral mineral alteration band indices (Sentinel-2 MSI equivalent)."""
        results = {}
        for index_name, spec in self.multispectral_indices.items():
            b_num = spec["bands"]
            if b_num[0] in band_reflectance and b_num[1] in band_reflectance and band_reflectance[b_num[1]] > 0:
                val = band_reflectance[b_num[0]] / band_reflectance[b_num[1]]
                results[index_name] = {
                    "value": round(val, 3),
                    "anomalous": val >= spec["threshold"],
                    "target_alterations": spec["target_alterations"]
                }
        return results

    def evaluate_telemetry(self, pXRF: Dict[str, float], geophone_hz: float, insar_mm: float) -> Dict[str, Any]:
        """Evaluates live geophysical sensor telemetry for deposit classification and hazard triggers."""
        matched_deposits = []
        hazards = []

        for dep in self.deposits.values():
            sig = dep.geophysical_signature
            match_score = 0.0
            
            # Geophone resonance match
            if sig["geophone_hz_range"][0] <= geophone_hz <= sig["geophone_hz_range"][1]:
                match_score += 0.4
            
            # InSAR displacement rate hazard check
            if insar_mm >= sig["insar_displacement_threshold_mm_yr"]:
                hazards.append({
                    "deposit": dep.name,
                    "hazard": "CRITICAL_SLOPE_DISPLACEMENT",
                    "displacement_mm_yr": insar_mm,
                    "threshold_mm_yr": sig["insar_displacement_threshold_mm_yr"],
                    "action": "TRIGGER_MINE_EVACUATION_WARNING"
                })

            if match_score >= 0.3:
                matched_deposits.append((dep.deposit_id, dep.name, match_score))

        return {
            "matched_deposits": matched_deposits,
            "hazards_detected": hazards,
            "hazard_level": "CRITICAL" if hazards else "NORMAL"
        }


# ============================================================
# 4.9. MILITARY ARSENALS & WEAPONS SYSTEMS KNOWLEDGE BASE
# ============================================================

@dataclass
class WeaponSystem:
    weapon_id: str
    name: str
    category: str  # "SMALL_ARMS", "MACHINE_GUN", "MORTAR", "ARTILLERY", "ROCKET_MLRS", "AIRCRAFT", "ARMOR", "AIR_DEFENSE", "DRONE"
    caliber: Optional[str]
    effective_range_km: float
    origin: str  # e.g. "SAC KaPaSa (Domestic)", "China", "Russia", "KIO Technical Bureau (Domestic)", "COTS Modified"
    primary_operators: List[str]
    acoustic_signature: str
    tactical_role: str
    capture_risk_rating: str  # "LOW", "MEDIUM", "HIGH"


@dataclass
class FactionArsenal:
    faction_id: str
    faction_name: str
    estimated_manpower: str
    inventory_tier: str  # "STATE_CONVENTIONAL", "STATE_EQUIVALENT", "REGIONAL_HEAVY", "ASYMMETRIC_DRONE_INFANTRY"
    domestic_production_capacity: str
    air_superiority_capability: str
    air_defense_rating: str
    drone_warfare_rating: str
    primary_infantry_calibers: List[str]
    signature_weapons: List[str]
    foreign_supporters_or_brokers: List[str]


class MilitaryArsenalKnowledgeBase:
    def __init__(self):
        self.weapons: Dict[str, WeaponSystem] = {
            "WEAPON_MA1": WeaponSystem(
                weapon_id="WEAPON_MA1",
                name="MA-1 Mk II Assault Rifle",
                category="SMALL_ARMS",
                caliber="5.56x45mm NATO",
                effective_range_km=0.45,
                origin="SAC KaPaSa (DDI Factory Line)",
                primary_operators=["SAC (Tatmadaw)", "Resistance (Captured)"],
                acoustic_signature="Sharp, high-velocity supersonic crack, 5.56mm bore resonance (~2.2 kHz peak)",
                tactical_role="Standard issue infantry assault rifle for SAC ground forces",
                capture_risk_rating="HIGH"
            ),
            "WEAPON_MA2": WeaponSystem(
                weapon_id="WEAPON_MA2",
                name="MA-2 Light Machine Gun",
                category="MACHINE_GUN",
                caliber="5.56x45mm NATO",
                effective_range_km=0.80,
                origin="SAC KaPaSa (DDI Factory Line)",
                primary_operators=["SAC (Tatmadaw)", "Resistance (Captured)"],
                acoustic_signature="High cyclic rate (750 rpm) burst firing, 5.56mm harmonic muzzle blast",
                tactical_role="Squad-level automatic fire support",
                capture_risk_rating="HIGH"
            ),
            "WEAPON_MA15": WeaponSystem(
                weapon_id="WEAPON_MA15",
                name="MA-15 General Purpose Machine Gun",
                category="MACHINE_GUN",
                caliber="7.62x51mm NATO",
                effective_range_km=1.20,
                origin="SAC KaPaSa (MG3 Derivative)",
                primary_operators=["SAC (Tatmadaw)"],
                acoustic_signature="Deep roaring high-rate buzz saw report (1000+ rpm)",
                tactical_role="Platoon and perimeter defensive sustained fire support",
                capture_risk_rating="MEDIUM"
            ),
            "WEAPON_MA6_120MM": WeaponSystem(
                weapon_id="WEAPON_MA6_120MM",
                name="MA-6 120mm Heavy Mortar",
                category="MORTAR",
                caliber="120mm",
                effective_range_km=6.20,
                origin="SAC KaPaSa (DDI Factory Line)",
                primary_operators=["SAC (Tatmadaw)", "AA (Captured)", "3BA (Captured)"],
                acoustic_signature="Low-frequency subsonic thud (25-45 Hz) followed by 5.5s flight whistle",
                tactical_role="Battalion-level indirect high-explosive saturation bombardment",
                capture_risk_rating="HIGH"
            ),
            "WEAPON_MAM01": WeaponSystem(
                weapon_id="WEAPON_MAM01",
                name="MAM-01 122mm Multiple Launch Rocket System (MLRS)",
                category="ROCKET_MLRS",
                caliber="122mm Rocket",
                effective_range_km=20.50,
                origin="SAC KaPaSa (BM-21 / Type 81 Derivative)",
                primary_operators=["SAC (Tatmadaw)"],
                acoustic_signature="Sustained continuous whoosh and rocket exhaust roar across 40 tubes",
                tactical_role="Division-level area-denial rocket artillery barrage",
                capture_risk_rating="LOW"
            ),
            "WEAPON_SU30SME": WeaponSystem(
                weapon_id="WEAPON_SU30SME",
                name="Sukhoi Su-30SME Multi-Role Fighter",
                category="AIRCRAFT",
                caliber="30mm GSh-30-1 / FAB-500 / Thermobaric ODAB",
                effective_range_km=1500.0,
                origin="Russia (Irkut Corporation)",
                primary_operators=["SAC (Air Force)"],
                acoustic_signature="Twin AL-31FP afterburning turbofan roar (120-140 dB, supersonic shockwave)",
                tactical_role="Air superiority and long-range precision standoff aerial bombardment",
                capture_risk_rating="LOW"
            ),
            "WEAPON_YAK130": WeaponSystem(
                weapon_id="WEAPON_YAK130",
                name="Yakovlev Yak-130 Light Attack Jet",
                category="AIRCRAFT",
                caliber="23mm GSh-23L / S-8 Rockets / 250-500lb Bombs",
                effective_range_km=800.0,
                origin="Russia (Yakovlev)",
                primary_operators=["SAC (Air Force)"],
                acoustic_signature="High-pitched twin turbofan whine (85-110 dB), rapid dive-bombing profile",
                tactical_role="Primary frontline Close Air Support (CAS) and market/village bombing",
                capture_risk_rating="LOW"
            ),
            "WEAPON_MI35": WeaponSystem(
                weapon_id="WEAPON_MI35",
                name="Mil Mi-35 Hind Heavy Attack Helicopter",
                category="AIRCRAFT",
                caliber="Twin 23mm Autocannon / 80mm S-8 / Ataka ATGM",
                effective_range_km=450.0,
                origin="Russia (Rostvertol)",
                primary_operators=["SAC (Air Force)"],
                acoustic_signature="Heavy 5-blade main rotor rhythmic thumping (18-35 Hz) + turboshaft scream",
                tactical_role="Low-altitude offensive punitive strikes and troop extraction escort",
                capture_risk_rating="LOW"
            ),
            "WEAPON_BTR3U": WeaponSystem(
                weapon_id="WEAPON_BTR3U",
                name="BTR-3U Guardian 8x8 Wheeled IFV",
                category="ARMOR",
                caliber="30mm ZTM-1 Autocannon / Barrier ATGM",
                effective_range_km=600.0,
                origin="Ukraine / SAC DDI Assembly",
                primary_operators=["SAC (Tatmadaw)", "MNDAA (Captured)", "TNLA (Captured)"],
                acoustic_signature="Heavy Deutz diesel engine rumble + high-cadence 30mm staccato bursts",
                tactical_role="Mechanized infantry offensive spearhead and urban road patrol",
                capture_risk_rating="HIGH"
            ),
            "WEAPON_TYPE81": WeaponSystem(
                weapon_id="WEAPON_TYPE81",
                name="Type 81-1 Assault Rifle",
                category="SMALL_ARMS",
                caliber="7.62x39mm Soviet",
                effective_range_km=0.50,
                origin="China / Norinco",
                primary_operators=["UWSA", "MNDAA", "TNLA", "AA", "KIA"],
                acoustic_signature="Heavy, resonant 7.62x39mm report with distinctive gas-piston clatter",
                tactical_role="Dominant frontline assault rifle across northern and western EAOs",
                capture_risk_rating="MEDIUM"
            ),
            "WEAPON_QBZ95": WeaponSystem(
                weapon_id="WEAPON_QBZ95",
                name="QBZ-95 Bullpup Assault Rifle",
                category="SMALL_ARMS",
                caliber="5.8x42mm DBP87",
                effective_range_km=0.40,
                origin="China (Special Export / UWSA Supply)",
                primary_operators=["UWSA Elite Brigades"],
                acoustic_signature="High-velocity distinctive crack with rear-ejecting bullpup receiver echo",
                tactical_role="Wa Special Forces and central command guard standard rifle",
                capture_risk_rating="LOW"
            ),
            "WEAPON_K09": WeaponSystem(
                weapon_id="WEAPON_K09",
                name="K-09 Indigenous Kachin Assault Rifle",
                category="SMALL_ARMS",
                caliber="7.62x39mm Soviet",
                effective_range_km=0.45,
                origin="KIO Technical Department (Laiza Factories)",
                primary_operators=["KIA (Kachin Independence Army)", "Upper Sagaing PDFs"],
                acoustic_signature="Custom gas-block report, slightly sharper cyclic cadence than Type 81",
                tactical_role="Indigenous standard issue assault rifle ensuring Kachin ammo self-reliance",
                capture_risk_rating="MEDIUM"
            ),
            "WEAPON_TYPE90_MLRS": WeaponSystem(
                weapon_id="WEAPON_TYPE90_MLRS",
                name="Type 90 122mm 40-Tube MLRS",
                category="ROCKET_MLRS",
                caliber="122mm Rocket",
                effective_range_km=30.00,
                origin="China (Supplied to Wa Region)",
                primary_operators=["UWSA (United Wa State Army)"],
                acoustic_signature="Massed supersonic rocket screech with extended propellant exhaust plumes",
                tactical_role="Strategic deterrent artillery protecting Wa Special Region 2 borders",
                capture_risk_rating="LOW"
            ),
            "WEAPON_FN6_MANPADS": WeaponSystem(
                weapon_id="WEAPON_FN6_MANPADS",
                name="FN-6 Third-Generation Infrared MANPADS",
                category="AIR_DEFENSE",
                caliber="72mm Surface-to-Air Missile",
                effective_range_km=6.00,
                origin="China / Norinco",
                primary_operators=["UWSA", "KIA", "MNDAA", "TNLA", "AA"],
                acoustic_signature="Pyrotechnic thermal battery hiss followed by solid-propellant boost roar",
                tactical_role="Low-altitude airspace denial; responsible for shooting down SAC jets and gunships",
                capture_risk_rating="LOW"
            ),
            "WEAPON_AGRAS_HEXA_BOMBER": WeaponSystem(
                weapon_id="WEAPON_AGRAS_HEXA_BOMBER",
                name="Heavy Agricultural Hexacopter Bomber Drone",
                category="DRONE",
                caliber="4-8 x 60mm/81mm Mortar Bombs or PG-7V Shaped Charges",
                effective_range_km=8.50,
                origin="COTS Conversion (DJI Agras / EFT E410 / Custom Carbon Fiber)",
                primary_operators=["MNDAA", "TNLA", "AA", "KNDF", "PDFs"],
                acoustic_signature="Low-frequency rhythmic multi-rotor buzz (65-85 Hz) audible <400m",
                tactical_role="Precision standoff bombing of fortified SAC hilltop garrisons and ammo depots",
                capture_risk_rating="MEDIUM"
            ),
            "WEAPON_FPV_KAMIKAZE": WeaponSystem(
                weapon_id="WEAPON_FPV_KAMIKAZE",
                name="Tactical FPV Suicide Kamikaze Drone",
                category="DRONE",
                caliber="1.5-2.5 kg C4/TNT or PG-7V HEAT Warhead",
                effective_range_km=12.00,
                origin="Resistance Drone Workshops (3D-Printed / Analog 5.8GHz)",
                primary_operators=["3BA (MNDAA/TNLA/AA)", "KNDF", "Karenni Drone Force", "PDFs"],
                acoustic_signature="High-pitched screaming motor pitch (1.5-3.5 kHz) at speeds up to 140 km/h",
                tactical_role="Surgical kinetic strikes on command bunkers, artillery crews, and moving armor",
                capture_risk_rating="LOW"
            ),
            "WEAPON_FGC9": WeaponSystem(
                weapon_id="WEAPON_FGC9",
                name="FGC-9 Mk II 3D-Printed Semi-Automatic Carbine",
                category="SMALL_ARMS",
                caliber="9x19mm Parabellum",
                effective_range_km=0.10,
                origin="Decentralized PDF Workshops (Electrochemical Rifling)",
                primary_operators=["Urban Guerrillas", "Early-Stage PDFs"],
                acoustic_signature="Muffled 9mm subsonic/supersonic report with synthetic polymer receiver vibration",
                tactical_role="Asymmetric urban defense and covert ambush weapon bypassing arms blockades",
                capture_risk_rating="LOW"
            ),
            "WEAPON_M16_M4": WeaponSystem(
                weapon_id="WEAPON_M16_M4",
                name="M16A1 / M4A1 Carbine Series",
                category="SMALL_ARMS",
                caliber="5.56x45mm NATO",
                effective_range_km=0.50,
                origin="USA / Thai Border Procurement",
                primary_operators=["KNU / KNLA", "KNDF", "Southern PDFs"],
                acoustic_signature="Crisp supersonic 5.56mm report with distinct direct-impingement bolt sound",
                tactical_role="Primary frontline assault rifle for Karen and Karenni resistance forces",
                capture_risk_rating="MEDIUM"
            )
        }

        self.factions: Dict[str, FactionArsenal] = {
            "SAC": FactionArsenal(
                faction_id="SAC",
                faction_name="State Administration Council (Tatmadaw / Myanmar Military)",
                estimated_manpower="~120,000–140,000 combat effectives (declining via casualties/desertion)",
                inventory_tier="STATE_CONVENTIONAL",
                domestic_production_capacity="High (25+ specialized KaPaSa factories producing small arms, artillery, and aerial bombs)",
                air_superiority_capability="TOTAL_MONOPOLY (Fixed-wing Su-30, MiG-29, Yak-130, K-8, FTC-2000G, Mi-35 gunships)",
                air_defense_rating="HEAVY_COMPLEX (Pechora-2M, KS-1M, Tor-M1, Igla MANPADS)",
                drone_warfare_rating="MODERATE_CONVENTIONAL (CH-4 MALE strike UAVs, Orlan-10, electronic jammers)",
                primary_infantry_calibers=["5.56x45mm NATO", "7.62x51mm NATO", "12.7x108mm"],
                signature_weapons=["MA-1 Assault Rifle", "Yak-130 Attack Jet", "MAM-01 122mm MLRS", "MA-6 120mm Mortar", "Mi-35 Gunship"],
                foreign_supporters_or_brokers=["Russia (Aviation & Missiles)", "China (Fighters & APCs)", "Belarus (Air Defense Radar)"]
            ),
            "UWSA": FactionArsenal(
                faction_id="UWSA",
                faction_name="United Wa State Army (Panghsang / Special Region 2)",
                estimated_manpower="~30,000–35,000 regular troops (fully mobilized)",
                inventory_tier="STATE_EQUIVALENT",
                domestic_production_capacity="High (Indigenous ammunition plants, refurbishment depots, arms assembly)",
                air_superiority_capability="NONE (No fixed-wing combat airpower)",
                air_defense_rating="ADVANCED_MANPADS (Dense FN-6 and HN-5 coverage, 14.5mm ZPU-4 anti-aircraft batteries)",
                drone_warfare_rating="ADVANCED_RECONNAISSANCE (Medium-altitude fixed-wing ISR and commercial platforms)",
                primary_infantry_calibers=["7.62x39mm Soviet", "5.8x42mm DBP87", "12.7x108mm", "14.5x114mm"],
                signature_weapons=["Type 81-Wa Rifle", "QBZ-95", "Type 90 122mm MLRS", "FN-6 MANPADS", "HJ-8 ATGM"],
                foreign_supporters_or_brokers=["China (Defense Industrial Proximity & Cross-Border Supply Channels)"]
            ),
            "3BA": FactionArsenal(
                faction_id="3BA",
                faction_name="Three Brotherhood Alliance (MNDAA, TNLA, AA Coalition)",
                estimated_manpower="~65,000–75,000 combined combatants",
                inventory_tier="REGIONAL_HEAVY_DRONE_PIONEER",
                domestic_production_capacity="Moderate (Mobile armories, 3D printing labs, drone bomb assembly lines)",
                air_superiority_capability="ASYMMETRIC_AIR_DENIAL (Tactical drone strike dominance at altitudes <500m)",
                air_defense_rating="HIGH_MANPADS (FN-6, HN-5, heavy 12.7mm and 14.5mm truck-mounted anti-aircraft guns)",
                drone_warfare_rating="ELITE_REVOLUTIONARY (Massed synchronized hexacopter bombers and FPV kamikaze swarms)",
                primary_infantry_calibers=["7.62x39mm Soviet", "5.56x45mm NATO (Captured)", "12.7x108mm"],
                signature_weapons=["Agricultural Hexacopter Bomber", "FPV Kamikaze Drone", "Type 81-1", "Captured D-30 Howitzer", "FN-6 MANPADS"],
                foreign_supporters_or_brokers=["UWSA (Ammunition & Small Arms Brokerage)", "Commercial Global Drone Component Networks"]
            ),
            "AA": FactionArsenal(
                faction_id="AA",
                faction_name="Arakan Army (Rakhine State & Western Command)",
                estimated_manpower="~38,000–42,000 troops",
                inventory_tier="REGIONAL_HEAVY_AMPHIBIOUS",
                domestic_production_capacity="Moderate (Specialized siege mortar fabrication and naval conversion depots)",
                air_superiority_capability="NONE (Relies on strict camouflage and subterranean bunker networks)",
                air_defense_rating="HIGH_MANPADS (FN-6 MANPADS, mobile 14.5mm twin anti-aircraft technicals)",
                drone_warfare_rating="VERY_HIGH (Extensive FPV and mortar-drop drone coordination during town sieges)",
                primary_infantry_calibers=["7.62x39mm Soviet", "5.56x45mm NATO (Captured)", "12.7x108mm"],
                signature_weapons=["120mm Heavy Siege Mortars", "FN-6 MANPADS", "Captured Naval Patrol Gunboats", "Custom Long-Range Snipers"],
                foreign_supporters_or_brokers=["UWSA / KIA (Historic Training & Equipment Logistics)", "Cross-border Maritime Channels"]
            ),
            "KIA": FactionArsenal(
                faction_id="KIA",
                faction_name="Kachin Independence Army (KIO / Northern Command)",
                estimated_manpower="~18,000–22,000 troops",
                inventory_tier="REGIONAL_INDIGENOUS_MANUFACTURING",
                domestic_production_capacity="Very High (Indigenous K-09 and K-10 rifle lines, 60mm/81mm mortar factories in Laiza)",
                air_superiority_capability="NONE (Anti-aircraft ambushes over mountain valleys)",
                air_defense_rating="HIGH_MANPADS (Proven FN-6 shoot-down track record against SAC jets and helicopters)",
                drone_warfare_rating="HIGH (Dedicated drone warfare regiments conducting heavy aerial bombing)",
                primary_infantry_calibers=["7.62x39mm Soviet", "12.7x108mm", "14.5x114mm"],
                signature_weapons=["K-09 Indigenous Rifle", "K-10 Carbine", "Indigenous 81mm Mortar", "FN-6 MANPADS", "ZPU-2 AAA"],
                foreign_supporters_or_brokers=["Cross-border Yunnan illicit commercial channels", "Allied EAO Technology Sharing"]
            ),
            "KNU_PDF": FactionArsenal(
                faction_id="KNU_PDF",
                faction_name="KNU / KNLA, KNDF, and Allied People's Defence Forces (Southern & Eastern Front)",
                estimated_manpower="~40,000–55,000 guerrilla fighters and PDF brigade troops",
                inventory_tier="ASYMMETRIC_DRONE_INFANTRY",
                domestic_production_capacity="Dispersed (Underground 3D-printing workshops, improvised mortar fabrication, FPV assembly)",
                air_superiority_capability="NONE (Extreme vulnerability to SAC standoff aerial strikes)",
                air_defense_rating="LOW_TO_MODERATE (Limited MANPADS, reliance on 12.7mm and small arms fire against low-flying aircraft)",
                drone_warfare_rating="ELITE_INNOVATIVE (Pioneered rapid FPV kamikaze strikes and 3D-printed impact fuzes)",
                primary_infantry_calibers=["5.56x45mm NATO", "7.62x39mm Soviet", "9x19mm Parabellum (FGC-9)"],
                signature_weapons=["M16A1 / M4A1", "FPV Kamikaze Drone", "FGC-9 3D-Printed Carbine", "Captured MA-1", "Improvised 60mm Mortars"],
                foreign_supporters_or_brokers=["Thai Border Black Market", "Global Myanmar Diaspora Crowdfunding"]
            )
        }

    def get_weapon(self, weapon_id: str) -> Optional[WeaponSystem]:
        return self.weapons.get(weapon_id.upper().strip())

    def list_weapons(self, category: Optional[str] = None) -> List[WeaponSystem]:
        if not category:
            return list(self.weapons.values())
        return [w for w in self.weapons.values() if w.category.upper() == category.upper()]

    def get_faction_arsenal(self, faction_id: str) -> Optional[FactionArsenal]:
        return self.factions.get(faction_id.upper().strip())

    def list_faction_arsenals(self) -> List[FactionArsenal]:
        return list(self.factions.values())

    def match_weapons_by_caliber(self, caliber: str) -> List[WeaponSystem]:
        """Matches all weapon systems that utilize the specified ammunition caliber."""
        cal_clean = caliber.lower().strip()
        matched = []
        for w in self.weapons.values():
            if w.caliber and cal_clean in w.caliber.lower():
                matched.append(w)
        return matched

    def compare_arsenals(self, faction_a_id: str, faction_b_id: str) -> Dict[str, Any]:
        """Performs a comprehensive side-by-side military hardware and doctrine comparison."""
        f_a = self.get_faction_arsenal(faction_a_id)
        f_b = self.get_faction_arsenal(faction_b_id)

        if not f_a or not f_b:
            return {"error": f"One or both faction IDs ({faction_a_id}, {faction_b_id}) not found."}

        weapons_a = [w for w in self.weapons.values() if any(f_a.faction_id in op for op in w.primary_operators)]
        weapons_b = [w for w in self.weapons.values() if any(f_b.faction_id in op for op in w.primary_operators)]

        # Asymmetric balance assessment
        air_monopoly = (f_a.air_superiority_capability == "TOTAL_MONOPOLY" or f_b.air_superiority_capability == "TOTAL_MONOPOLY")
        drone_advantage = f_a.faction_id if "ELITE" in f_a.drone_warfare_rating else (f_b.faction_id if "ELITE" in f_b.drone_warfare_rating else "BALANCED")

        return {
            "comparison": f"{f_a.faction_name} vs. {f_b.faction_name}",
            "faction_a": {
                "id": f_a.faction_id,
                "tier": f_a.inventory_tier,
                "manpower": f_a.estimated_manpower,
                "air_superiority": f_a.air_superiority_capability,
                "air_defense": f_a.air_defense_rating,
                "drone_rating": f_a.drone_warfare_rating,
                "domestic_capacity": f_a.domestic_production_capacity,
                "signature_weapons": f_a.signature_weapons,
                "weapons_cataloged_count": len(weapons_a)
            },
            "faction_b": {
                "id": f_b.faction_id,
                "tier": f_b.inventory_tier,
                "manpower": f_b.estimated_manpower,
                "air_superiority": f_b.air_superiority_capability,
                "air_defense": f_b.air_defense_rating,
                "drone_rating": f_b.drone_warfare_rating,
                "domestic_capacity": f_b.domestic_production_capacity,
                "signature_weapons": f_b.signature_weapons,
                "weapons_cataloged_count": len(weapons_b)
            },
            "asymmetric_dynamics": {
                "air_superiority_monopoly": air_monopoly,
                "drone_tactical_edge": drone_advantage,
                "caliber_capture_compatibility": "5.56x45mm NATO ammunition captured from SAC KaPaSa is instantly usable by KNU/PDFs, while Northern EAOs rely primarily on 7.62x39mm supply channels."
            }
        }


# ============================================================
# 4.10. SAC AIRCRAFT FLEET & AERIAL COMBAT KNOWLEDGE BASE
# ============================================================

@dataclass
class SACAircraftProfile:
    model_id: str
    common_name: str
    nato_reporting_name: Optional[str]
    category: str  # "AIR_SUPERIORITY_FIGHTER", "LIGHT_ATTACK_TRAINER", "ATTACK_HELICOPTER", "TRANSPORT_HELICOPTER", "TRANSPORT_IMPROVISED_BOMBER", "STRIKE_UAV"
    origin_country: str
    manufacturer: str
    active_fleet_count: int
    engines: str
    max_speed_kmh: float
    service_ceiling_m: float
    combat_radius_km: float
    hardpoints_count: int
    max_ordnance_kg: float
    typical_strike_weapons: List[str]
    primary_airbases: List[str]
    acoustic_signature_profile: Dict[str, Any]
    tactical_role_description: str
    known_losses: int


@dataclass
class AirbaseFacility:
    base_id: str
    name: str
    region_state: str
    coordinates: Tuple[float, float]
    runways_m: List[float]
    assigned_aircraft: List[str]
    strategic_strike_coverage: List[str]
    fortification_status: str


@dataclass
class AirAttritionRecord:
    loss_id: str
    date: str
    aircraft_type: str
    tail_or_serial: Optional[str]
    location_sector: str
    state_region: str
    weapon_employed: str
    downing_actor: str
    casualty_details: str
    tactical_significance: str


class SACAircraftFleetKnowledgeBase:
    def __init__(self):
        self.aircraft: Dict[str, SACAircraftProfile] = {
            "SU-30SME": SACAircraftProfile(
                model_id="SU-30SME",
                common_name="Sukhoi Su-30SME Multi-Role Fighter",
                nato_reporting_name="Flanker-H",
                category="AIR_SUPERIORITY_FIGHTER",
                origin_country="Russian Federation",
                manufacturer="Irkut Corporation",
                active_fleet_count=6,
                engines="2 × Saturn AL-31FP afterburning turbofans with 2D thrust vectoring",
                max_speed_kmh=2120.0,
                service_ceiling_m=17300.0,
                combat_radius_km=1500.0,
                hardpoints_count=12,
                max_ordnance_kg=8000.0,
                typical_strike_weapons=["FAB-500", "ODAB-500PM Thermobaric", "KAB-500Kr", "Kh-29T", "R-77 BVR"],
                primary_airbases=["Naypyidaw (Ela)", "Tada-U (Mandalay)"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [40.0, 120.0],
                    "compressor_whine_hz": [2500.0, 6000.0],
                    "db_range": [120.0, 140.0],
                    "doppler_shift_hz": [-320.0, 320.0]
                },
                tactical_role_description="High-altitude strategic standoff strikes, thermobaric mass-casualty village bombings, and nationwide strategic deterrence.",
                known_losses=0
            ),
            "MIG-29": SACAircraftProfile(
                model_id="MIG-29",
                common_name="Mikoyan MiG-29B/SE/UB Fighter",
                nato_reporting_name="Fulcrum",
                category="AIR_SUPERIORITY_FIGHTER",
                origin_country="Russian Federation",
                manufacturer="RAC MiG",
                active_fleet_count=26,
                engines="2 × Klimov RD-33 turbofans",
                max_speed_kmh=2400.0,
                service_ceiling_m=18000.0,
                combat_radius_km=700.0,
                hardpoints_count=7,
                max_ordnance_kg=4000.0,
                typical_strike_weapons=["FAB-250", "FAB-500", "B-8M1 (80mm S-8)", "R-73 dogfight AAM", "R-27R"],
                primary_airbases=["Tada-U (Mandalay)", "Magway Airbase", "Yangon-Mingaladon"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [80.0, 220.0],
                    "compressor_whine_hz": [3000.0, 7500.0],
                    "db_range": [115.0, 135.0],
                    "doppler_shift_hz": [-280.0, 280.0]
                },
                tactical_role_description="Rapid-reaction point air defense interceptor and medium-altitude high-speed dive-bombing strike platform.",
                known_losses=1
            ),
            "JF-17M": SACAircraftProfile(
                model_id="JF-17M",
                common_name="PAC / Chengdu JF-17M Thunder Block II",
                nato_reporting_name=None,
                category="AIR_SUPERIORITY_FIGHTER",
                origin_country="Pakistan & China",
                manufacturer="Pakistan Aeronautical Complex / Chengdu",
                active_fleet_count=7,
                engines="1 × Klimov RD-93 turbofan",
                max_speed_kmh=1960.0,
                service_ceiling_m=16900.0,
                combat_radius_km=900.0,
                hardpoints_count=7,
                max_ordnance_kg=3400.0,
                typical_strike_weapons=["Unguided gravity bombs", "Type 57 rocket pods", "PL-5E AAM"],
                primary_airbases=["Meiktila (Shante)", "Magway Airbase"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [100.0, 250.0],
                    "compressor_whine_hz": [2800.0, 6500.0],
                    "db_range": [110.0, 130.0],
                    "doppler_shift_hz": [-220.0, 220.0]
                },
                tactical_role_description="Multi-role fighter severely constrained by airframe vibration cracks, radar integration faults, and sanctions on manufacturer spares.",
                known_losses=0
            ),
            "YAK-130": SACAircraftProfile(
                model_id="YAK-130",
                common_name="Yakovlev Yak-130 Light Attack Jet",
                nato_reporting_name="Mitten",
                category="LIGHT_ATTACK_TRAINER",
                origin_country="Russian Federation",
                manufacturer="Irkut Corporation",
                active_fleet_count=19,
                engines="2 × Ivchenko-Progress AI-222-25 turbofans",
                max_speed_kmh=1060.0,
                service_ceiling_m=12500.0,
                combat_radius_km=555.0,
                hardpoints_count=9,
                max_ordnance_kg=3000.0,
                typical_strike_weapons=["Twin 23mm GSh-23L gun pod", "B-8M1 (80mm S-8)", "250-lb Bombs", "500-lb Bombs", "Thermobaric submunitions"],
                primary_airbases=["Tada-U (Mandalay)", "Taungoo Airbase", "Meiktila"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [120.0, 450.0],
                    "compressor_whine_hz": [1200.0, 4500.0],
                    "db_range": [85.0, 110.0],
                    "doppler_shift_hz": [-220.0, 220.0]
                },
                tactical_role_description="Single most heavily flown Close Air Support (CAS) attack aircraft in Myanmar, responsible for dense strikes in Sagaing, Karenni, and Kachin.",
                known_losses=1
            ),
            "FTC-2000G": SACAircraftProfile(
                model_id="FTC-2000G",
                common_name="Guizhou FTC-2000G Mountain Eagle",
                nato_reporting_name=None,
                category="LIGHT_ATTACK_TRAINER",
                origin_country="People's Republic of China",
                manufacturer="Guizhou Aviation Industry Import/Export Company (GAIEC)",
                active_fleet_count=11,
                engines="1 × Guizhou Liyang WP-13F turbojet with afterburner",
                max_speed_kmh=1700.0,
                service_ceiling_m=15000.0,
                combat_radius_km=800.0,
                hardpoints_count=7,
                max_ordnance_kg=2000.0,
                typical_strike_weapons=["23mm Type 23-1 gun", "250kg bombs", "57mm/90mm rocket pods", "PL-8/PL-9 AAM"],
                primary_airbases=["Namsang (Eastern Shan)", "Taungoo Airbase"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [300.0, 850.0],
                    "compressor_whine_hz": [1800.0, 5500.0],
                    "db_range": [105.0, 125.0],
                    "doppler_shift_hz": [-260.0, 260.0]
                },
                tactical_role_description="Supersonic strike fighter utilized extensively during Operation 1027 in Northern and Southern Shan State.",
                known_losses=1
            ),
            "K-8W": SACAircraftProfile(
                model_id="K-8W",
                common_name="Hongdu / PAC K-8W Karakorum",
                nato_reporting_name=None,
                category="LIGHT_ATTACK_TRAINER",
                origin_country="China & Pakistan (Domestic Assembly at Meiktila)",
                manufacturer="Hongdu Aviation / Meiktila Aircraft Depot",
                active_fleet_count=46,
                engines="1 × Garrett TFE731-2A-2A turbofan",
                max_speed_kmh=800.0,
                service_ceiling_m=13000.0,
                combat_radius_km=400.0,
                hardpoints_count=5,
                max_ordnance_kg=1000.0,
                typical_strike_weapons=["23mm belly gun pod", "Type 57-1 (57mm rockets)", "100-lb / 250-lb unguided bombs"],
                primary_airbases=["Meiktila (Shante)", "Magway", "Taungoo", "Namsang", "Myitkyina"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [150.0, 600.0],
                    "compressor_whine_hz": [1500.0, 4000.0],
                    "db_range": [80.0, 105.0],
                    "doppler_shift_hz": [-160.0, 160.0]
                },
                tactical_role_description="Numerical backbone of SAC ground-attack operations nationwide; low operating cost, rapid turnaround, and domestic assembly at Meiktila.",
                known_losses=3
            ),
            "PC-7_PC-9": SACAircraftProfile(
                model_id="PC-7_PC-9",
                common_name="Pilatus PC-7 / PC-9 Turboprop Trainer/Strike",
                nato_reporting_name=None,
                category="LIGHT_ATTACK_TRAINER",
                origin_country="Switzerland & Austria",
                manufacturer="Pilatus Aircraft",
                active_fleet_count=14,
                engines="1 × Pratt & Whitney Canada PT6A-25A/62 turboprop",
                max_speed_kmh=550.0,
                service_ceiling_m=11500.0,
                combat_radius_km=350.0,
                hardpoints_count=4,
                max_ordnance_kg=1040.0,
                typical_strike_weapons=["7.62mm / 12.7mm gun pods", "68mm Matra unguided rocket pods"],
                primary_airbases=["Meiktila (Shante)", "Magway"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [65.0, 180.0],
                    "compressor_whine_hz": [800.0, 2200.0],
                    "db_range": [75.0, 95.0],
                    "doppler_shift_hz": [-90.0, 90.0]
                },
                tactical_role_description="Light visual reconnaissance, forward air control, and low-altitude daytime strafing runs against rural outposts.",
                known_losses=1
            ),
            "MI-35P": SACAircraftProfile(
                model_id="MI-35P",
                common_name="Mil Mi-35P / Mi-35M Hind Heavy Attack Helicopter",
                nato_reporting_name="Hind-E",
                category="ATTACK_HELICOPTER",
                origin_country="Russian Federation",
                manufacturer="Rostvertol",
                active_fleet_count=13,
                engines="2 × Isotov TV3-117VMA turboshafts",
                max_speed_kmh=310.0,
                service_ceiling_m=4500.0,
                combat_radius_km=450.0,
                hardpoints_count=4,
                max_ordnance_kg=1500.0,
                typical_strike_weapons=["Twin 30mm GSh-30K autocannon", "B-8M1 (80 × S-8 rockets)", "9M120 Ataka ATGM"],
                primary_airbases=["Meiktila", "Tada-U", "Myitkyina", "Taungoo", "Hmawbi"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [18.5, 22.0],  # 5-blade main rotor BPF
                    "compressor_whine_hz": [1100.0, 2800.0],
                    "db_range": [88.0, 118.0],
                    "doppler_shift_hz": [-45.0, 45.0]
                },
                tactical_role_description="Dedicated heavy armor-plated assault gunship deployed for low-altitude close-in strafing, bunker busting, and village clearance.",
                known_losses=3
            ),
            "MI-17": SACAircraftProfile(
                model_id="MI-17",
                common_name="Mil Mi-17 / Mi-8 Hip Transport & Assault Helicopter",
                nato_reporting_name="Hip-H",
                category="TRANSPORT_HELICOPTER",
                origin_country="Russian Federation",
                manufacturer="Kazan Helicopters / Ulan-Ude",
                active_fleet_count=22,
                engines="2 × Klimov TV3-117MT turboshafts",
                max_speed_kmh=250.0,
                service_ceiling_m=6000.0,
                combat_radius_km=465.0,
                hardpoints_count=6,
                max_ordnance_kg=1500.0,
                typical_strike_weapons=["Outrigger UB-32 / B-8M1 rocket pods", "Door-mounted PKM / 12.7mm machine guns"],
                primary_airbases=["Meiktila", "Tada-U", "Taungoo", "Namsang", "Hmawbi"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [19.2, 23.0],
                    "compressor_whine_hz": [950.0, 2400.0],
                    "db_range": [85.0, 112.0],
                    "doppler_shift_hz": [-40.0, 40.0]
                },
                tactical_role_description="Essential lifeline for isolated junta hilltop cantonments; executes combat troop insertions, ammunition resupply, and wounded evacuation.",
                known_losses=2
            ),
            "AS365_Z9": SACAircraftProfile(
                model_id="AS365_Z9",
                common_name="Eurocopter AS365 Dauphin / Harbin Z-9",
                nato_reporting_name="Haitun",
                category="TRANSPORT_HELICOPTER",
                origin_country="France & China",
                manufacturer="Airbus Helicopters / Harbin Aircraft",
                active_fleet_count=10,
                engines="2 × Turbomeca Arriel 1M1 / 2C turboshafts",
                max_speed_kmh=287.0,
                service_ceiling_m=5865.0,
                combat_radius_km=400.0,
                hardpoints_count=2,
                max_ordnance_kg=500.0,
                typical_strike_weapons=["Door guns", "VIP transport pods", "Artillery observation gear"],
                primary_airbases=["Naypyidaw (Ela)", "Hmawbi", "Meiktila"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [23.0, 28.0],
                    "compressor_whine_hz": [1400.0, 3200.0],
                    "db_range": [78.0, 98.0],
                    "doppler_shift_hz": [-35.0, 35.0]
                },
                tactical_role_description="Command and staff VIP transit, forward artillery target designation, and rapid courier operations.",
                known_losses=1
            ),
            "Y-12": SACAircraftProfile(
                model_id="Y-12",
                common_name="Shaanxi Y-12 II/IV Light STOL Transport",
                nato_reporting_name=None,
                category="TRANSPORT_IMPROVISED_BOMBER",
                origin_country="People's Republic of China",
                manufacturer="Harbin Aircraft Industry Group",
                active_fleet_count=9,
                engines="2 × Pratt & Whitney Canada PT6A-27 turboprops",
                max_speed_kmh=292.0,
                service_ceiling_m=7000.0,
                combat_radius_km=600.0,
                hardpoints_count=0,
                max_ordnance_kg=1700.0,
                typical_strike_weapons=["Rear-ramp pushed unguided 50-kg mortar bomb arrays ('barrel bombs')"],
                primary_airbases=["Meiktila", "Magway", "Mandalay", "Naypyidaw"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [45.0, 110.0],
                    "compressor_whine_hz": [600.0, 1800.0],
                    "db_range": [72.0, 90.0],
                    "doppler_shift_hz": [-45.0, 45.0]
                },
                tactical_role_description="High-altitude improvised indiscriminate gravity bombing of civilian villages from beyond MANPADS reach, alongside utility transport.",
                known_losses=0
            ),
            "Y-8_Y-9": SACAircraftProfile(
                model_id="Y-8_Y-9",
                common_name="Shaanxi Y-8 / Y-9 Heavy Military Transport",
                nato_reporting_name=None,
                category="TRANSPORT_IMPROVISED_BOMBER",
                origin_country="People's Republic of China",
                manufacturer="Shaanxi Aircraft Corporation",
                active_fleet_count=5,
                engines="4 × Zhuzhou WoJiang-6 (WJ-6) turboprops",
                max_speed_kmh=660.0,
                service_ceiling_m=10400.0,
                combat_radius_km=1800.0,
                hardpoints_count=0,
                max_ordnance_kg=20000.0,
                typical_strike_weapons=["Troop airlift (96 soldiers)", "Heavy cargo drops"],
                primary_airbases=["Naypyidaw (Ela)", "Yangon-Mingaladon"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [30.0, 85.0],
                    "compressor_whine_hz": [450.0, 1500.0],
                    "db_range": [82.0, 102.0],
                    "doppler_shift_hz": [-75.0, 75.0]
                },
                tactical_role_description="Strategic heavy inter-theater logistics pipeline transferring munitions and reserves between Naypyidaw and regional command bastions.",
                known_losses=1
            ),
            "CH-4B": SACAircraftProfile(
                model_id="CH-4B",
                common_name="CASC Rainbow CH-4B MALE Strike UAV",
                nato_reporting_name=None,
                category="STRIKE_UAV",
                origin_country="People's Republic of China",
                manufacturer="China Aerospace Science and Technology Corporation (CASC)",
                active_fleet_count=5,
                engines="1 × Rotax 914 turbocharged piston engine (pusher prop)",
                max_speed_kmh=235.0,
                service_ceiling_m=7200.0,
                combat_radius_km=1500.0,
                hardpoints_count=4,
                max_ordnance_kg=345.0,
                typical_strike_weapons=["AR-1 laser-guided missiles", "FT-9 50kg satellite glide bombs"],
                primary_airbases=["Meiktila (Shante)", "Magway Airbase"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [85.0, 130.0],
                    "compressor_whine_hz": [350.0, 900.0],
                    "db_range": [45.0, 65.0],
                    "doppler_shift_hz": [-15.0, 15.0]
                },
                tactical_role_description="Persistent high-altitude standoff surveillance and precision guided missile strikes out of range of MANPADS air defense.",
                known_losses=0
            ),
            "ORLAN-10": SACAircraftProfile(
                model_id="ORLAN-10",
                common_name="Special Technology Center Orlan-10 Tactical Recon UAV",
                nato_reporting_name=None,
                category="STRIKE_UAV",
                origin_country="Russian Federation",
                manufacturer="Special Technology Center (STC)",
                active_fleet_count=12,
                engines="1 × Piston engine (gasoline/kerosene)",
                max_speed_kmh=150.0,
                service_ceiling_m=5000.0,
                combat_radius_km=120.0,
                hardpoints_count=0,
                max_ordnance_kg=5.0,
                typical_strike_weapons=["Stabilized daylight/thermal camera payload", "Artillery laser target designator"],
                primary_airbases=["Magway", "Tada-U", "Meiktila"],
                acoustic_signature_profile={
                    "fundamental_hz_range": [90.0, 160.0],
                    "compressor_whine_hz": [200.0, 600.0],
                    "db_range": [40.0, 60.0],
                    "doppler_shift_hz": [-10.0, 10.0]
                },
                tactical_role_description="Catapult-launched tactical ISR drone spotting targets for SAC heavy artillery and coordinating jet airstrikes.",
                known_losses=2
            )
        }

        self.airbases: Dict[str, AirbaseFacility] = {
            "AIRBASE_ELA": AirbaseFacility(
                base_id="AIRBASE_ELA",
                name="Naypyidaw (Ela) Air Base",
                region_state="Naypyidaw Union Territory",
                coordinates=(19.778, 96.121),
                runways_m=[3658.0],
                assigned_aircraft=["SU-30SME", "Y-8_Y-9", "AS365_Z9", "VIP Fleet"],
                strategic_strike_coverage=["Capital Defense", "Southern Shan", "Bago Yoma", "Nationwide Strategic Sorties"],
                fortification_status="Heavily fortified central military citadel with hardened underground hangars; periodic resistance 107mm rocket harassment."
            ),
            "AIRBASE_TADAU": AirbaseFacility(
                base_id="AIRBASE_TADAU",
                name="Tada-U (Mandalay International / Central Command Air Base)",
                region_state="Mandalay Region",
                coordinates=(21.701, 95.975),
                runways_m=[4268.0],
                assigned_aircraft=["SU-30SME", "MIG-29", "YAK-130", "MI-35P"],
                strategic_strike_coverage=["Sagaing Region", "Northern Shan", "Kachin State", "Central Dry Zone"],
                fortification_status="Primary combat strike headquarters for Upper and Central Myanmar; dense perimeter rings and radar installations."
            ),
            "AIRBASE_MAGWAY": AirbaseFacility(
                base_id="AIRBASE_MAGWAY",
                name="Magway Air Base",
                region_state="Magway Region",
                coordinates=(20.155, 94.933),
                runways_m=[2743.0],
                assigned_aircraft=["MIG-29", "K-8W", "CH-4B", "ORLAN-10"],
                strategic_strike_coverage=["Magway Region", "Chin State", "Rakhine Border", "Yaw Region"],
                fortification_status="Major combat training and strike hub frequently targeted by PDF standoff mortar barrages."
            ),
            "AIRBASE_TAUNGOO": AirbaseFacility(
                base_id="AIRBASE_TAUNGOO",
                name="Taungoo (Ketu) Air Base",
                region_state="Bago Region",
                coordinates=(18.925, 96.401),
                runways_m=[2743.0],
                assigned_aircraft=["YAK-130", "FTC-2000G", "K-8W", "MI-35P", "MI-17"],
                strategic_strike_coverage=["Kayah (Karenni) State", "Kayin (Karen) State", "Mon State", "Southern Bago"],
                fortification_status="Critical frontline fighter-bomber launchpad directly supporting SAC defense against Karen and Karenni resistance forces."
            ),
            "AIRBASE_MEIKTILA": AirbaseFacility(
                base_id="AIRBASE_MEIKTILA",
                name="Meiktila (Shante) Air Base",
                region_state="Mandalay Region",
                coordinates=(20.883, 95.832),
                runways_m=[3048.0, 2438.0],
                assigned_aircraft=["K-8W (Assembly Lines)", "YAK-130", "MI-35P", "CH-4B", "Y-12"],
                strategic_strike_coverage=["Central logistics", "Maintenance airlift", "Central Dry Zone"],
                fortification_status="Core industrial aviation hub housing the Aircraft Production & Maintenance Depot; central pilot academy."
            ),
            "AIRBASE_NAMSANG": AirbaseFacility(
                base_id="AIRBASE_NAMSANG",
                name="Namsang Air Base",
                region_state="Shan State (East-Central)",
                coordinates=(20.890, 97.740),
                runways_m=[2500.0],
                assigned_aircraft=["FTC-2000G", "K-8W", "MI-17"],
                strategic_strike_coverage=["Northern Shan", "Southern Shan", "Wa Special Region 2", "Salween River Corridor"],
                fortification_status="Forward advanced combat base anchoring SAC strikes against Operation 1027 coalitions."
            ),
            "AIRBASE_MYITKYINA": AirbaseFacility(
                base_id="AIRBASE_MYITKYINA",
                name="Myitkyina (Pamati) Air Base",
                region_state="Kachin State",
                coordinates=(25.383, 97.350),
                runways_m=[2134.0],
                assigned_aircraft=["MI-35P", "K-8W", "YAK-130 (Detached)"],
                strategic_strike_coverage=["Kachin State (Laiza, Bhamo, Hpakant)", "Upper Sagaing (Indaw, Banmauk)"],
                fortification_status="Encircled northern bastion vulnerable to KIA standoff sniper and mortar observation."
            ),
            "AIRBASE_HMAWBI": AirbaseFacility(
                base_id="AIRBASE_HMAWBI",
                name="Hmawbi Air Base",
                region_state="Yangon Region",
                coordinates=(17.112, 96.061),
                runways_m=[2743.0],
                assigned_aircraft=["MIG-29", "MI-17", "MI-35P", "Naval Helicopters"],
                strategic_strike_coverage=["Ayeyarwady Delta", "Tanintharyi Coast", "Yangon Defense Ring"],
                fortification_status="Southern Air Command base and primary helicopter heavy maintenance facility."
            )
        }

        self.attrition_records: List[AirAttritionRecord] = [
            AirAttritionRecord(
                loss_id="LOSS_20240116_FTC2000G",
                date="2024-01-16",
                aircraft_type="FTC-2000G Mountain Eagle",
                tail_or_serial="FTC-2000G #602",
                location_sector="Kutkai Township, Northern Shan State",
                state_region="Shan State",
                weapon_employed="FN-6 Infrared Homing MANPADS",
                downing_actor="Kachin Independence Army (KIA / KIO)",
                casualty_details="Pilot ejected over resistance territory; captured/confirmed KIA.",
                tactical_significance="First confirmed combat loss of China's newly exported supersonic FTC-2000G fighter jet worldwide."
            ),
            AirAttritionRecord(
                loss_id="LOSS_20231111_K8W",
                date="2023-11-11",
                aircraft_type="K-8W Karakorum",
                tail_or_serial="K-8W #3212",
                location_sector="Demoso Township, Karenni State",
                state_region="Kayah (Karenni) State",
                weapon_employed="12.7mm Heavy Machine Gun / MANPADS crossfire",
                downing_actor="Karenni Nationalities Defence Force (KNDF) & Karenni Army",
                casualty_details="Two pilots ejected; Pilot Major and Co-pilot captured by KNDF.",
                tactical_significance="Severely degraded SAC close air support during Operation 1111 surrounding Loikaw capital."
            ),
            AirAttritionRecord(
                loss_id="LOSS_20240103_MI17",
                date="2024-01-03",
                aircraft_type="Mil Mi-17 Transport/Gunship",
                tail_or_serial="Mi-17 #4408",
                location_sector="Momauk Township, Kachin State",
                state_region="Kachin State",
                weapon_employed="FN-6 MANPADS",
                downing_actor="Kachin Independence Army (KIA)",
                casualty_details="All 6 personnel on board killed, including senior Light Infantry Battalion commander.",
                tactical_significance="Crippled junta emergency aerial resupply to besieged hilltop outposts guarding Bhamo corridor."
            ),
            AirAttritionRecord(
                loss_id="LOSS_20240116_MI35P",
                date="2024-01-16",
                aircraft_type="Mil Mi-35P Attack Helicopter",
                tail_or_serial="Mi-35P #2214",
                location_sector="Waingmaw Township, Kachin State",
                state_region="Kachin State",
                weapon_employed="FN-6 MANPADS",
                downing_actor="Kachin Independence Army (KIA)",
                casualty_details="Helicopter impacted mountain slope and exploded; crew killed on impact.",
                tactical_significance="Neutralized key close air support asset directly defending junta artillery bases outside Laiza."
            ),
            AirAttritionRecord(
                loss_id="LOSS_20240129_AS365",
                date="2024-01-29",
                aircraft_type="Eurocopter AS365 Dauphin (VIP)",
                tail_or_serial="AS365 #1105",
                location_sector="Thingannyinaung, Karen State (near Myawaddy)",
                state_region="Kayin State",
                weapon_employed="Coordinated 12.7mm HMG Concentrated Anti-Air Volley",
                downing_actor="Karen National Liberation Army (KNLA / KNU)",
                casualty_details="Brigadier General and key logistics officers killed in crash.",
                tactical_significance="Decapitated junta command structure managing the defense of Asian Highway 1 trade gateway."
            ),
            AirAttritionRecord(
                loss_id="LOSS_20240628_K8W",
                date="2024-06-28",
                aircraft_type="K-8W Karakorum",
                tail_or_serial="K-8W #3220",
                location_sector="Upper Sagaing Frontier",
                state_region="Sagaing Region",
                weapon_employed="Coordinated Anti-Air Ambush (12.7mm / Small Arms)",
                downing_actor="Joint People's Defence Forces (PDFs)",
                casualty_details="Aircraft crashed into rural scrubland; pilot ejected.",
                tactical_significance="Demonstrated vulnerability of low-altitude K-8 diving attacks to massed ground fire in rural dry zones."
            )
        ]

    def get_aircraft(self, model_id: str) -> Optional[SACAircraftProfile]:
        return self.aircraft.get(model_id.upper().strip())

    def list_aircraft(self, category: Optional[str] = None) -> List[SACAircraftProfile]:
        if not category:
            return list(self.aircraft.values())
        return [a for a in self.aircraft.values() if a.category.upper() == category.upper()]

    def get_airbase(self, base_id: str) -> Optional[AirbaseFacility]:
        return self.airbases.get(base_id.upper().strip())

    def list_airbases(self) -> List[AirbaseFacility]:
        return list(self.airbases.values())

    def list_attrition(self) -> List[AirAttritionRecord]:
        return list(self.attrition_records)

    def evaluate_acoustic_detection(self, freq_hz: float, db_level: float, doppler_hz: float) -> List[Tuple[str, float]]:
        """
        Matches real-time acoustic edge telemetry against the SAC aircraft model signature database.
        Returns candidate aircraft matches scored by acoustic correlation confidence (0.0 to 1.0).
        """
        matches = []
        for model in self.aircraft.values():
            sig = model.acoustic_signature_profile
            score = 0.0

            # Frequency match check
            f_min, f_max = sig["fundamental_hz_range"]
            c_min, c_max = sig["compressor_whine_hz"]
            if f_min <= freq_hz <= f_max:
                score += 0.45
            elif c_min <= freq_hz <= c_max:
                score += 0.35

            # Decibel level check
            d_min, d_max = sig["db_range"]
            if d_min <= db_level <= d_max + 10.0:
                score += 0.25

            # Doppler shift correlation
            dp_min, dp_max = sig["doppler_shift_hz"]
            if dp_min <= doppler_hz <= dp_max and doppler_hz != 0.0:
                score += 0.30

            if score >= 0.40:
                matches.append((model.model_id, round(min(score, 0.99), 2)))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def calculate_warning_time_seconds(self, model_id: str, sensor_distance_km: float) -> float:
        """
        Calculates available civilian warning window (in seconds) from acoustic sensor detection
        until aircraft reaches the ground target.
        """
        ac = self.get_aircraft(model_id)
        if not ac:
            return 60.0  # Conservative fallback
        speed_mps = (ac.max_speed_kmh * 0.80) / 3.6  # Assume 80% throttle cruising attack speed
        distance_m = sensor_distance_km * 1000.0
        return round(distance_m / max(speed_mps, 50.0), 1)


# ============================================================
# 4.11. WEATHER FORECASTING & METEOROLOGICAL TELEMETRY KNOWLEDGE BASE
# ============================================================

@dataclass
class ClimateZone:
    zone_id: str
    name: str
    geographical_scope: str
    annual_rainfall_mm: Tuple[float, float]
    monsoon_months: List[str]
    peak_cyclone_months: List[str]
    air_operations_impact: str
    drone_operations_impact: str
    typical_environmental_hazards: List[str]


class AtmosphericAcousticModel:
    @staticmethod
    def speed_of_sound_ms(temperature_c: float) -> float:
        """Returns speed of sound in air (m/s) as a function of temperature."""
        import math
        return round(331.3 * math.sqrt(1.0 + (temperature_c / 273.15)), 2)

    @staticmethod
    def acoustic_attenuation_db_km(frequency_hz: float, relative_humidity_pct: float) -> float:
        """Approximates atmospheric sound absorption coefficient (dB/km)."""
        if frequency_hz <= 100.0:
            return 0.3
        elif frequency_hz <= 500.0:
            return 1.2
        elif frequency_hz <= 1500.0:
            return 4.5
        elif frequency_hz <= 4000.0:
            hum_factor = 1.0 + (relative_humidity_pct / 100.0) * 0.5
            return round(18.0 * hum_factor, 1)
        else:
            hum_factor = 1.0 + (relative_humidity_pct / 100.0) * 0.8
            return round(45.0 * hum_factor, 1)


@dataclass
class TacticalFlightConditions:
    fpv_drone_status: str       # "GO", "MARGINAL", "GROUNDED"
    hexacopter_status: str      # "GO", "MARGINAL", "GROUNDED"
    cas_jet_strike_status: str  # "UNRESTRICTED", "CONSTRAINED_STANDOFF", "GROUNDED"
    helicopter_status: str      # "GO", "HIGH_TURBULENCE_RISK", "GROUNDED"
    critical_limitations: List[str]


class WeatherKnowledgeBase:
    def __init__(self):
        self.zones: Dict[str, ClimateZone] = {
            "ZONE_COASTAL_WET": ClimateZone(
                zone_id="ZONE_COASTAL_WET",
                name="Coastal Tropical Wet Belt (Rakhine Coast & Tanintharyi)",
                geographical_scope="Rakhine State, Ayeyarwady Delta, Mon State, Tanintharyi Region",
                annual_rainfall_mm=(3500.0, 5200.0),
                monsoon_months=["May", "June", "July", "August", "September", "October"],
                peak_cyclone_months=["April", "May", "October", "November"],
                air_operations_impact="Monsoon clouds (<300m) and torrential squalls shut down SAC CAS strikes >65% of days in June-August.",
                drone_operations_impact="Severe saltwater corrosion, high coastal wind shear (>12 m/s), and downpours short-circuit commercial FPV drones.",
                typical_environmental_hazards=["Tropical Cyclones (Bay of Bengal)", "Storm Surges", "Flash Flooding", "Riverine Coastal Erosion"]
            ),
            "ZONE_CENTRAL_DRY": ClimateZone(
                zone_id="ZONE_CENTRAL_DRY",
                name="Central Dry Zone (Anyar Plains)",
                geographical_scope="Sagaing Region, Magway Region, Mandalay Region",
                annual_rainfall_mm=(600.0, 1000.0),
                monsoon_months=["July", "August", "September"],
                peak_cyclone_months=[],
                air_operations_impact="Near-year-round clear skies allow maximum SAC daily sortie generation (Yak-130, K-8, Mi-35) 8 to 9 months/year.",
                drone_operations_impact="Ideal thermal and wind conditions for resistance FPV strikes, except during extreme dust storms and afternoon heatwaves (>42°C).",
                typical_environmental_hazards=["Extreme Heatwaves (>44°C)", "Agricultural Brush Fires / Smoke Haze", "Severe Water Scarcity", "Dust Storms"]
            ),
            "ZONE_NORTHERN_MOUNTAIN": ClimateZone(
                zone_id="ZONE_NORTHERN_MOUNTAIN",
                name="Northern Mountain & Subtropical Highland",
                geographical_scope="Kachin State, Upper Sagaing (Homalin, Banmauk)",
                annual_rainfall_mm=(1800.0, 2800.0),
                monsoon_months=["May", "June", "July", "August", "September"],
                peak_cyclone_months=[],
                air_operations_impact="Mountain valley fog and low cloud bases force SAC jets into high-altitude unguided bomb drops or aborts.",
                drone_operations_impact="Alpine wind gusts over mountain saddles cause heavy battery drain; rain and cold degrade lithium-polymer capacity by 30%.",
                typical_environmental_hazards=["Massive Jade Mine Landslides (Hpakant)", "Alpine Flash Floods (N'Mai / Mali Hka)", "Logistics Road Washouts"]
            ),
            "ZONE_SHAN_PLATEAU": ClimateZone(
                zone_id="ZONE_SHAN_PLATEAU",
                name="Eastern Shan Limestone Plateau",
                geographical_scope="Northern Shan State, Southern Shan State, Eastern Shan",
                annual_rainfall_mm=(1200.0, 1800.0),
                monsoon_months=["June", "July", "August", "September"],
                peak_cyclone_months=[],
                air_operations_impact="Moderate monsoon interference; cloud layers obstruct visual bombing along Salween river gorge.",
                drone_operations_impact="Highly viable for tactical hexacopter and FPV drone operations outside direct thunderstorm cells.",
                typical_environmental_hazards=["Karst Sinkholes", "Highland Soil Erosion", "Flash Mountain Floods", "Seasonal Winter Fog"]
            ),
            "ZONE_SOUTHEAST_HILLS": ClimateZone(
                zone_id="ZONE_SOUTHEAST_HILLS",
                name="Southeastern Dawna & Karen Hills",
                geographical_scope="Kayah (Karenni) State, Kayin State, Bago Yoma",
                annual_rainfall_mm=(2200.0, 3800.0),
                monsoon_months=["May", "June", "July", "August", "September", "October"],
                peak_cyclone_months=["May", "October"],
                air_operations_impact="Heavy rainfall along Bilauktaung and Dawna ranges severely curtails Taungoo-based SAC strike packages.",
                drone_operations_impact="High humidity and rapid weather fronts require flexible mobile drone strike teams with waterproof coatings.",
                typical_environmental_hazards=["Mountain Road Mudslides", "Salween & Sittaung River Floods", "River Crossing Inundations"]
            )
        }
        self.acoustic_model = AtmosphericAcousticModel()

    def get_zone(self, zone_id: str) -> Optional[ClimateZone]:
        zid = zone_id.upper().strip()
        if zid in self.zones:
            return self.zones[zid]
        if not zid.startswith("ZONE_"):
            prefixed = f"ZONE_{zid}"
            if prefixed in self.zones:
                return self.zones[prefixed]
        for k, v in self.zones.items():
            if zid in k or zid in v.name.upper():
                return v
        return None

    def list_zones(self) -> List[ClimateZone]:
        return list(self.zones.values())

    def evaluate_flight_conditions(
        self,
        wind_speed_ms: float,
        rain_rate_mm_hr: float,
        cloud_ceiling_m: float
    ) -> TacticalFlightConditions:
        """Evaluates tactical flight viability for FPV drones, hexacopters, and military strike aircraft."""
        limitations = []

        # 1. FPV Suicide Drones (7-10 inch)
        if wind_speed_ms > 10.0 or rain_rate_mm_hr > 0.5:
            fpv_status = "GROUNDED"
            if wind_speed_ms > 10.0:
                limitations.append(f"Wind speed {wind_speed_ms} m/s exceeds FPV motor saturation limit (10 m/s).")
            if rain_rate_mm_hr > 0.5:
                limitations.append(f"Precipitation {rain_rate_mm_hr} mm/hr causes short-circuit risk on exposed drone ESCs.")
        elif wind_speed_ms > 7.0 or rain_rate_mm_hr > 0.0:
            fpv_status = "MARGINAL"
            limitations.append("Moderate wind/moisture degrades FPV flight stabilization and camera visibility.")
        else:
            fpv_status = "GO"

        # 2. Agricultural Heavy Hexacopter Bombers
        if wind_speed_ms > 13.0 or rain_rate_mm_hr > 3.0:
            hexa_status = "GROUNDED"
            limitations.append("Severe wind/rain grounds heavy hexacopter bombers.")
        elif wind_speed_ms > 9.0 or rain_rate_mm_hr > 1.0:
            hexa_status = "MARGINAL"
        else:
            hexa_status = "GO"

        # 3. Fixed-Wing CAS Jets (Yak-130, K-8W)
        if cloud_ceiling_m < 400.0 or rain_rate_mm_hr > 15.0:
            cas_status = "GROUNDED"
            limitations.append(f"Cloud ceiling {cloud_ceiling_m}m below minimum safe dive-bombing floor (400m).")
        elif cloud_ceiling_m < 800.0 or rain_rate_mm_hr > 5.0:
            cas_status = "CONSTRAINED_STANDOFF"
            limitations.append("Low cloud base limits visual ground targeting; forces standoff unguided bombing.")
        else:
            cas_status = "UNRESTRICTED"

        # 4. Attack & Transport Helicopters (Mi-35, Mi-17)
        if wind_speed_ms > 16.0 or rain_rate_mm_hr > 12.0 or cloud_ceiling_m < 200.0:
            heli_status = "GROUNDED"
            limitations.append("High mountain turbulence and low visibility ground rotary combat elements.")
        elif wind_speed_ms > 11.0:
            heli_status = "HIGH_TURBULENCE_RISK"
        else:
            heli_status = "GO"

        return TacticalFlightConditions(
            fpv_drone_status=fpv_status,
            hexacopter_status=hexa_status,
            cas_jet_strike_status=cas_status,
            helicopter_status=heli_status,
            critical_limitations=limitations
        )

    def evaluate_acoustic_propagation(
        self,
        temperature_c: float,
        relative_humidity_pct: float,
        frequency_hz: float,
        distance_km: float
    ) -> Dict[str, Any]:
        """Calculates environmental sound speed and expected decibel attenuation over distance."""
        c = self.acoustic_model.speed_of_sound_ms(temperature_c)
        alpha = self.acoustic_model.acoustic_attenuation_db_km(frequency_hz, relative_humidity_pct)
        total_attenuation_db = round(alpha * distance_km, 1)

        return {
            "temperature_c": temperature_c,
            "relative_humidity_pct": relative_humidity_pct,
            "speed_of_sound_ms": c,
            "frequency_hz": frequency_hz,
            "attenuation_coefficient_db_km": alpha,
            "distance_km": distance_km,
            "total_atmospheric_loss_db": total_attenuation_db,
            "acoustic_propagation_condition": "FAVORABLE" if alpha < 5.0 else ("MODERATE" if alpha < 20.0 else "HEAVILY_DAMPENED")
        }


# ============================================================
# 4.12. WORLD RELIGIONS & MYANMAR SOCIO-RELIGIOUS DYNAMICS
# ============================================================

@dataclass
class ReligiousTradition:
    tradition_id: str
    name: str
    core_ethos: str
    benevolent_aspects: List[str]
    dark_aspects: List[str]
    myanmar_population_share_pct: float
    primary_ethnic_adherents: List[str]
    prominent_humanitarian_institutions: List[str]
    weaponized_or_extremist_manifestations: List[str]


@dataclass
class SacredSiteIncident:
    incident_id: str
    site_name: str
    site_type: str  # CHURCH, MONASTERY, MOSQUE, TEMPLE, SHRINE
    religion: str
    region_state: str
    township: str
    date_occurred: str
    damage_severity: str  # CRITICAL_TOTAL_DESTRUCTION, MAJOR_STRUCTURAL_DAMAGE, MODERATE_DESECRATION, THREAT_INTIMIDATION
    perpetrator_entity: str
    attack_vector: str  # AIRSTRIKE, ARTILLERY_SHELL, ARSON, GROUND_RAID
    civilian_casualties: int
    ihl_violation_status: str
    description: str


@dataclass
class YadayaRitualRecord:
    record_id: str
    ruler_or_actor: str
    era_or_date: str
    ritual_act: str
    esoteric_intent: str
    historical_outcome: str


class ReligiousDynamicsKnowledgeBase:
    """
    Structured domain knowledge of World Religions, comparing benevolent (light)
    and weaponized/extremist (dark) manifestations, integrated into Myanmar's
    socio-political, humanitarian, and counter-insurgency sectors.
    """

    def __init__(self):
        self.traditions: Dict[str, ReligiousTradition] = {
            "THERAVADA_BUDDHISM": ReligiousTradition(
                tradition_id="THERAVADA_BUDDHISM",
                name="Theravada Buddhism (Southern School)",
                core_ethos="Four Noble Truths, Noble Eightfold Path, Kamma (action/cause), Anicca (impermanence), Metta (loving-kindness), Karuna (compassion).",
                benevolent_aspects=[
                    "Monastic sanctuaries providing food, medical aid, and shelter to thousands of displaced villagers in Sagaing and Magway.",
                    "Saffron Revolution legacy: Overturning alms bowls (Patam Nikkujjana Kamma) as moral boycott and spiritual excommunication of military oppressors.",
                    "Free underground schooling in rural monasteries where state education collapsed post-coup.",
                    "Deep community meditation practices (Vipassana) cultivating psychological resilience in war zones."
                ],
                dark_aspects=[
                    "Ethno-nationalist majoritarian chauvinism: Monastic nationalist organizations (969 Movement, MaBaTha / Association for Protection of Race and Religion).",
                    "Anti-Rohingya and anti-Muslim hate speech incitement by radical monks (e.g., U Wirathu).",
                    "Militant monk alliances with SAC regime: Pyusawhti death squad formation and firearm distribution by radical monks (e.g., U Wasawa in Kanbalu).",
                    "State co-optation of supreme monastic hierarchy (State Sangha Maha Nayaka Committee / MaHaNa) to silence dissent."
                ],
                myanmar_population_share_pct=87.9,
                primary_ethnic_adherents=["Bamar", "Shan", "Mon", "Rakhine", "Pa-O", "Palaung (Ta'ang)"],
                prominent_humanitarian_institutions=[
                    "Local Village Sangha IDP Sanctuaries",
                    "Monastic Education Development Group (MEDG)",
                    "Anti-Coup Sangha Strike Strike Committees (Mandalay, Monywa)"
                ],
                weaponized_or_extremist_manifestations=[
                    "MaBaTha (Patriotic Association of Myanmar)",
                    "969 Movement",
                    "Pyusawhti Militias under militant monastic patronage"
                ]
            ),
            "CHRISTIANITY_BAPTIST": ReligiousTradition(
                tradition_id="CHRISTIANITY_BAPTIST",
                name="Christianity (Baptist Convention)",
                core_ethos="Salvation by grace through faith, authority of the Bible, autonomy of local church, social gospel, defense of the persecuted.",
                benevolent_aspects=[
                    "Primary humanitarian and civic backbone in ethnic minority highlands (Kachin, Chin, Karen).",
                    "Massive refugee and IDP camp administration delivering food, water, sanitation, and trauma healing (e.g., KBC sheltering >100,000 IDPs in Kachin).",
                    "International advocacy for federal democracy, religious freedom, and documenting SAC atrocities.",
                    "Bilingual ethnic language preservation and healthcare networks in remote mountain valleys."
                ],
                dark_aspects=[
                    "Historical inter-denominational rivalries occasionally hindering political cohesion.",
                    "Fundamentalist conservative doctrines in select sects discouraging civic resistance or modern rights advocacy.",
                    "Vulnerability to SAC targeting: Military arrests of senior pastors (e.g., Rev. Dr. Hkalam Samson)."
                ],
                myanmar_population_share_pct=4.2,
                primary_ethnic_adherents=["Kachin (Jinghpaw)", "Chin (Laimi, Asho)", "Karen (Sgaw, Pwo)", "Naga", "Lahu"],
                prominent_humanitarian_institutions=[
                    "Kachin Baptist Convention (KBC)",
                    "Chin Baptist Convention (CBC)",
                    "Karen Baptist Convention (KBC - Karen)",
                    "Myanmar Baptist Convention (MBC)"
                ],
                weaponized_or_extremist_manifestations=[
                    "Exploited by SAC propaganda claiming ethnic armies are 'Christian insurgents attacking Buddhist culture'."
                ]
            ),
            "CHRISTIANITY_CATHOLIC": ReligiousTradition(
                tradition_id="CHRISTIANITY_CATHOLIC",
                name="Christianity (Roman Catholic Church)",
                core_ethos="Universal Church, Sacraments, Social Doctrine, Preferential option for the poor, Sanctity of human dignity, Peacemaking.",
                benevolent_aspects=[
                    "Heroic frontline humanitarian leadership: Nuns kneeling before armed soldiers (Sister Ann Rose Nu Tawng in Myitkyina).",
                    "Dioceses of Pekon and Loikaw transformed cathedral complexes into major emergency refugee hubs.",
                    "Caritas Myanmar (KMSS) providing non-partisan medical and nutritional aid regardless of race or religion.",
                    "Vocal international advocacy by Cardinal Charles Maung Bo highlighting religious persecution and human rights."
                ],
                dark_aspects=[
                    "Historical institutional hierarchy that occasionally sought diplomatic compromises with the regime to protect church assets.",
                    "Systematic SAC targeting: More than 35 Catholic churches and rectories shelled, bombed, or occupied as military outposts in Kayah and Chin."
                ],
                myanmar_population_share_pct=1.8,
                primary_ethnic_adherents=["Karenni (Kayah)", "Karen", "Chin", "Kachin", "Anglo-Burmese", "Bamar converts"],
                prominent_humanitarian_institutions=[
                    "Karuna Mission Social Services (KMSS / Caritas Myanmar)",
                    "Diocese of Loikaw IDP Relief Committee",
                    "Diocese of Pekon Emergency Shelter Network"
                ],
                weaponized_or_extremist_manifestations=[
                    "Fringe ultra-traditionalist apathy; SAC disinformation targeting Catholic humanitarian networks."
                ]
            ),
            "ISLAM_SUNNI_SUFI": ReligiousTradition(
                tradition_id="ISLAM_SUNNI_SUFI",
                name="Islam (Sunni & Sufi Traditions)",
                core_ethos="Tawhid (Oneness of God), Five Pillars, Zakat (obligatory charity), Adl (divine justice), Ummah (brotherhood), Sufi inner devotion (Ihsan).",
                benevolent_aspects=[
                    "Unprecedented Spring Revolution solidarity: Muslim youth organizing medical teams and fighting in multi-faith PDF units.",
                    "Centuries of communal harmony in historical trade centers (Mandalay, Amarapura, Yangon, Mawlamyine).",
                    "Extensive covert charitable relief distributing rice, cash, and medical supplies to war-affected communities across faiths.",
                    "Sufi traditions emphasizing peace, tolerance, and poetic mystical devotion."
                ],
                dark_aspects=[
                    "Victim of state-sponsored genocidal persecution: 2017 clearance operations expelling >740,000 Rohingya to Bangladesh.",
                    "Systematic institutional discrimination: Denial of citizenship under 1982 Citizenship Law, arbitrary travel restrictions, and mosque closures.",
                    "Extremist splinter exploitation: Arakan Rohingya Salvation Army (ARSA) violent raids leveraged by Tatmadaw to justify collective punishment.",
                    "Vulnerability to SAC false-flag communal riot instigation."
                ],
                myanmar_population_share_pct=4.3,
                primary_ethnic_adherents=["Rohingya", "Kaman", "Bamar Muslims (Pathi)", "Panthay (Chinese Muslims)", "Indian Muslims"],
                prominent_humanitarian_institutions=[
                    "All Myanmar Islamic Association Relief Networks",
                    "Mandalay Multi-Faith Youth Humanitarian Brigade",
                    "Rohingya Refugee Relief Councils (Cox's Bazar / Arakan)"
                ],
                weaponized_or_extremist_manifestations=[
                    "ARSA (Arakan Rohingya Salvation Army)",
                    "RSO (Rohingya Solidarity Organisation) militant splinters"
                ]
            ),
            "HINDUISM": ReligiousTradition(
                tradition_id="HINDUISM",
                name="Hinduism (Sanatana Dharma)",
                core_ethos="Dharma (cosmic order/duty), Ahimsa (non-harm), Karma, Moksha (liberation), Bhakti (loving devotion).",
                benevolent_aspects=[
                    "Peaceful, pluralistic civic integration of Myanmar Tamils, Bengalis, and Gurkhas over two centuries.",
                    "Community temples hosting free vegetarian food kitchens (Annadana) welcoming displaced persons regardless of background.",
                    "Shared cultural and mythological heritage (Ramayana / Yama Zatdaw) deeply woven into traditional Burmese court culture and puppetry."
                ],
                dark_aspects=[
                    "Cross-border ideological contagion: Hindutva majoritarian rhetoric from India occasionally mirrored in local online discourse.",
                    "Vulnerability as a minority caught in ethnic crossfire in urban and border trading centers.",
                    "SAC instrumentalization: Regime inviting Hindu religious representatives to state ceremonies for international pluralism posturing."
                ],
                myanmar_population_share_pct=0.8,
                primary_ethnic_adherents=["Myanmar Tamils", "Gurkhas", "Bengali Hindus", "Manipuri (Kathe)"],
                prominent_humanitarian_institutions=[
                    "Sanatan Dharma Swayamsevak Sangh Myanmar Relief",
                    "Sri Kali & Sri Mariamman Temple Charitable Committees"
                ],
                weaponized_or_extremist_manifestations=[
                    "Radical online diaspora Hindutva sentiment targeting Muslim minorities."
                ]
            ),
            "ANIMISM_NAT_WORSHIP": ReligiousTradition(
                tradition_id="ANIMISM_NAT_WORSHIP",
                name="Animism & Nat Veneration (Spirit Worship)",
                core_ethos="Spirits (Nats) inhabit nature, mountains, trees, and water bodies; ancestor veneration; reciprocal respect between humans and the natural cosmos.",
                benevolent_aspects=[
                    "Indigenous ecological stewardship: Sacred groves, spirit mountains, and river taboos prohibiting deforestation, illegal mining, and habitat destruction.",
                    "Highland communal solidarity and village elder conflict resolution protocols.",
                    "Syncretic integration with Theravada Buddhism: The cult of the 37 Great Nats providing emotional solace, festive bonding (Taungbyone Nat Pwe), and localized identity."
                ],
                dark_aspects=[
                    "Fatalistic spirit fear: Manipulated by unscrupulous spirit mediums (Nat Kadaws) extracting excessive tribute.",
                    "Superstitious exploitation: Rogue commanders performing bloody animal sacrifices before combat.",
                    "Historical marginalization by orthodox state authorities as 'backward superstition'."
                ],
                myanmar_population_share_pct=1.0,
                primary_ethnic_adherents=["Highland Chin", "Naga", "Kachin (Rawang, Lisu)", "Akha", "Wa", "Syncretic Bamar"],
                prominent_humanitarian_institutions=[
                    "Customary Highland Tribal Elder Councils",
                    "Taungbyone Festival Communal Kitchens"
                ],
                weaponized_or_extremist_manifestations=[
                    "Occult spirit manipulation in military psychological warfare."
                ]
            ),
            "WEIZZA_YADAYA_OCCULT": ReligiousTradition(
                tradition_id="WEIZZA_YADAYA_OCCULT",
                name="Esoteric Weizza Pathways & Military Yadaya",
                core_ethos="Supernatural mastery (Weizza) through alchemy, samatha meditation, sacred geometry (Yantras), numerology, and karmic evasion (Yadaya).",
                benevolent_aspects=[
                    "Traditional herbal medicine and holistic healing practiced by reclusive forest masters (Yathes).",
                    "Meditation practices focused on spiritual purification and moral transcendence beyond worldly strife.",
                    "Cultural folklore celebrating mythical immortal protectors who will arrive to inaugurate the era of the Metteyya Buddha."
                ],
                dark_aspects=[
                    "Institutionalized military occult dictatorship: Systematically weaponized by Tatmadaw top brass to maintain dictatorial power.",
                    "Karmic evasion rituals (Yadaya): Conducting bizarre symbolic acts to ritually avert predicted political collapse, neutralize curses, or destroy rivals.",
                    "Misogynistic black magic: Tatmadaw commanders ritually stepping over women's sarongs (Htamain) or hanging underwear over resistance icons to neutralize feminine power (specifically targeting Aung San Suu Kyi).",
                    "Costly monument construction as karmic laundering while slaughtering civilians."
                ],
                myanmar_population_share_pct=0.0,  # Cross-cutting esoteric practice
                primary_ethnic_adherents=["Tatmadaw High Command", "Elite Astrologers (Beda)", "Esoteric Buddhist Sects"],
                prominent_humanitarian_institutions=[],
                weaponized_or_extremist_manifestations=[
                    "State-level Yadaya ritual operations",
                    "Military astrologer councils dictating cabinet timing and battle launches",
                    "Occult counter-curse psychological operations"
                ]
            )
        }

        self.documented_sacred_site_attacks: List[SacredSiteIncident] = [
            SacredSiteIncident(
                incident_id="SAC-SACR-001",
                site_name="Thantlang Baptist Church & Town Parishes",
                site_type="CHURCH",
                religion="CHRISTIANITY_BAPTIST",
                region_state="Chin State",
                township="Thantlang",
                date_occurred="2021-10-29",
                damage_severity="CRITICAL_TOTAL_DESTRUCTION",
                perpetrator_entity="SAC Light Infantry Division 66",
                attack_vector="ARSON_AND_ARTILLERY",
                civilian_casualties=1,
                ihl_violation_status="PROBABLE_WAR_CRIME_GENEVA_ART_53",
                description="Entire mountain town incinerated including Baptist and Catholic churches; Pastor Cung Biak Hum shot dead while attempting to extinguish church fires."
            ),
            SacredSiteIncident(
                incident_id="SAC-SACR-002",
                site_name="Sacred Heart Catholic Church (Kayan Tharyar)",
                site_type="CHURCH",
                religion="CHRISTIANITY_CATHOLIC",
                region_state="Kayah (Karenni) State",
                township="Loikaw",
                date_occurred="2021-05-24",
                damage_severity="MAJOR_STRUCTURAL_DAMAGE",
                perpetrator_entity="SAC Artillery Regiment",
                attack_vector="ARTILLERY_SHELL",
                civilian_casualties=4,
                ihl_violation_status="PROBABLE_WAR_CRIME_GENEVA_ART_53",
                description="Direct heavy artillery strike on Catholic church compound sheltering women and children fleeing Loikaw combat; 4 civilian women killed."
            ),
            SacredSiteIncident(
                incident_id="SAC-SACR-003",
                site_name="Ye-U Monastic Educational Complex",
                site_type="MONASTERY",
                religion="THERAVADA_BUDDHISM",
                region_state="Sagaing Region",
                township="Ye-U",
                date_occurred="2022-09-16",
                damage_severity="CRITICAL_TOTAL_DESTRUCTION",
                perpetrator_entity="SAC Mi-35 Gunships & Airborne Ground Troops",
                attack_vector="AIRSTRIKE",
                civilian_casualties=11,
                ihl_violation_status="PROBABLE_WAR_CRIME_GENEVA_ART_53",
                description="Airstrike and ground assault on village monastery school (Let Yet Kone); Mi-35 cannon fire raked school building killing 11 schoolchildren and 2 teachers."
            ),
            SacredSiteIncident(
                incident_id="SAC-SACR-004",
                site_name="Historical Jameh Mosque of Maungdaw",
                site_type="MOSQUE",
                religion="ISLAM_SUNNI_SUFI",
                region_state="Rakhine State",
                township="Maungdaw",
                date_occurred="2024-05-18",
                damage_severity="MAJOR_STRUCTURAL_DAMAGE",
                perpetrator_entity="SAC Border Guard Police & Drone Units",
                attack_vector="AIRSTRIKE",
                civilian_casualties=7,
                ihl_violation_status="PROBABLE_WAR_CRIME_GENEVA_ART_53",
                description="Drone dropped munitions and artillery strike hit historic mosque during intense fighting against Arakan Army; minaret collapsed."
            ),
            SacredSiteIncident(
                incident_id="SAC-SACR-005",
                site_name="Christ the King Cathedral Complex",
                site_type="CHURCH",
                religion="CHRISTIANITY_CATHOLIC",
                region_state="Kayah (Karenni) State",
                township="Loikaw",
                date_occurred="2023-11-26",
                damage_severity="MODERATE_DESECRATION",
                perpetrator_entity="SAC Regional Operations Command",
                attack_vector="GROUND_RAID",
                civilian_casualties=0,
                ihl_violation_status="VIOLATION_OF_SACRED_NEUTRALITY",
                description="Military raided bishop's residence and cathedral compound, forcibly evicting Bishop Celso Ba Shwe, clergy, and 80 IDPs, converting church into military redoubt."
            )
        ]

        self.yadaya_records: List[YadayaRitualRecord] = [
            YadayaRitualRecord(
                record_id="YADAYA-001",
                ruler_or_actor="Senior General Min Aung Hlaing",
                era_or_date="2023-08-01",
                ritual_act="Consecration of Maravijaya Buddha Colossus in Naypyidaw (81-ft marble colossus, 1,780 tons, 9 sacred relics).",
                esoteric_intent="Karmic cleansing (Kamma Launder) and assumption of Chakkavatti (Universal Buddhist Monarch) mantle to avert military downfall.",
                historical_outcome="Failed to halt resistance momentum; 10 weeks later, Operation 1027 shattered SAC forces across Northern Shan State."
            ),
            YadayaRitualRecord(
                record_id="YADAYA-002",
                ruler_or_actor="General Ne Win",
                era_or_date="1987-09-05",
                ritual_act="Demonetization of 25, 35, and 75-kyat banknotes; introduction of 45 and 90-kyat notes based on astrological numerology (divisible by 9).",
                esoteric_intent="Astrologer-directed ritual to ensure Ne Win would live past 90 years and suppress student unrest.",
                historical_outcome="Catastrophic economic collapse wiping out public savings; directly ignited the 8888 Nationwide Democratic Uprising."
            ),
            YadayaRitualRecord(
                record_id="YADAYA-003",
                ruler_or_actor="Senior General Than Shwe",
                era_or_date="2005-11-06 at precisely 06:37 AM",
                ritual_act="Abrupt relocation of the national capital from Yangon to Naypyidaw (The Royal City of Kings) carved out of jungle.",
                esoteric_intent="Astrological prediction of maritime foreign invasion; building an impenetrable fortress capital aligned with planetary deities.",
                historical_outcome="Created isolated military bunker capital, insulating junta from civilian urban protests."
            ),
            YadayaRitualRecord(
                record_id="YADAYA-004",
                ruler_or_actor="Tatmadaw Field Commanders",
                era_or_date="2021-2024",
                ritual_act="Stepping over women's sarongs (Htamain) and hoisting women's garments over flags (Anti-Htamain magic).",
                esoteric_intent="Deflecting female spiritual authority (Hpon) and neutralizing the protective power of female protest leaders.",
                historical_outcome="Backfired into widespread civil disobedience symbol: Women used Htamain wash lines as barricades that superstitious junta soldiers refused to cross."
            )
        ]

        self.state_demographics: Dict[str, Dict[str, float]] = {
            "CHIN": {"Christianity": 85.5, "Animism": 8.0, "Theravada_Buddhism": 6.2, "Islam": 0.3},
            "KACHIN": {"Christianity": 64.8, "Theravada_Buddhism": 31.0, "Animism": 2.5, "Islam": 1.7},
            "KAYAH": {"Christianity": 47.9, "Theravada_Buddhism": 46.5, "Animism": 3.8, "Islam": 1.8},
            "KAYIN": {"Theravada_Buddhism": 82.5, "Christianity": 11.2, "Islam": 5.0, "Animism": 1.3},
            "SAGAING": {"Theravada_Buddhism": 92.2, "Christianity": 5.1, "Islam": 2.5, "Hinduism": 0.2},
            "MAGWAY": {"Theravada_Buddhism": 97.4, "Islam": 1.8, "Christianity": 0.7, "Hinduism": 0.1},
            "MANDALAY": {"Theravada_Buddhism": 92.0, "Islam": 6.0, "Christianity": 1.1, "Hinduism": 0.9},
            "YANGON": {"Theravada_Buddhism": 83.2, "Islam": 8.4, "Christianity": 4.8, "Hinduism": 3.6},
            "RAKHINE": {"Theravada_Buddhism": 63.8, "Islam": 34.2, "Hinduism": 1.4, "Animism": 0.6},
            "SHAN": {"Theravada_Buddhism": 81.7, "Christianity": 9.8, "Animism": 6.5, "Islam": 2.0},
            "MON": {"Theravada_Buddhism": 92.6, "Islam": 4.1, "Christianity": 2.5, "Hinduism": 0.8},
            "TANINTHARYI": {"Theravada_Buddhism": 87.5, "Christianity": 7.2, "Islam": 5.1, "Hinduism": 0.2},
            "BAGO": {"Theravada_Buddhism": 93.5, "Christianity": 3.2, "Islam": 2.8, "Hinduism": 0.5},
            "AYEYARWADY": {"Theravada_Buddhism": 92.1, "Christianity": 6.3, "Islam": 1.4, "Hinduism": 0.2}
        }

    def get_tradition(self, tradition_id: str) -> Optional[ReligiousTradition]:
        tid = tradition_id.upper().strip()
        if tid in self.traditions:
            return self.traditions[tid]
        for k, v in self.traditions.items():
            if tid in k or tid in v.name.upper():
                return v
        return None

    def list_traditions(self) -> List[ReligiousTradition]:
        return list(self.traditions.values())

    def get_state_demographics(self, state_name: str) -> Optional[Dict[str, float]]:
        st = state_name.upper().strip()
        for k, v in self.state_demographics.items():
            if st in k:
                return v
        return None


# ============================================================
# 4.13. THE VOID PILLAR ENGINE (THE NULL SPACE & ZERO-TRACE)
# ============================================================

@dataclass
class BlackoutZone:
    zone_id: str
    region_state: str
    townships: List[str]
    blackout_type: str  # TOTAL_TELECOM_SEVERANCE, MOBILE_DATA_THROTTLED, FIBER_CUT, POWER_GRID_SHUTDOWN
    commenced_date: str
    severed_infrastructure: List[str]
    estimated_uncontactable_civilians: int
    tactical_purpose: str
    dtn_mesh_relay_status: str


@dataclass
class AbsenceAnomalyProfile:
    profile_id: str
    monitored_signal: str  # CELLULAR_PING_RATE, ACOUSTIC_COMMUNITY_CHATTER, HF_RADIO_TRANSMISSIONS, TRUCKING_TRAFFIC
    baseline_frequency_or_rate: str
    anomaly_threshold_silence_sec: float
    tactical_threat_inference: str
    recommended_defense_action: str


@dataclass
class ZeroizationProtocolDefinition:
    protocol_id: str
    tamper_trigger: str  # CHASSIS_BREACH_LIGHT_SENSOR, ENCLOSURE_TRIPWIRE, REPEATED_FAILED_AUTH, DEAD_MAN_TIMER_EXPIRED
    wipe_sequence: List[str]
    execution_time_ms: float
    post_wipe_hardware_state: str  # PERMANENT_BRICK, REVERSIBLE_COLD_REFLASH


class VoidPillarEngine:
    """
    Structured domain knowledge for the Fifth Pillar: VOID (The Null Space).
    Governs the anomaly of absence, telecommunication blackouts, anti-forensic zeroization,
    epistemic uncertainty modeling, and delay-tolerant networking (DTN).
    """

    def __init__(self):
        self.blackout_zones: Dict[str, BlackoutZone] = {
            "ZONE_SAGAING_HEARTLAND": BlackoutZone(
                zone_id="ZONE_SAGAING_HEARTLAND",
                region_state="Sagaing Region",
                townships=["Ayadaw", "Budalin", "Depayin", "Kani", "Pale", "Salingyi", "Ye-U"],
                blackout_type="TOTAL_TELECOM_SEVERANCE",
                commenced_date="2022-03-03",
                severed_infrastructure=["MPT/Mytel/Atom fiber trunks severed", "312 cellular tower power cuts"],
                estimated_uncontactable_civilians=1450000,
                tactical_purpose="Information blockade to conceal SAC scorched-earth village arson and prevent resistance ambush coordination.",
                dtn_mesh_relay_status="ACTIVE_OFFLINE_LORA_MESH"
            ),
            "ZONE_CHIN_HIGHLANDS": BlackoutZone(
                zone_id="ZONE_CHIN_HIGHLANDS",
                region_state="Chin State",
                townships=["Thantlang", "Mindat", "Matupi", "Kanpetlet"],
                blackout_type="TOTAL_TELECOM_SEVERANCE",
                commenced_date="2021-09-23",
                severed_infrastructure=["Microwave relay towers on Mt. Victoria sabotaged", "Generators seized"],
                estimated_uncontactable_civilians=380000,
                tactical_purpose="Isolate Chinland Defense Forces (CDF) from satellite internet and cross-border humanitarian coordination.",
                dtn_mesh_relay_status="PARTIAL_MOTORCYCLE_COURIER_BUFFER"
            ),
            "ZONE_KAYAH_SALWEEN": BlackoutZone(
                zone_id="ZONE_KAYAH_SALWEEN",
                region_state="Kayah (Karenni) State",
                townships=["Demoso", "Hpruso", "Shadaw", "Bawlakhe"],
                blackout_type="FIBER_CUT_AND_GRID_SHUTDOWN",
                commenced_date="2022-01-12",
                severed_infrastructure=["Lawpita hydro-electric distribution lines severed to rebel sectors", "Mobile base stations unpowered"],
                estimated_uncontactable_civilians=210000,
                tactical_purpose="Prevent Karenni Nationalities Defence Force (KNDF) from relaying real-time SAC fighter jet air-raid alerts.",
                dtn_mesh_relay_status="ACTIVE_OFFLINE_LORA_MESH"
            ),
            "ZONE_RAKHINE_COASTAL": BlackoutZone(
                zone_id="ZONE_RAKHINE_COASTAL",
                region_state="Rakhine State",
                townships=["Pauktaw", "Minbya", "Mrauk-U", "Kyauktaw", "Maungdaw"],
                blackout_type="TOTAL_TELECOM_SEVERANCE",
                commenced_date="2023-11-13",
                severed_infrastructure=["Undersea fiber landing stations throttled", "All commercial 4G/5G disabled"],
                estimated_uncontactable_civilians=1100000,
                tactical_purpose="Prevent Arakan Army (AA) from coordinating urban siege operations and reporting naval artillery casualties.",
                dtn_mesh_relay_status="TACTICAL_HIGH_FREQUENCY_RADIO_BRIDGE"
            )
        }

        self.absence_anomalies: Dict[str, AbsenceAnomalyProfile] = {
            "ANOMALY_RADIO_SILENCE_PRE_STRIKE": AbsenceAnomalyProfile(
                profile_id="ANOMALY_RADIO_SILENCE_PRE_STRIKE",
                monitored_signal="SAC_VHF_UHF_TACTICAL_CHATTER",
                baseline_frequency_or_rate="15-25 transmissions / hour",
                anomaly_threshold_silence_sec=900.0,
                tactical_threat_inference="Immediate pre-strike electronic emissions blackout; CAS jets or heavy artillery barrage inbound within 5-20 minutes.",
                recommended_defense_action="TRIGGER_RED_ALERT_BOMB_SHELTER_EVACUATION"
            ),
            "ANOMALY_VILLAGE_ACOUSTIC_DROPOUT": AbsenceAnomalyProfile(
                profile_id="ANOMALY_VILLAGE_ACOUSTIC_DROPOUT",
                monitored_signal="AMBIENT_VILLAGE_BIOPHONY_AND_LIVESTOCK",
                baseline_frequency_or_rate="Continuous ambient 45-65 dB background",
                anomaly_threshold_silence_sec=600.0,
                tactical_threat_inference="Village silently evacuated or pinned down; probable covert enemy infantry scouting / sniper infiltration.",
                recommended_defense_action="DISPATCH_LOCAL_DEFENSE_RECON_PATROL"
            ),
            "ANOMALY_HEARTBEAT_SENSOR_LOSS": AbsenceAnomalyProfile(
                profile_id="ANOMALY_HEARTBEAT_SENSOR_LOSS",
                monitored_signal="PARLA_EDGE_NODE_LIVENESS_HEARTBEAT",
                baseline_frequency_or_rate="1 ping every 300 seconds",
                anomaly_threshold_silence_sec=1800.0,
                tactical_threat_inference="Node destroyed by kinetic blast, RF jammed, or power supply cut; sector entering unobserved Void status.",
                recommended_defense_action="REVISE_CONFIDENCE_MAP_TO_VOID_UNKNOWN"
            )
        }

        self.zeroization_protocols: Dict[str, ZeroizationProtocolDefinition] = {
            "PROTO_DEAD_MAN_CHASSIS_BREACH": ZeroizationProtocolDefinition(
                protocol_id="PROTO_DEAD_MAN_CHASSIS_BREACH",
                tamper_trigger="Internal photodiode detects ambient lux breach (enclosure opened).",
                wipe_sequence=[
                    "Overwriting AES-256 root master keys in SRAM with 0xAA / 0x55 / cryptographically secure random bytes.",
                    "Invalidating flash file allocation table (FAT) and erasing sector headers.",
                    "Overwriting physical GPS history buffer and node peer routing table.",
                    "Permanent hardware fuse blown (EFUSE_BLOW) to disable JTAG debug ports."
                ],
                execution_time_ms=12.4,
                post_wipe_hardware_state="PERMANENT_BRICK"
            ),
            "PROTO_DEAD_MAN_TIMER_EXPIRY": ZeroizationProtocolDefinition(
                protocol_id="PROTO_DEAD_MAN_TIMER_EXPIRY",
                tamper_trigger="No secure keep-alive passphrase entered within 72 hours.",
                wipe_sequence=[
                    "Zeroization of local encrypted ledger replica cache.",
                    "Clearing transient operating memory.",
                    "Dropping microcontroller into ultra-low-power locked bootloader awaiting rescue key."
                ],
                execution_time_ms=45.0,
                post_wipe_hardware_state="REVERSIBLE_COLD_REFLASH"
            )
        }

        self.epistemic_domains: Dict[str, str] = {
            "KNOWN": "High sensor density, verified multi-source telemetry, confident projection (Yang).",
            "NOISY_UNCERTAIN": "Active warfare interference, high acoustic reverberation, degraded sensor precision (Chaos).",
            "THE_VOID": "Total absence of sensor coverage, severed communication blackout, unobserved terrain (Void)."
        }

    def get_blackout_zone(self, zone_id: str) -> Optional[BlackoutZone]:
        zid = zone_id.upper().strip()
        if zid in self.blackout_zones:
            return self.blackout_zones[zid]
        for k, v in self.blackout_zones.items():
            if zid in k or zid in v.region_state.upper() or any(zid in t.upper() for t in v.townships):
                return v
        return None

    def list_blackout_zones(self) -> List[BlackoutZone]:
        return list(self.blackout_zones.values())

    def get_absence_anomaly(self, anomaly_id: str) -> Optional[AbsenceAnomalyProfile]:
        aid = anomaly_id.upper().strip()
        if aid in self.absence_anomalies:
            return self.absence_anomalies[aid]
        for k, v in self.absence_anomalies.items():
            if aid in k or aid in v.monitored_signal.upper():
                return v
        return None


# ============================================================
# 4.9. INTERNATIONAL ACCOUNTABILITY & COMMAND ROSTER
# ============================================================

@dataclass
class AccountabilityIndividual:
    individual_id: str
    name: str
    rank: str
    operational_role: str
    command_authority: str
    documented_cases: List[str]
    institutional_citations: List[str]
    evidentiary_grade: str
    echelon_id: str
    echelon_title: str


class InternationalAccountabilityKnowledgeBase:
    """
    Structured domain knowledge base of senior military commanders and echelons
    documented for war crimes, crimes against humanity, and command responsibility
    by the UN FFM, ICC, IIMM, and international bodies.
    """
    def __init__(self, json_path: Optional[Path] = None):
        self.individuals: Dict[str, AccountabilityIndividual] = {}
        self.echelons: Dict[str, Dict[str, Any]] = {}
        self._load_roster(json_path)

    def _load_roster(self, json_path: Optional[Path] = None):
        target = json_path or (Path(__file__).resolve().parent.parent.parent / "Data" / "international_accountability_roster_2026.json")
        if not target.exists():
            return
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            for ech in data.get("command_echelons", []):
                e_id = ech.get("echelon_id", "")
                self.echelons[e_id] = {
                    "echelon_id": e_id,
                    "echelon_title": ech.get("echelon_title", ""),
                    "legal_basis": ech.get("legal_basis", "")
                }
                for ind in ech.get("individuals", []):
                    entity = AccountabilityIndividual(
                        individual_id=ind["individual_id"],
                        name=ind["name"],
                        rank=ind["rank"],
                        operational_role=ind["operational_role"],
                        command_authority=ind["command_authority"],
                        documented_cases=ind.get("documented_cases", []),
                        institutional_citations=ind.get("institutional_citations", []),
                        evidentiary_grade=ind.get("evidentiary_grade", "A1"),
                        echelon_id=e_id,
                        echelon_title=ech.get("echelon_title", "")
                    )
                    self.individuals[entity.individual_id] = entity
                    self.individuals[entity.name.upper()] = entity
        except Exception:
            pass

    def get_individual(self, query: str) -> Optional[AccountabilityIndividual]:
        if not query:
            return None
        q = query.strip().upper()
        if q in self.individuals:
            return self.individuals[q]
        # Check full name, id, or rank+name containment
        for v in self.list_all():
            name_u = v.name.upper()
            rank_u = v.rank.upper()
            full_u = f"{rank_u} {name_u}"
            if q == name_u or name_u in q or q in name_u or q == v.individual_id.upper() or v.individual_id.upper() in q:
                return v
            if q == full_u or full_u in q or q in full_u:
                return v
        return None

    def list_all(self) -> List[AccountabilityIndividual]:
        seen = set()
        unique = []
        for ind in self.individuals.values():
            if ind.individual_id not in seen:
                seen.add(ind.individual_id)
                unique.append(ind)
        return unique


# ============================================================
# 5. UNIFIED KNOWLEDGE BASE
# ============================================================

class ParlaKnowledgeBase:
    def __init__(self):
        self.acoustic = AcousticKnowledgeBase()
        self.osint = OSINTKnowledgeBase()
        self.regional = MyanmarRegionalContext()
        self.protocols = HumanitarianProtocols()
        self.eao = MyanmarEAO2023_2025Context()
        self.geology = GeologicalKnowledgeBase()
        self.arms = MilitaryArsenalKnowledgeBase()
        self.sac_air = SACAircraftFleetKnowledgeBase()
        self.weather = WeatherKnowledgeBase()
        self.religion = ReligiousDynamicsKnowledgeBase()
        self.void = VoidPillarEngine()
        self.accountability = InternationalAccountabilityKnowledgeBase()
    
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
    
    def analyze_osint(
        self,
        text: str,
        source_reliability: str = "C",
        base_credibility: int = 3,
        corroborations: Optional[List[Dict[str, Any]]] = None,
        contradictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        matches = self.osint.classify_text(text)
        primary_event = matches[0][0] if matches else "UNKNOWN"
        raw_confidence = matches[0][1] if matches else 0.0
        
        # Admiralty Evaluation
        assessment = self.osint.evaluate_admiralty(
            reliability=source_reliability,
            credibility=base_credibility,
            corroborating_evidence=corroborations,
            contradiction_evidence=contradictions
        )
        
        # Tactical Extraction
        tactical_entities = self.osint.extract_tactical_entities(text)
        detected_contradictions = self.osint.detect_contradictions(text)
        if contradictions:
            detected_contradictions.extend(contradictions)
            
        # Cross-reference with SAC Aircraft Fleet Knowledge Base
        enriched_sac_threats = []
        for ac in tactical_entities.get("aircraft", []):
            ac_norm = ac.replace("_", "-")
            profile = self.sac_air.aircraft.get(ac) or self.sac_air.aircraft.get(ac_norm)
            if profile:
                enriched_sac_threats.append({
                    "model": profile.common_name,
                    "category": profile.category,
                    "threat_level": "EXTREME" if "SUPERIORITY" in profile.category else "HIGH",
                    "primary_bases": profile.primary_airbases,
                    "ordnance_payload": profile.typical_strike_weapons,
                    "acoustic_signature": profile.acoustic_signature_profile
                })
                
        # Cross-reference with Military Arsenal Knowledge Base
        enriched_ordnance = []
        for ord_name in tactical_entities.get("ordnance", []):
            if ord_name == "THERMOBARIC_ODAB":
                enriched_ordnance.append({
                    "system": "ODAB-500PM Thermobaric FAE",
                    "hazard": "Severe vacuum overpressure & thermal blast",
                    "lethal_radius_m": 150,
                    "humanitarian_flag": "MASS_CASUALTY_HAZARD"
                })
            elif ord_name == "FAB_500":
                enriched_ordnance.append({
                    "system": "FAB-500 Demolition Aerial Bomb",
                    "hazard": "Structural collapse & deep cratering",
                    "lethal_radius_m": 120,
                    "humanitarian_flag": "STRUCTURE_DEMOLITION"
                })
                
        is_actionable = assessment.get("actionable_for_civilian_protection", False) or (raw_confidence >= 0.70)
        action_directive = "URGENT_CIVILIAN_SHELTER_ALERT" if (
            any(t.get("threat_level") in ("EXTREME", "HIGH") for t in enriched_sac_threats) or
            any(o.get("humanitarian_flag") == "MASS_CASUALTY_HAZARD" for o in enriched_ordnance)
        ) else ("ALERT" if is_actionable else "MONITOR")
        
        return {
            "event_matches": matches,
            "primary_event": primary_event,
            "confidence": assessment.get("elevated_confidence", raw_confidence),
            "base_confidence": raw_confidence,
            "admiralty_grade": assessment.get("elevated_grade", f"{source_reliability}{base_credibility}"),
            "admiralty_assessment": assessment,
            "tactical_intel": tactical_entities,
            "enriched_sac_threats": enriched_sac_threats,
            "enriched_ordnance": enriched_ordnance,
            "contradictions": detected_contradictions,
            "action_directive": action_directive,
            "risk_weight": self.osint.get_risk_weight(primary_event),
            "response_protocol": self.osint.get_response_protocol(primary_event),
            "action_protocol": self.protocols.get_protocol(primary_event, assessment.get("elevated_confidence", raw_confidence))
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

    def get_eao_intel(self, query: str = "") -> Dict[str, Any]:
        """
        100X Expanded EAO Intelligence & Relational Query Engine:
        Supports:
          - OP_ID (e.g. 'OP_1027_PHASE1')
          - FACTION_ID (e.g. 'AA', 'UWSA', 'MNDAA')
          - THEATER_ID (e.g. 'THEATER_SHAN_NORTH')
          - 'COALITION:<ID>' (e.g. 'COALITION:3BA', 'COALITION:FPNCC')
          - 'RELATION:<FACTION_A>:<FACTION_B>' (e.g. 'RELATION:MNDAA:TNLA', 'RELATION:TNLA:SSPP')
          - 'ALLIES:<FACTION>' (e.g. 'ALLIES:AA', 'ALLIES:KIA')
          - 'ADVERSARIES:<FACTION>' (e.g. 'ADVERSARIES:AA', 'ADVERSARIES:PNLA')
          - 'FRICTIONS:<FACTION>' (e.g. 'FRICTIONS:TNLA', 'FRICTIONS:CNF_CNA')
          - Free text search (e.g. 'rare-earth', 'drone swarm')
        """
        q = query.strip()
        q_upper = q.upper()

        # 1. Bilateral Relationship query: RELATION:A:B
        if q_upper.startswith("RELATION:"):
            parts = q_upper.split(":")
            if len(parts) >= 3:
                f1, f2 = parts[1], parts[2]
                rel = self.eao.get_bilateral_relationship(f1, f2)
                return {"type": "BILATERAL_RELATIONSHIP", "data": rel, "faction_a": f1, "faction_b": f2}

        # 2. Allies query: ALLIES:FACTION
        if q_upper.startswith("ALLIES:"):
            fid = q_upper.split(":", 1)[1]
            allies = self.eao.get_allies(fid)
            return {"type": "ALLIES_LIST", "faction": fid, "allies_count": len(allies), "data": allies}

        # 3. Adversaries query: ADVERSARIES:FACTION
        if q_upper.startswith("ADVERSARIES:"):
            fid = q_upper.split(":", 1)[1]
            adv = self.eao.get_adversaries(fid)
            return {"type": "ADVERSARIES_LIST", "faction": fid, "adversaries_count": len(adv), "data": adv}

        # 4. Frictions query: FRICTIONS:FACTION
        if q_upper.startswith("FRICTIONS:"):
            fid = q_upper.split(":", 1)[1]
            frictions = self.eao.get_friction_points(fid)
            return {"type": "FRICTIONS_LIST", "faction": fid, "frictions_count": len(frictions), "data": frictions}

        # 5. Coalition query: COALITION:ID
        if q_upper.startswith("COALITION:"):
            cid = q_upper.split(":", 1)[1]
            coalition = self.eao.get_coalition(cid)
            return {"type": "COALITION", "coalition_id": cid, "data": coalition}

        # 6. Direct Operation / Faction / Theater lookups
        if q_upper in self.eao.operations:
            return {"type": "OPERATION", "data": self.eao.operations[q_upper]}
        elif q_upper in self.eao.factions:
            return {"type": "FACTION", "data": self.eao.factions[q_upper]}
        elif q_upper in self.eao.theaters:
            return {"type": "THEATER", "data": self.eao.theaters[q_upper]}
        elif q_upper in self.eao.coalitions:
            return {"type": "COALITION", "coalition_id": q_upper, "data": self.eao.coalitions[q_upper]}
        elif q:
            search_results = self.eao.search_intel(q)
            return {"type": "SEARCH_RESULTS", "data": search_results}
        else:
            return {
                "type": "MACRO_SUMMARY",
                "summary": self.eao.get_macro_summary(),
                "all_operations": [op.name for op in self.eao.list_operations()],
                "all_factions": list(self.eao.factions.keys()),
                "all_theaters": list(self.eao.theaters.keys()),
                "all_coalitions": self.eao.list_coalitions(),
                "total_bilateral_relationships": len(self.eao.relationships) // 2
            }

    def get_arms_intel(self, query: str = "") -> Dict[str, Any]:
        """
        Query engine for Military Arms & Armaments Knowledge Base:
        Supports:
          - 'COMPARE:<FACTION_A>:<FACTION_B>' (e.g. 'COMPARE:SAC:3BA', 'COMPARE:SAC:AA')
          - 'CALIBER:<CALIBER>' (e.g. 'CALIBER:5.56', 'CALIBER:7.62x39')
          - 'FACTION:<FACTION_ID>' (e.g. 'FACTION:SAC', 'FACTION:UWSA')
          - 'WEAPON:<ID>' or direct WEAPON_ID (e.g. 'WEAPON_SU30SME', 'WEAPON_FN6_MANPADS')
          - Empty query -> macro overview of all tracked weapons systems and arsenals
        """
        q = query.strip()
        q_upper = q.upper()

        if q_upper.startswith("COMPARE:"):
            parts = q_upper.split(":")
            if len(parts) >= 3:
                return {"type": "ARSENAL_COMPARISON", "data": self.arms.compare_arsenals(parts[1], parts[2])}
        elif q_upper.startswith("CALIBER:"):
            parts = q.split(":", 1)
            cal = parts[1].strip()
            return {"type": "CALIBER_MATCHES", "caliber": cal, "data": self.arms.match_weapons_by_caliber(cal)}
        elif q_upper.startswith("FACTION:"):
            parts = q_upper.split(":", 1)
            fac = parts[1].strip()
            return {"type": "FACTION_ARSENAL", "data": self.arms.get_faction_arsenal(fac)}
        elif q_upper.startswith("WEAPON:"):
            parts = q_upper.split(":", 1)
            w_id = parts[1].strip()
            return {"type": "WEAPON_SYSTEM", "data": self.arms.get_weapon(w_id)}
        elif q_upper in self.arms.weapons:
            return {"type": "WEAPON_SYSTEM", "data": self.arms.weapons[q_upper]}
        elif q_upper in self.arms.factions:
            return {"type": "FACTION_ARSENAL", "data": self.arms.factions[q_upper]}
        else:
            return {
                "type": "MACRO_ARMS_SUMMARY",
                "total_weapons_tracked": len(self.arms.weapons),
                "factions_tracked": list(self.arms.factions.keys()),
                "weapons_by_category": {
                    cat: len(self.arms.list_weapons(cat))
                    for cat in set(w.category for w in self.arms.weapons.values())
                }
            }

    def get_aircraft_intel(self, query: str = "") -> Dict[str, Any]:
        """
        Query engine for SAC Aircraft Fleet, Airbases, and Attrition Intelligence:
        Supports:
          - Model ID (e.g. 'SU-30SME', 'YAK-130', 'FTC-2000G', 'MI-35P', 'K-8W')
          - 'AIRBASE:<ID>' or 'AIRBASES'
          - 'ATTRITION' (returns documented shoot-down logs)
          - 'ACOUSTIC:<FREQ_HZ>:<DB>:<DOPPLER_HZ>'
          - Empty query -> comprehensive fleet overview
        """
        q = query.strip()
        q_upper = q.upper()

        if q_upper == "AIRBASES":
            return {"type": "AIRBASES_LIST", "total_airbases": len(self.sac_air.airbases), "data": self.sac_air.list_airbases()}
        elif q_upper.startswith("AIRBASE:"):
            b_id = q_upper.split(":", 1)[1].strip()
            return {"type": "AIRBASE_DETAIL", "data": self.sac_air.get_airbase(b_id)}
        elif q_upper == "ATTRITION":
            return {"type": "AIR_ATTRITION_LOGS", "total_losses": len(self.sac_air.attrition_records), "data": self.sac_air.list_attrition()}
        elif q_upper.startswith("ACOUSTIC:"):
            parts = q.split(":")
            if len(parts) >= 4:
                try:
                    f = float(parts[1])
                    db = float(parts[2])
                    dp = float(parts[3])
                    matches = self.sac_air.evaluate_acoustic_detection(f, db, dp)
                    return {"type": "ACOUSTIC_MATCHES", "telemetry": {"freq_hz": f, "db": db, "doppler_hz": dp}, "matches": matches}
                except ValueError:
                    pass
        elif q_upper in self.sac_air.aircraft:
            return {"type": "AIRCRAFT_PROFILE", "data": self.sac_air.aircraft[q_upper]}
        
        # Check partial model matches
        if q_upper:
            for m_id, model in self.sac_air.aircraft.items():
                if q_upper in m_id or q_upper in model.common_name.upper():
                    return {"type": "AIRCRAFT_PROFILE", "data": model}

        # Default macro summary
        total_fleet = sum(a.active_fleet_count for a in self.sac_air.aircraft.values())
        total_losses = sum(a.known_losses for a in self.sac_air.aircraft.values())
        return {
            "type": "MACRO_FLEET_SUMMARY",
            "active_fleet_estimate": total_fleet,
            "documented_losses": total_losses,
            "models_tracked": len(self.sac_air.aircraft),
            "airbases_tracked": len(self.sac_air.airbases),
            "fleet_by_category": {
                cat: sum(a.active_fleet_count for a in self.sac_air.list_aircraft(cat))
                for cat in set(a.category for a in self.sac_air.aircraft.values())
            }
        }

    def get_weather_intel(self, query: str = "") -> Dict[str, Any]:
        """
        Query engine for Weather Forecasting & Meteorological Intelligence:
        Supports:
          - 'ZONE:<ZONE_ID>' (e.g. 'ZONE:ZONE_CENTRAL_DRY', 'ZONE:ZONE_COASTAL_WET')
          - 'ZONES' (lists all climate zones)
          - 'FLIGHT:<WIND_MS>:<RAIN_MM_HR>:<CLOUD_M>' (evaluates drone and CAS flight viability)
          - 'ACOUSTIC:<TEMP_C>:<HUMIDITY_PCT>:<FREQ_HZ>:<DISTANCE_KM>' (calculates sound speed and attenuation)
          - Empty query -> comprehensive meteorological summary
        """
        q = query.strip()
        q_upper = q.upper()

        if q_upper == "ZONES":
            return {"type": "CLIMATE_ZONES_LIST", "total_zones": len(self.weather.zones), "data": [asdict(z) for z in self.weather.list_zones()]}
        elif q_upper.startswith("ZONE:"):
            z_id = q_upper.split(":", 1)[1].strip()
            z = self.weather.get_zone(z_id)
            return {"type": "CLIMATE_ZONE_DETAIL", "data": asdict(z) if z else None}
        elif q_upper in self.weather.zones:
            return {"type": "CLIMATE_ZONE_DETAIL", "data": asdict(self.weather.zones[q_upper])}
        elif q_upper.startswith("FLIGHT:"):
            parts = q.split(":")
            if len(parts) >= 4:
                try:
                    w_spd = float(parts[1])
                    rain = float(parts[2])
                    cloud = float(parts[3])
                    conditions = self.weather.evaluate_flight_conditions(w_spd, rain, cloud)
                    return {"type": "TACTICAL_FLIGHT_EVALUATION", "conditions": asdict(conditions)}
                except ValueError:
                    pass
        elif q_upper.startswith("ACOUSTIC:"):
            parts = q.split(":")
            if len(parts) >= 5:
                try:
                    temp = float(parts[1])
                    hum = float(parts[2])
                    freq = float(parts[3])
                    dist = float(parts[4])
                    prop = self.weather.evaluate_acoustic_propagation(temp, hum, freq, dist)
                    return {"type": "ACOUSTIC_PROPAGATION_REPORT", "data": prop}
                except ValueError:
                    pass

        # Partial zone search
        if q_upper:
            for z_id, zone in self.weather.zones.items():
                if q_upper in z_id or q_upper in zone.name.upper():
                    return {"type": "CLIMATE_ZONE_DETAIL", "data": asdict(zone)}

        # Default macro summary
        return {
            "type": "MACRO_WEATHER_SUMMARY",
            "climate_zones_tracked": len(self.weather.zones),
            "zones": [z.name for z in self.weather.list_zones()],
            "monsoon_season_months": "May to October (Southwest Monsoon)",
            "dry_season_months": "November to April (Northeast / Arid Season)",
            "cyclone_hazard_risk": "Bay of Bengal Severe Tropical Storms (Peak: April-May & October-November)"
        }

    def get_religious_intel(self, query: str = "") -> Dict[str, Any]:
        """
        World Religions & Myanmar Socio-Religious Intelligence Query Engine:
        Supports:
          - 'TRADITIONS': Complete taxonomy of world traditions in Myanmar.
          - 'TRADITION:<ID>': Detailed profile of a specific religion.
          - 'INCIDENTS' or 'SACRILEGE': Documented airstrikes and artillery attacks on churches, monasteries, and mosques under IHL.
          - 'YADAYA': Military esoteric rituals, astrology, and karmic manipulation records.
          - 'STATE:<NAME>' or 'DEMOGRAPHICS:<NAME>': State/Region religious demographics.
          - Free-text search across tradition names, concepts (e.g. 'Maravijaya', 'MaBaTha', 'Htamain', 'Metta', 'Saffron').
          - Empty query -> Macro socio-religious intelligence summary.
        """
        q = query.strip()
        q_upper = q.upper()

        if q_upper in ["TRADITIONS", "ALL"]:
            return {
                "type": "RELIGIOUS_TRADITIONS_LIST",
                "total_traditions": len(self.religion.traditions),
                "data": [asdict(t) for t in self.religion.list_traditions()]
            }
        elif q_upper.startswith("TRADITION:"):
            t_id = q_upper.split(":", 1)[1].strip()
            t = self.religion.get_tradition(t_id)
            return {"type": "RELIGIOUS_TRADITION_DETAIL", "data": asdict(t) if t else None}
        elif q_upper in self.religion.traditions:
            return {"type": "RELIGIOUS_TRADITION_DETAIL", "data": asdict(self.religion.traditions[q_upper])}
        elif q_upper in ["INCIDENTS", "SACRILEGE", "ATTACKS"]:
            return {
                "type": "SACRED_SITE_INCIDENTS_LIST",
                "total_incidents": len(self.religion.documented_sacred_site_attacks),
                "data": [asdict(i) for i in self.religion.documented_sacred_site_attacks]
            }
        elif q_upper.startswith("YADAYA"):
            return {
                "type": "YADAYA_RITUALS_LIST",
                "total_records": len(self.religion.yadaya_records),
                "data": [asdict(y) for y in self.religion.yadaya_records]
            }
        elif q_upper.startswith("STATE:") or q_upper.startswith("DEMOGRAPHICS:"):
            st_name = q_upper.split(":", 1)[1].strip()
            demo = self.religion.get_state_demographics(st_name)
            return {"type": "STATE_RELIGIOUS_DEMOGRAPHICS", "state_region": st_name, "data": demo}

        # Partial match on traditions
        if q_upper:
            for t_id, trad in self.religion.traditions.items():
                if q_upper in t_id or q_upper in trad.name.upper() or any(q_upper in m.upper() for m in trad.weaponized_or_extremist_manifestations):
                    return {"type": "RELIGIOUS_TRADITION_DETAIL", "data": asdict(trad)}

            # Search in incidents
            matched_incidents = [
                asdict(i) for i in self.religion.documented_sacred_site_attacks
                if q_upper in i.site_name.upper() or q_upper in i.region_state.upper() or q_upper in i.description.upper()
            ]
            if matched_incidents:
                return {"type": "SACRED_SITE_INCIDENTS_MATCH", "query": query, "matches": matched_incidents}

            # Search in Yadaya
            matched_yadaya = [
                asdict(y) for y in self.religion.yadaya_records
                if q_upper in y.ruler_or_actor.upper() or q_upper in y.ritual_act.upper() or q_upper in y.esoteric_intent.upper()
            ]
            if matched_yadaya:
                return {"type": "YADAYA_RECORDS_MATCH", "query": query, "matches": matched_yadaya}

            # State demographics search
            demo = self.religion.get_state_demographics(q_upper)
            if demo:
                return {"type": "STATE_RELIGIOUS_DEMOGRAPHICS", "state_region": q_upper, "data": demo}

        # Default macro summary
        return {
            "type": "MACRO_SOCIO_RELIGIOUS_SUMMARY",
            "world_traditions_profiled": len(self.religion.traditions),
            "documented_sacred_site_strikes": len(self.religion.documented_sacred_site_attacks),
            "historical_military_yadaya_records": len(self.religion.yadaya_records),
            "states_demographically_mapped": len(self.religion.state_demographics),
            "national_religious_split_approx": {
                "Theravada_Buddhism": "87.9%",
                "Christianity": "6.2% (Concentrated in Chin 85%, Kachin 65%, Kayah 48%)",
                "Islam": "4.3% (Concentrated in Rakhine 34%, Yangon 8%, Mandalay 6%)",
                "Animism_Nat_Veneration": "1.0% (Indigenous Highlands & syncretized nationwide)",
                "Hinduism": "0.8% (Urban mercantile & historical agricultural pockets)"
            },
            "core_conflict_dynamics": {
                "light_sector": "Monastic IDP sanctuaries, Highland Christian relief (KBC, KMSS), Saffron moral boycott, inter-faith Spring Revolution solidarity.",
                "dark_sector": "MaBaTha/969 ethno-nationalism, Pyusawhti death squads under militant monks, Maravijaya karmic statecraft, airstrikes targeting churches/monasteries/mosques, misogynistic Htamain black magic."
            }
        }

    def get_void_intel(self, query: str = "") -> Dict[str, Any]:
        """
        The Fifth Pillar: VOID (The Null Space & Zero-Trace) Intelligence Engine:
        Supports:
          - 'BLACKOUTS': All documented telecommunication/internet blackout zones in Myanmar.
          - 'BLACKOUT:<ID_OR_NAME>': Specific blackout zone details.
          - 'ABSENCE' or 'ANOMALIES': Signal absence and silence indicators (the dog that didn't bark).
          - 'ZEROIZATION': Hardware dead-man triggers, key vaporization, and anti-forensics.
          - 'EPISTEMIC': Epistemic uncertainty mapping (Known vs. Noisy vs. The Void).
          - Free text search across blackout zones and anomaly profiles.
          - Empty query -> Macro Void summary.
        """
        q = query.strip()
        q_upper = q.upper()

        if q_upper in ["BLACKOUTS", "BLACKOUT_ZONES", "ZONES"]:
            return {
                "type": "BLACKOUT_ZONES_LIST",
                "total_blackout_zones": len(self.void.blackout_zones),
                "data": [asdict(z) for z in self.void.list_blackout_zones()]
            }
        elif q_upper.startswith("BLACKOUT:"):
            z_id = q_upper.split(":", 1)[1].strip()
            z = self.void.get_blackout_zone(z_id)
            return {"type": "BLACKOUT_ZONE_DETAIL", "data": asdict(z) if z else None}
        elif q_upper in self.void.blackout_zones:
            return {"type": "BLACKOUT_ZONE_DETAIL", "data": asdict(self.void.blackout_zones[q_upper])}
        elif q_upper in ["ABSENCE", "ANOMALIES", "ABSENCE_ANOMALIES"]:
            return {
                "type": "ABSENCE_ANOMALIES_LIST",
                "total_profiles": len(self.void.absence_anomalies),
                "data": [asdict(a) for a in self.void.absence_anomalies.values()]
            }
        elif q_upper.startswith("ANOMALY:"):
            a_id = q_upper.split(":", 1)[1].strip()
            a = self.void.get_absence_anomaly(a_id)
            return {"type": "ABSENCE_ANOMALY_DETAIL", "data": asdict(a) if a else None}
        elif q_upper in ["ZEROIZATION", "DEAD_MAN", "ANTIFORENSICS"]:
            return {
                "type": "ZEROIZATION_PROTOCOLS_LIST",
                "total_protocols": len(self.void.zeroization_protocols),
                "data": [asdict(p) for p in self.void.zeroization_protocols.values()]
            }
        elif q_upper in ["EPISTEMIC", "UNCERTAINTY", "IGNORANCE"]:
            return {
                "type": "EPISTEMIC_UNCERTAINTY_MAP",
                "domains": self.void.epistemic_domains
            }

        # Partial search
        if q_upper:
            # Blackout zone match
            z = self.void.get_blackout_zone(q_upper)
            if z:
                return {"type": "BLACKOUT_ZONE_DETAIL", "data": asdict(z)}

            # Anomaly profile match
            a = self.void.get_absence_anomaly(q_upper)
            if a:
                return {"type": "ABSENCE_ANOMALY_DETAIL", "data": asdict(a)}

            # Zeroization match
            for p_id, proto in self.void.zeroization_protocols.items():
                if q_upper in p_id or q_upper in proto.tamper_trigger.upper():
                    return {"type": "ZEROIZATION_PROTOCOL_DETAIL", "data": asdict(proto)}

        # Default macro summary
        return {
            "type": "MACRO_VOID_PILLAR_SUMMARY",
            "pillar_name": "VOID (The Null Space / Emptiness / Absence / Anti-Forensic Zero-Trace)",
            "position_in_paradigm": "The Fifth Pillar — The unobserved ground between Yin (receptive) and Yang (active), counterbalancing Chaos (entropy) and resolving into Harmony (consensus).",
            "active_telecom_blackout_zones": len(self.void.blackout_zones),
            "absence_anomaly_profiles_active": len(self.void.absence_anomalies),
            "zeroization_hardware_protocols": len(self.void.zeroization_protocols),
            "total_uncontactable_civilians_estimated": sum(z.estimated_uncontactable_civilians for z in self.void.list_blackout_zones()),
            "primary_doctrine": {
                "anomaly_of_absence": "Alerts when expected periodic signals or ambient noise abruptly vanish before strikes.",
                "dtn_mesh_buffering": "Asynchronous delay-tolerant store-and-forward when internet backbones are severed.",
                "anti_forensic_zeroization": "Millisecond-scale in-memory key shredding and hardware bricking upon enclosure tampering."
            }
        }

    def get_accountability_intel(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Queries international accountability rosters, command echelons, and legal citations."""
        if not query:
            return {
                "type": "ACCOUNTABILITY_ROSTER_SUMMARY",
                "total_commanders_tracked": len(self.accountability.list_all()),
                "command_echelons": list(self.accountability.echelons.values()),
                "individuals": [asdict(i) for i in self.accountability.list_all()]
            }
        ind = self.accountability.get_individual(query)
        if ind:
            return {
                "type": "ACCOUNTABILITY_INDIVIDUAL_DOSSIER",
                "data": asdict(ind)
            }
        return {
            "type": "ACCOUNTABILITY_NOT_FOUND",
            "query": query,
            "data": None
        }


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    kb = ParlaKnowledgeBase()
    
    print("=" * 75)
    print("📚 PARLA DOMAIN KNOWLEDGE BASE: 100X EXPANDED EAO RELATIONAL NETWORK")
    print("=" * 75)

    macro = kb.get_eao_intel()
    print(f"\n[1] MACRO CONFLICT INVENTORY (2023-2025):")
    print(f"    • Operations Tracked: {macro['summary']['operations_tracked']}")
    print(f"    • Factions Tracked: {macro['summary']['factions_tracked']}")
    print(f"    • Theaters Tracked: {macro['summary']['theaters_tracked']}")
    print(f"    • Coalitions Tracked: {len(macro['all_coalitions'])} ({', '.join(macro['all_coalitions'])})")
    print(f"    • Bilateral Relational Edges: {macro['total_bilateral_relationships']} verified pairs")
    print(f"    • Resistance Territorial Control: {macro['summary']['macro_territorial_split']['eao_and_resistance_control']}")

    print(f"\n[2] BILATERAL STRATEGIC ALLIANCE: MNDAA <-> TNLA")
    r_3ba = kb.get_eao_intel("RELATION:MNDAA:TNLA")
    if r_3ba["data"]:
        r = r_3ba["data"]
        print(f"    • Status: {r.rel_type} (Affinity: {r.affinity_score:+.2f} | Coalition: {r.coalition})")
        print(f"    • History: {r.historical_context}")
        print(f"    • Joint Ops: {', '.join(r.joint_operations)}")
        print(f"    • Arms Dynamic: {r.arms_flow}")

    print(f"\n[3] BILATERAL TERRITORIAL FRICTION: TNLA <-> SSPP")
    r_fric = kb.get_eao_intel("RELATION:TNLA:SSPP")
    if r_fric["data"]:
        r = r_fric["data"]
        print(f"    • Status: {r.rel_type} (Affinity: {r.affinity_score:+.2f})")
        print(f"    • Flashpoints: {', '.join(r.friction_points)}")

    print(f"\n[4] ALLIES QUERY: Arakan Army (AA)")
    aa_allies = kb.get_eao_intel("ALLIES:AA")
    print(f"    • AA Strategic Allies ({aa_allies['allies_count']}):")
    for ally in aa_allies["data"]:
        print(f"      - {ally.target_faction}: {ally.rel_type} (Score: {ally.affinity_score:+.2f}) -> {ally.historical_context[:70]}...")

    print(f"\n[5] ADVERSARIES QUERY: Pa-O National Liberation Army (PNLA)")
    pnla_adv = kb.get_eao_intel("ADVERSARIES:PNLA")
    print(f"    • PNLA Active Hostiles ({pnla_adv['adversaries_count']}):")
    for adv in pnla_adv["data"]:
        print(f"      - {adv.target_faction}: {adv.rel_type} (Score: {adv.affinity_score:+.2f}) -> {adv.historical_context[:70]}...")

    print(f"\n[6] COALITION PROFILE: Three Brotherhood Alliance (3BA)")
    c_3ba = kb.get_eao_intel("COALITION:3BA")
    if c_3ba["data"]:
        c = c_3ba["data"]
        print(f"    • Name: {c['name']} (Est. {c['established']})")
        print(f"    • Members: {', '.join(c['members'])}")
        print(f"    • Doctrine: {c['strategic_doctrine']}")
        print(f"    • Cohesion: {c['cohesion_level']}")

    print("\n" + "=" * 75)
    print("✓ 100X EXPANDED EAO RELATIONAL KNOWLEDGE BASE SELF-TEST COMPLETE")
    print("=" * 75)