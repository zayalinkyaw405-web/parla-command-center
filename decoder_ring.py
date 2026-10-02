"""
decoder_ring.py
The Authorized Lookup Table for Parla's Zero-Trust Privacy Architecture.
THIS FILE MUST BE KEPT SECURE AND SEPARATE FROM THE LEDGER DATABASE.
"""
import hashlib
import json
from pathlib import Path
import sys

# Safe encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from parla.domains.risk_mapper import RegionalRiskMapper

# The Authorized Lookup Table
# Maps the internal Parla string to the Human-Readable Name
AUTHORIZED_MAP = {
    "MYANMAR_REGION_SAGAING": "Sagaing (Central Dry Zone)",
    "MYANMAR_REGION_RAKHINE": "Rakhine (Western Coast)",
    "MYANMAR_REGION_SHAN_NORTH": "Northern Shan State",
    "MYANMAR_REGION_KACHIN": "Kachin State (North)",
    "MYANMAR_REGION_CHIN": "Chin State (West)",
    "MYANMAR_REGION_KAYAH": "Kayah State (East)",
    "MYANMAR_REGION_KAYIN": "Kayin State (South-East)",
    "MYANMAR_REGION_MAGWAY": "Magway (Central)",
    "MYANMAR_REGION_MANDALAY": "Mandalay (Central)",
    "MYANMAR_REGION_YANGON": "Yangon (South)",
    "MYANMAR_REGION_UNSPECIFIED": "Unspecified / Coords Redacted"
}

def generate_hash_lookup() -> dict:
    """Pre-calculates the SHA-256 hashes for all known regions."""
    lookup = {}
    for internal_name, human_name in AUTHORIZED_MAP.items():
        # Parla uses standard SHA-256 for region hashing
        region_hash = hashlib.sha256(internal_name.encode('utf-8')).hexdigest()
        lookup[region_hash] = human_name
    return lookup

def decode_ledger_report(days=90):
    """
    Pulls the hashed risk report from the ledger and translates it 
    using the Authorized Lookup Table.
    """
    print("=" * 70)
    print("AUTHORIZED DECODER: TRANSLATING ZERO-TRUST LEDGER")
    print("=" * 70)
    
    # 1. Get the secure lookup dictionary
    secure_lookup = generate_hash_lookup()
    
    # 2. Pull the hashed data from the ledger
    mapper = RegionalRiskMapper()
    report = mapper.calculate_regional_risk(days=days)
    
    print(f"\nDECRYPTED HUMANITARIAN RISK REPORT (Last {days} Days)")
    print("-" * 70)
    
    if not report['regions']:
        print("No events recorded.")
        return

    # 3. Translate and display
    for region in report['regions']:
        raw_hash = region['region_hash']
        
        # Look up the human-readable name
        human_name = secure_lookup.get(raw_hash, "UNKNOWN / UNMAPPED REGION")
        
        print(f"\nLOCATION: {human_name}")
        print(f"   |-- Cryptographic Hash: {raw_hash}")
        print(f"   |-- Risk Score: {region['risk_score']}")
        print(f"   |-- Total Events: {region['total_events']}")
        print(f"   +-- Latest Activity: {region['latest_activity']}")
        
        print(f"   +-- Threat Breakdown:")
        for evt, count in region['event_breakdown'].items():
            print(f"      * {evt}: {count} incidents")

if __name__ == "__main__":
    decode_ledger_report(days=90)
