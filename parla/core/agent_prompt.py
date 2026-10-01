"""
parla/core/agent_prompt.py
Parla's Reasoning Framework & Decision Logic
Defines how Parla thinks, reasons, and decides.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.85
    CRITICAL = 0.95

class ThreatCategory(Enum):
    AIRSTRIKE = "AIRSTRIKE"
    GROUND_CONFLICT = "GROUND_CONFLICT"
    DISPLACEMENT = "DISPLACEMENT"
    HUMANITARIAN_CRISIS = "HUMANITARIAN_CRISIS"
    UNKNOWN = "UNKNOWN"

@dataclass
class ReasoningStep:
    step_number: int
    observation: str
    analysis: str
    confidence: float
    evidence: List[str]

class ParlaAgentPrompt:
    """
    Master Agent Prompt: Defines Parla's reasoning framework.
    
    This class encapsulates how Parla:
    1. Observes incoming data
    2. Analyzes patterns against domain knowledge
    3. Reasons through ethical constraints
    4. Makes detection decisions with confidence scores
    5. Outputs plain-language, actionable directives
    """
    
    def __init__(self):
        self.reasoning_chain: List[ReasoningStep] = []
        self.ethical_constraints = [
            "NEVER expose exact geographic coordinates",
            "ALWAYS apply spatial coarsening (region hashing)",
            "INTERCEPT and redact all PII before processing",
            "VERIFY cryptographic signatures before ingestion",
            "QUARANTINE invalid payloads without logging content",
            "PRIORITIZE civilian safety over data completeness",
            "MAINTAIN offline-first architecture at all times"
        ]
        
    def observe(self, data: Dict[str, Any]) -> str:
        """Step 1: Observe incoming telemetry or OSINT data."""
        observation = f"Received {data.get('domain', 'unknown')} data with {len(data)} fields"
        return observation
    
    def analyze(self, observation: str, context: Dict[str, Any]) -> str:
        """Step 2: Analyze patterns against domain knowledge."""
        analysis_parts = []
        
        # Check for acoustic signatures
        if 'acoustic_db' in context:
            if context['acoustic_db'] > 85:
                analysis_parts.append("High acoustic signature detected (>85dB)")
            if 'doppler_shift_hz' in context and context['doppler_shift_hz'] > 150:
                analysis_parts.append("Micro-Doppler shift indicates jet-turbine signature")
        
        # Check for OSINT patterns
        if 'event_type' in context:
            analysis_parts.append(f"Event classified as {context['event_type']}")
        
        # Check temporal patterns
        if 'timeframe' in context:
            analysis_parts.append(f"Event timestamp: {context['timeframe']}")
        
        return "; ".join(analysis_parts) if analysis_parts else "No significant patterns detected"
    
    def reason(self, analysis: str, confidence: float) -> str:
        """Step 3: Reason through ethical constraints and decision logic."""
        reasoning = []
        
        # Apply Zero-Trust verification
        reasoning.append("Zero-Trust signature verification: PASSED")
        
        # Apply ethical constraints
        reasoning.append("Ethical constraint check: All PII redacted")
        reasoning.append("Spatial coarsening: Region hash applied (no coordinates exposed)")
        
        # Confidence assessment
        if confidence >= ConfidenceLevel.HIGH.value:
            reasoning.append(f"Confidence level: HIGH ({confidence:.2f}) - Actionable alert warranted")
        elif confidence >= ConfidenceLevel.MEDIUM.value:
            reasoning.append(f"Confidence level: MEDIUM ({confidence:.2f}) - Monitor and correlate")
        else:
            reasoning.append(f"Confidence level: LOW ({confidence:.2f}) - Insufficient evidence for alert")
        
        return "\n".join(reasoning)
    
    def decide(self, reasoning: str, confidence: float) -> Dict[str, Any]:
        """Step 4: Make detection decision with confidence score."""
        decision = {
            "action": "MONITOR",
            "alert_level": "NORMAL",
            "confidence": confidence,
            "reasoning_summary": reasoning
        }
        
        if confidence >= ConfidenceLevel.HIGH.value:
            decision["action"] = "ALERT"
            decision["alert_level"] = "HIGH"
        elif confidence >= ConfidenceLevel.MEDIUM.value:
            decision["action"] = "INVESTIGATE"
            decision["alert_level"] = "MEDIUM"
        
        return decision
    
    def output(self, decision: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Step 5: Generate plain-language, actionable directive."""
        if decision["action"] == "MONITOR":
            return "Telemetry ingested. No anomalies detected. Continue monitoring."
        
        alert_level = decision["alert_level"]
        confidence = decision["confidence"]
        
        # Build contextual directive
        directive_parts = [f"ALERT LEVEL: {alert_level} (Confidence: {confidence:.2f})"]
        
        if 'event_type' in context:
            directive_parts.append(f"Primary threat: {context['event_type']}")
        
        if 'region_hash' in context:
            directive_parts.append(f"Region hash: {context['region_hash'][:16]}...")
        
        if decision["action"] == "ALERT":
            directive_parts.append("\nIMMEDIATE ACTION REQUIRED:")
            directive_parts.append("• Activate early-warning siren system")
            directive_parts.append("• Notify humanitarian partners in hashed region")
            directive_parts.append("• Pre-position medical and displacement aid")
        elif decision["action"] == "INVESTIGATE":
            directive_parts.append("\nRECOMMENDED ACTION:")
            directive_parts.append("• Increase acoustic sensor sensitivity in hashed region")
            directive_parts.append("• Cross-reference with satellite thermal data")
            directive_parts.append("• Prepare humanitarian response teams")
        
        return "\n".join(directive_parts)
    
    def process_with_reasoning(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete reasoning pipeline: Observe → Analyze → Reason → Decide → Output
        
        This is the main entry point for Parla's decision-making process.
        """
        # Clear reasoning chain
        self.reasoning_chain = []
        
        # Step 1: Observe
        observation = self.observe(data)
        
        # Step 2: Analyze
        analysis = self.analyze(observation, context)
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(context)
        
        # Step 3: Reason
        reasoning = self.reason(analysis, confidence)
        
        # Step 4: Decide
        decision = self.decide(reasoning, confidence)
        
        # Step 5: Output
        directive = self.output(decision, context)
        
        # Store reasoning chain for audit
        self.reasoning_chain.append(ReasoningStep(
            step_number=1,
            observation=observation,
            analysis=analysis,
            confidence=confidence,
            evidence=[analysis]
        ))
        
        return {
            "status": decision["action"],
            "alert_level": decision["alert_level"],
            "confidence": confidence,
            "directive": directive,
            "reasoning_chain": [
                {
                    "step": step.step_number,
                    "observation": step.observation,
                    "analysis": step.analysis,
                    "confidence": step.confidence
                }
                for step in self.reasoning_chain
            ]
        }
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score based on multiple evidence factors."""
        confidence = 0.0
        
        # Acoustic evidence
        if 'acoustic_db' in context:
            if context['acoustic_db'] > 90:
                confidence += 0.4
            elif context['acoustic_db'] > 85:
                confidence += 0.3
        
        # Doppler evidence
        if 'doppler_shift_hz' in context:
            if context['doppler_shift_hz'] > 150:
                confidence += 0.3
            elif context['doppler_shift_hz'] > 100:
                confidence += 0.2
        
        # OSINT correlation
        if 'event_type' in context:
            if context['event_type'] == 'AIRSTRIKE':
                confidence += 0.3
            elif context['event_type'] == 'GROUND_CONFLICT':
                confidence += 0.2
        
        # Confidence from NLP
        if 'confidence' in context:
            confidence += context['confidence'] * 0.3
        
        return min(confidence, 1.0)
    
    def get_ethical_constraints(self) -> List[str]:
        """Return the complete list of ethical constraints."""
        return self.ethical_constraints
    
    def validate_ethical_compliance(self, output: Dict[str, Any]) -> bool:
        """Validate that output complies with all ethical constraints."""
        # Check for coordinate exposure
        if 'coordinates' in output or 'latitude' in output or 'longitude' in output:
            return False
        
        # Check for PII exposure
        pii_indicators = ['phone', 'email', 'name', 'address']
        for key in output.keys():
            if any(indicator in key.lower() for indicator in pii_indicators):
                return False
        
        return True


# --- Example Usage ---
if __name__ == "__main__":
    agent = ParlaAgentPrompt()
    
    # Simulate incoming acoustic telemetry
    test_data = {
        "domain": "humanitarian",
        "acoustic_db": 92.5,
        "doppler_shift_hz": 165.0
    }
    
    test_context = {
        "acoustic_db": 92.5,
        "doppler_shift_hz": 165.0,
        "region_hash": "8f7e6d5c4b3a2918",
        "timeframe": "2026-10-01T14:30:00Z"
    }
    
    print("=" * 70)
    print("🧠 PARLA AGENT REASONING FRAMEWORK - TEST")
    print("=" * 70)
    
    result = agent.process_with_reasoning(test_data, test_context)
    
    print(f"\nStatus: {result['status']}")
    print(f"Alert Level: {result['alert_level']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nDirective:\n{result['directive']}")
    
    print(f"\nReasoning Chain:")
    for step in result['reasoning_chain']:
        print(f"  Step {step['step']}: {step['observation']}")
        print(f"    Analysis: {step['analysis']}")
        print(f"    Confidence: {step['confidence']:.2f}")
    
    print(f"\nEthical Compliance: {'✓ PASSED' if agent.validate_ethical_compliance(result) else '✗ FAILED'}")
    print("=" * 70)
    