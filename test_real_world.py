import sys; sys.path.insert(0, '.')
from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature

extractor = OSINTEventExtractor()

# Paste a realistic, messy report here (with fake PII)
raw_text = "Urgent: Heavy shelling reported near the central market in Magway today. My neighbor Ko Aung (phone: +95-9-1234567) says 3 families fled. Contact me at test@email.com for details."

# Sign and process
sig = generate_osint_signature(raw_text)
result = extractor.process_osint_payload(raw_text, sig, source_id="FIELD_OPERATOR_01")

print("\n🛡️ PARLA PROCESSING RESULT:")
print(f"Status: {result['status']}")
print(f"Event: {result['event']['event_type']} (Confidence: {result['event']['confidence']})")
print(f"Action Required: {result['event'].get('action', 'N/A')}")
print(f"Region Hash: {result['event']['region_hash']}")
print(f"Ledger Hash: {result['ledger_hash'][:32]}...")