"""
parla_varla_core/wrappers/varla_geo.py
======================================
Varla (Red Team) Adversarial Geolocation & EXIF Spoofing/Spoof Detection Module.
Generates GPS drift offsets, EXIF coordinate manipulation vectors, and deepfake alert flags.
"""

import json
import time
import math
import hashlib
from typing import Dict, Any

class VarlaGeoEngine:
    """
    Adversarial OSINT Geolocation Engine.
    Simulates EXIF coordinate manipulation, GPS location offset, and deepfake imagery alerts.
    """
    def __init__(self, secret_key: str = "void_node_secret_key_2026"):
        self.secret_key = secret_key.encode("utf-8")

    def synthesize_spoof_vectors(self, original_lat: float, original_lng: float, drift_km: float = 12.5) -> Dict[str, Any]:
        """
        Synthesizes adversarial EXIF drift and geo-spoofing indicators to stress-test Parla.
        """
        # 1 degree latitude ~ 111 km
        lat_offset = drift_km / 111.0
        lng_offset = drift_km / (111.0 * math.cos(math.radians(original_lat)))

        spoofed_lat = original_lat + lat_offset
        spoofed_lng = original_lng + lng_offset

        payload_data = json.dumps({
            "original": [original_lat, original_lng],
            "spoofed": [spoofed_lat, spoofed_lng],
            "drift_km": drift_km,
            "adversarial_flag": "EXIF_LOCATION_MUTATED"
        }, sort_keys=True)

        payload_hash = hashlib.sha256(payload_data.encode('utf-8')).hexdigest()
        mac_hasher = hashlib.sha256()
        mac_hasher.update(self.secret_key)
        mac_hasher.update(payload_data.encode('utf-8'))

        return {
            "geo_id": f"varla_geo_{int(time.time())}",
            "personality": "VARLA_ADVERSARIAL",
            "original_lat": original_lat,
            "original_lng": original_lng,
            "spoofed_lat": round(spoofed_lat, 6),
            "spoofed_lng": round(spoofed_lng, 6),
            "drift_km": round(drift_km, 2),
            "exif_tampered": True,
            "deepfake_alert": True,
            "sha256_root": payload_hash,
            "hmac_signature": mac_hasher.hexdigest(),
            "timestamp": time.time()
        }
