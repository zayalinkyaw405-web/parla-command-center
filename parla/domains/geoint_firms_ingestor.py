"""
parla/domains/geoint_firms_ingestor.py
NASA FIRMS (Fire Information for Resource Management System) GEOINT Ingestor.
Processes thermal anomalies (VIIRS 375m & MODIS 1km) to corroborate kinetic events (bombings, shelling, burnings).
Includes geofence fuzzing, Haversine space-time proximity matching, and Admiralty linkage.
"""

import math
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ThermalAnomaly:
    latitude: float
    longitude: float
    brightness_kelvin: float
    acquisition_time: str      # ISO-8601 string
    satellite: str             # "VIIRS_NPP", "VIIRS_NOAA20", "MODIS_TERRA"
    confidence_level: str      # "low", "nominal", "high"
    frp_mw: float              # Fire Radiative Power in MegaWatts
    sector_hash: str

class GEOINTFirmsIngestor:
    """
    Ingests and queries NASA FIRMS satellite thermal anomaly data.
    Corroborates conflict events by verifying elevated thermal radiance
    within spatial radius R and temporal window Delta T.
    """

    def __init__(self, salt: str = "parla_firms_salt_2026"):
        self.salt = salt
        self.anomalies: List[ThermalAnomaly] = []

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two GPS coordinates in kilometers."""
        radius_earth = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return radius_earth * c

    def compute_sector_hash(self, lat: float, lon: float) -> str:
        """
        Geofence Fuzzing (The Void Pillar):
        Converts exact micro-coordinates into generalized 0.1-degree sector hashes (~11 km grid)
        to prevent adversary location pinpointing.
        """
        coarse_lat = round(lat, 1)
        coarse_lon = round(lon, 1)
        data = f"{coarse_lat}:{coarse_lon}:{self.salt}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()[:16]

    def add_anomaly(
        self,
        lat: float,
        lon: float,
        brightness_k: float,
        acq_time: str,
        satellite: str = "VIIRS_NOAA20",
        confidence: str = "high",
        frp_mw: float = 12.5
    ) -> ThermalAnomaly:
        """Registers a thermal anomaly into memory."""
        sector = self.compute_sector_hash(lat, lon)
        anomaly = ThermalAnomaly(
            latitude=lat,
            longitude=lon,
            brightness_kelvin=brightness_k,
            acquisition_time=acq_time,
            satellite=satellite,
            confidence_level=confidence,
            frp_mw=frp_mw,
            sector_hash=sector
        )
        self.anomalies.append(anomaly)
        return anomaly

    def parse_firms_csv_row(self, row: Dict[str, str]) -> Optional[ThermalAnomaly]:
        """Parses a standard NASA FIRMS CSV row."""
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            bright = float(row.get("bright_ti4", row.get("brightness", 320.0)))
            acq_date = row.get("acq_date", "2026-01-01")
            acq_time = row.get("acq_time", "0000").zfill(4)
            hour = int(acq_time[:2])
            minute = int(acq_time[2:])
            dt_str = f"{acq_date}T{hour:02d}:{minute:02d}:00Z"
            sat = row.get("satellite", "VIIRS_NPP")
            conf = row.get("confidence", "nominal")
            frp = float(row.get("frp", 10.0))
            return self.add_anomaly(lat, lon, bright, dt_str, sat, conf, frp)
        except Exception:
            return None

    def corroborate_event(
        self,
        target_lat: float,
        target_lon: float,
        target_time_iso: str,
        radius_km: float = 15.0,
        window_hours: float = 6.0
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Space-Time Corroboration Engine:
        Matches a ground/airstrike claim against FIRMS thermal detections.
        Returns (corroborated_flag, matching_details).
        """
        try:
            # Parse ISO timestamp (handling trailing Z)
            clean_time = target_time_iso.replace("Z", "+00:00")
            target_dt = datetime.fromisoformat(clean_time)
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
        except Exception:
            target_dt = datetime.now(timezone.utc)

        best_match = None
        min_dist = float("inf")

        for anomaly in self.anomalies:
            dist = self.haversine_km(target_lat, target_lon, anomaly.latitude, anomaly.longitude)
            if dist <= radius_km:
                try:
                    anom_time = anomaly.acquisition_time.replace("Z", "+00:00")
                    anom_dt = datetime.fromisoformat(anom_time)
                    if anom_dt.tzinfo is None:
                        anom_dt = anom_dt.replace(tzinfo=timezone.utc)
                    time_diff = abs((target_dt - anom_dt).total_seconds()) / 3600.0
                except Exception:
                    time_diff = 0.0

                if time_diff <= window_hours:
                    if dist < min_dist:
                        min_dist = dist
                        best_match = {
                            "modality": "GEOINT_THERMAL",
                            "satellite": anomaly.satellite,
                            "brightness_kelvin": anomaly.brightness_kelvin,
                            "distance_km": round(dist, 2),
                            "time_delta_hours": round(time_diff, 2),
                            "frp_mw": anomaly.frp_mw,
                            "sector_hash": anomaly.sector_hash,
                            "detection_confidence": anomaly.confidence_level
                        }

        if best_match:
            return True, best_match
        return False, None
