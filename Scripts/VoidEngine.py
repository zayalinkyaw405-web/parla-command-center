from parla.domains.void_engine import VoidEngine

engine = VoidEngine()

# Example scenario containing paranormal entities
scenario = {
    "entities": ["alien", "god", "mutation"]
}

result = engine.assess_paranormal_nullification(scenario)
print(result)
# {
#   "risk_score": 240 -> clamped to 100,
#   "confidence": 1.0,
#   "recommended_actions": [
#       "activate electromagnetic pulse",
#       "invoke containment protocols",
#       "apply quarantine measures"
#   ]
# }
