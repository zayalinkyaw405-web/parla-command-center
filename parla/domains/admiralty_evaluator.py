"""
parla/domains/admiralty_evaluator.py
NATO Standardized 6x6 Admiralty System Evaluator for OSINT Multi-INT Fusion.
Calculates rigorous source reliability, information credibility, and dynamic multi-vector corroboration scores.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

class SourceReliability(str, Enum):
    A = "A"  # Completely reliable (Calibrated scientific sensor / Accredited monitor)
    B = "B"  # Usually reliable (Established local investigator / Verified community lead)
    C = "C"  # Fairly reliable (Eyewitness with direct observation, unverified history)
    D = "D"  # Not usually reliable (Partisan actor / Sensationalist channel)
    E = "E"  # Unreliable (Demonstrated history of fabrication / Disinformation)
    F = "F"  # Cannot be judged (First-time anonymous submission without provenance)

class InformationCredibility(int, Enum):
    CONFIRMED = 1    # Confirmed by other independent sources / satellites
    PROBABLY_TRUE = 2 # Consistent with known enemy doctrine & capability
    POSSIBLY_TRUE = 3 # Plausible claim, lacking independent corroboration
    DOUBTFUL = 4      # Inconsistent with flight capabilities / physics
    IMPROBABLE = 5    # Contradictory to established facts
    CANNOT_JUDGE = 6  # Insufficient detail to assess validity

# Baseline confidence mappings for NATO 6x6 matrix
BASE_CONFIDENCE_TABLE: Dict[Tuple[str, int], float] = {
    ("A", 1): 0.98, ("A", 2): 0.90, ("A", 3): 0.80, ("A", 4): 0.50, ("A", 5): 0.20, ("A", 6): 0.40,
    ("B", 1): 0.92, ("B", 2): 0.85, ("B", 3): 0.75, ("B", 4): 0.45, ("B", 5): 0.18, ("B", 6): 0.35,
    ("C", 1): 0.88, ("C", 2): 0.75, ("C", 3): 0.65, ("C", 4): 0.38, ("C", 5): 0.15, ("C", 6): 0.30,
    ("D", 1): 0.70, ("D", 2): 0.55, ("D", 3): 0.45, ("D", 4): 0.25, ("D", 5): 0.10, ("D", 6): 0.20,
    ("E", 1): 0.40, ("E", 2): 0.30, ("E", 3): 0.20, ("E", 4): 0.10, ("E", 5): 0.05, ("E", 6): 0.10,
    ("F", 1): 0.80, ("F", 2): 0.60, ("F", 3): 0.50, ("F", 4): 0.25, ("F", 5): 0.10, ("F", 6): 0.25,
}

@dataclass
class AdmiraltyAssessment:
    initial_grade: str
    elevated_grade: str
    initial_confidence: float
    elevated_confidence: float
    corroboration_count: int
    corroborating_modalities: List[str]
    contradictions: List[str] = field(default_factory=list)
    actionable_for_civilian_protection: bool = False

class AdmiraltyEvaluator:
    """
    Evaluator executing NATO 6x6 Admiralty Intelligence assessment
    with multi-INT elevation (SOCMINT + GEOINT + SIGINT + Acoustic).
    """

    def __init__(self, alert_threshold_confidence: float = 0.70):
        self.alert_threshold = alert_threshold_confidence

    def get_base_confidence(self, reliability: SourceReliability, credibility: InformationCredibility) -> float:
        rel_str = reliability.value if isinstance(reliability, SourceReliability) else str(reliability).upper()
        cred_int = credibility.value if isinstance(credibility, InformationCredibility) else int(credibility)
        return BASE_CONFIDENCE_TABLE.get((rel_str, cred_int), 0.50)

    def evaluate(
        self,
        reliability: SourceReliability,
        credibility: InformationCredibility,
        corroborating_evidence: Optional[List[Dict[str, Any]]] = None,
        contradiction_evidence: Optional[List[str]] = None
    ) -> AdmiraltyAssessment:
        """
        Calculates multi-INT corroborated Admiralty grade and numerical confidence.
        """
        rel_str = reliability.value if isinstance(reliability, SourceReliability) else str(reliability).upper()
        cred_int = credibility.value if isinstance(credibility, InformationCredibility) else int(credibility)
        initial_grade = f"{rel_str}{cred_int}"
        base_conf = self.get_base_confidence(reliability, credibility)

        corroborations = corroborating_evidence or []
        contradictions = contradiction_evidence or []

        modalities = []
        elevation_bonus = 0.0

        for item in corroborations:
            modality = item.get("modality", "UNKNOWN")
            modalities.append(modality)
            # Modality-specific elevation weights
            if modality == "GEOINT_THERMAL":        # e.g. NASA FIRMS VIIRS hotspot
                elevation_bonus += 0.18
            elif modality == "SIGINT_FLIGHT":       # e.g. ADS-B military sortie track
                elevation_bonus += 0.14
            elif modality == "ACOUSTIC_EDGE":       # e.g. Micro-doppler turbine detection
                elevation_bonus += 0.16
            elif modality == "INDEPENDENT_SOCMINT":  # Second independent eyewitness
                elevation_bonus += 0.10
            else:
                elevation_bonus += 0.05

        # Penalty for contradictory evidence
        contradiction_penalty = len(contradictions) * 0.25
        final_conf = max(0.05, min(0.99, base_conf + elevation_bonus - contradiction_penalty))
        final_conf = round(final_conf, 2)

        # Re-derive elevated Admiralty Code based on multi-source confirmation
        elevated_cred = cred_int
        elevated_rel = rel_str

        if len(modalities) >= 2 and not contradictions:
            elevated_cred = 1  # Elevated to "Confirmed by other sources"
            if elevated_rel in ("B", "C", "F"):
                elevated_rel = "A" if "GEOINT_THERMAL" in modalities or "ACOUSTIC_EDGE" in modalities else "B"
        elif len(modalities) == 1 and not contradictions:
            if elevated_cred > 2:
                elevated_cred = 2  # Elevated to "Probably True"

        if contradictions:
            elevated_cred = max(elevated_cred, 4)  # Downgraded to Doubtful/Improbable

        elevated_grade = f"{elevated_rel}{elevated_cred}"
        actionable = (final_conf >= self.alert_threshold) and (elevated_cred <= 3) and (not contradictions)

        return AdmiraltyAssessment(
            initial_grade=initial_grade,
            elevated_grade=elevated_grade,
            initial_confidence=base_conf,
            elevated_confidence=final_conf,
            corroboration_count=len(corroborations),
            corroborating_modalities=modalities,
            contradictions=contradictions,
            actionable_for_civilian_protection=actionable
        )
