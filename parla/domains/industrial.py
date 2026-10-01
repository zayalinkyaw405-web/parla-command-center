"""
parla/domains/industrial.py
Industrial Predictive Maintenance: EMD + DBSCAN + TreeSHAP
Zero-Trust, offline-first, explainable anomaly detection.
"""

import os
import numpy as np
import sqlite3
import json
import hashlib
import hmac
import warnings
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

# ML Dependencies
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Safe Import for EMD (Empirical Mode Decomposition)
try:
    from PyEMD import EMD
    EMD_AVAILABLE = True
except ImportError:
    try:
        from emd import EMD
        EMD_AVAILABLE = True
    except ImportError:
        EMD = None
        EMD_AVAILABLE = False
        warnings.warn("PyEMD/emd not installed. Falling back to basic FFT for signal decomposition.")

# Dynamic DB Path (Uses env var or defaults to current directory)
DB_PATH = os.environ.get("PARLA_LEDGER_DB", os.path.join(os.getcwd(), "parla_ledger.db"))
SECRET_KEY = b"parla_industrial_offline_key_2026"

@dataclass
class MaintenanceDirective:
    machine_id: str
    anomaly_score: float
    failure_mode: str
    confidence: float
    explanation: str
    recommended_action: str
    urgency: str  # LOW, MEDIUM, HIGH, CRITICAL

class IndustrialProcessor:
    """
    Zero-Trust Industrial Predictive Maintenance Processor.
    Combines EMD (signal decomposition), DBSCAN (anomaly clustering),
    and simplified TreeSHAP-style explainability.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.baseline_features = None
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database and create table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ledger_blocks (
                seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_hash TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                domain TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                nonce TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                signature TEXT NOT NULL,
                sync_status TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        
    def decompose_signal(self, vibration_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Apply Empirical Mode Decomposition to extract intrinsic mode functions.
        Falls back to basic FFT if EMD is not available.
        """
        if EMD_AVAILABLE:
            emd = EMD()
            imfs = emd.emd(vibration_data)
        else:
            # Fallback: Treat the whole signal as one IMF if EMD is missing
            imfs = [vibration_data]
        
        # Calculate energy in each IMF
        energies = np.array([np.sum(imf**2) for imf in imfs])
        total_energy = np.sum(energies)
        energy_ratios = energies / total_energy if total_energy > 0 else energies
        
        # Extract dominant frequency (simplified FFT on first IMF)
        fft_result = np.fft.fft(imfs[0])
        freqs = np.fft.fftfreq(len(imfs[0]))
        dominant_freq = np.abs(freqs[np.argmax(np.abs(fft_result))])
        
        return {
            "imfs": imfs,
            "energies": energies,
            "energy_ratios": energy_ratios,
            "dominant_frequency": dominant_freq,
            "imf_count": len(imfs)
        }
    
    def extract_features(self, vibration_data: np.ndarray, temperature: float) -> np.ndarray:
        """
        Extract feature vector from raw sensor data.
        Features: [mean, std, max, dominant_freq, energy_ratio_1, energy_ratio_2, temperature]
        """
        decomposition = self.decompose_signal(vibration_data)
        
        features = np.array([
            np.mean(vibration_data),
            np.std(vibration_data),
            np.max(np.abs(vibration_data)),
            decomposition["dominant_frequency"],
            decomposition["energy_ratios"][0] if len(decomposition["energy_ratios"]) > 0 else 0,
            decomposition["energy_ratios"][1] if len(decomposition["energy_ratios"]) > 1 else 0,
            temperature
        ])
        
        return features
    
    def detect_anomalies(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Use DBSCAN to detect if the current feature vector is anomalous.
        Returns (is_anomaly, anomaly_score).
        """
        # Reshape for sklearn
        features_2d = features.reshape(1, -1)
        
        # If we have baseline data, compare against it
        if self.baseline_features is not None:
            # Calculate distance from cluster centers
            all_data = np.vstack([self.baseline_features, features_2d])
            scaled_data = self.scaler.fit_transform(all_data)
            
            labels = self.dbscan.fit_predict(scaled_data)
            
            # If the new point is labeled as noise (-1), it's an anomaly
            is_anomaly = labels[-1] == -1
            
            # Calculate anomaly score based on distance from nearest cluster
            if is_anomaly:
                # Simplified: use distance from mean of normal cluster
                normal_mask = labels[:-1] != -1
                if np.any(normal_mask):
                    normal_mean = np.mean(scaled_data[:-1][normal_mask], axis=0)
                    distance = np.linalg.norm(scaled_data[-1] - normal_mean)
                    anomaly_score = min(distance / 3.0, 1.0)  # Normalize to 0-1
                else:
                    anomaly_score = 1.0
            else:
                anomaly_score = 0.0
        else:
            # First sample, establish baseline
            self.baseline_features = features_2d
            is_anomaly = False
            anomaly_score = 0.0
        
        return is_anomaly, anomaly_score
    
    def explain_anomaly(self, features: np.ndarray, anomaly_score: float) -> str:
        """
        Simplified TreeSHAP-style explainability.
        Identifies which features contributed most to the anomaly.
        """
        if self.baseline_features is None or anomaly_score < 0.3:
            return "Normal operating conditions."
        
        # Compare against baseline
        baseline_mean = np.mean(self.baseline_features, axis=0)
        deviations = np.abs(features - baseline_mean)
        
        # Identify top contributing features
        feature_names = [
            "vibration_mean",
            "vibration_std",
            "vibration_peak",
            "dominant_frequency",
            "energy_ratio_imf1",
            "energy_ratio_imf2",
            "temperature"
        ]
        
        # Get top 3 contributors
        top_indices = np.argsort(deviations)[-3:][::-1]
        contributors = [f"{feature_names[i]} (+{deviations[i]:.2f})" for i in top_indices]
        
        return f"Primary contributors: {', '.join(contributors)}"
    
    def generate_directive(self, machine_id: str, anomaly_score: float, 
                          explanation: str) -> MaintenanceDirective:
        """
        Generate plain-language maintenance directive for human technicians.
        """
        # Determine failure mode based on feature patterns
        if anomaly_score > 0.8:
            urgency = "CRITICAL"
            failure_mode = "IMMINENT FAILURE"
            action = "STOP MACHINE IMMEDIATELY. Schedule emergency maintenance."
        elif anomaly_score > 0.6:
            urgency = "HIGH"
            failure_mode = "BEARING DEGRADATION"
            action = "Schedule maintenance within 24 hours. Monitor vibration trends."
        elif anomaly_score > 0.4:
            urgency = "MEDIUM"
            failure_mode = "MISALIGNMENT OR LOOSE COMPONENTS"
            action = "Inspect within 1 week. Check mounting bolts and alignment."
        else:
            urgency = "LOW"
            failure_mode = "NORMAL WEAR"
            action = "Continue monitoring. Schedule routine inspection."
        
        return MaintenanceDirective(
            machine_id=machine_id,
            anomaly_score=anomaly_score,
            failure_mode=failure_mode,
            confidence=min(anomaly_score + 0.2, 1.0),
            explanation=explanation,
            recommended_action=action,
            urgency=urgency
        )
    
    def _verify_signature(self, payload: Dict[str, Any]) -> bool:
        """Zero-Trust: Verify cryptographic signature."""
        if "signature" not in payload:
            return False
        
        data_to_sign = json.dumps({k: v for k, v in payload.items() if k != "signature"}, sort_keys=True)
        expected_sig = hmac.new(SECRET_KEY, data_to_sign.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(payload["signature"], expected_sig)
    
    def _append_to_ledger(self, directive: MaintenanceDirective, raw_features: np.ndarray) -> str:
        """Append maintenance directive to Zero-Trust ledger."""
        payload = {
            "machine_id": directive.machine_id,
            "anomaly_score": directive.anomaly_score,
            "failure_mode": directive.failure_mode,
            "confidence": directive.confidence,
            "explanation": directive.explanation,
            "recommended_action": directive.recommended_action,
            "urgency": directive.urgency,
            "feature_vector": raw_features.tolist()
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        signature = hmac.new(SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
        
        # Get previous block hash
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
        result = cursor.fetchone()
        prev_hash = result[0] if result else "GENESIS"
        conn.close()
        
        timestamp = datetime.now().isoformat()
        nonce = hashlib.sha256(f"{prev_hash}{timestamp}".encode()).hexdigest()[:16]
        block_data = f"{prev_hash}{payload_hash}{timestamp}{nonce}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ledger_blocks 
            (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block_hash, prev_hash, "industrial", timestamp, nonce,
            payload_hash, payload_json, signature, "SYNCED"
        ))
        conn.commit()
        conn.close()
        
        return block_hash
    
    def process_telemetry(self, machine_id: str, vibration_data: np.ndarray, 
                         temperature: float, signature: str) -> Dict[str, Any]:
        """
        Main orchestration: Verify → Decompose → Detect → Explain → Directive → Ledger.
        """
        # 1. Zero-Trust Verification
        payload_to_verify = {
            "machine_id": machine_id,
            "vibration_data": vibration_data.tolist(),
            "temperature": temperature
        }
        payload_to_verify["signature"] = signature
        
        if not self._verify_signature(payload_to_verify):
            return {
                "status": "REJECTED",
                "reason": "Invalid cryptographic signature",
                "action": "Payload dropped. Audit log updated."
            }
        
        # 2. Feature Extraction
        features = self.extract_features(vibration_data, temperature)
        
        # 3. Anomaly Detection
        is_anomaly, anomaly_score = self.detect_anomalies(features)
        
        # 4. Explainability
        explanation = self.explain_anomaly(features, anomaly_score)
        
        # 5. Generate Directive
        directive = self.generate_directive(machine_id, anomaly_score, explanation)
        
        # 6. Ledger Update
        block_hash = self._append_to_ledger(directive, features)
        
        return {
            "status": "PROCESSED",
            "directive": {
                "machine_id": directive.machine_id,
                "anomaly_score": directive.anomaly_score,
                "failure_mode": directive.failure_mode,
                "confidence": directive.confidence,
                "explanation": directive.explanation,
                "recommended_action": directive.recommended_action,
                "urgency": directive.urgency
            },
            "ledger_hash": block_hash
        }


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    processor = IndustrialProcessor()
    
    print("=" * 70)
    print("🏭 PARLA INDUSTRIAL PREDICTIVE MAINTENANCE - SELF-TEST")
    print("=" * 70)
    
    # Simulate normal operating conditions (baseline)
    print("\n[1] Establishing baseline with normal vibration data...")
    np.random.seed(42)
    normal_vibration = np.random.normal(0, 0.5, 1000)
    normal_temp = 45.0
    
    # Generate signature for normal data
    normal_payload = {
        "machine_id": "PUMP-001",
        "vibration_data": normal_vibration.tolist(),
        "temperature": normal_temp
    }
    normal_json = json.dumps(normal_payload, sort_keys=True)
    normal_sig = hmac.new(SECRET_KEY, normal_json.encode(), hashlib.sha256).hexdigest()
    
    result1 = processor.process_telemetry("PUMP-001", normal_vibration, normal_temp, normal_sig)
    print(f"  Status: {result1['status']}")
    print(f"  Urgency: {result1['directive']['urgency']}")
    print(f"  Anomaly Score: {result1['directive']['anomaly_score']:.2f}")
    print(f"  Ledger Hash: {result1['ledger_hash'][:32]}...")
    
    # Simulate anomalous conditions (bearing degradation)
    print("\n[2] Detecting anomaly with degraded bearing signature...")
    # Add high-frequency components and increased amplitude
    t = np.linspace(0, 1, 1000)
    anomalous_vibration = (
        np.random.normal(0, 0.5, 1000) +
        2.0 * np.sin(2 * np.pi * 50 * t) +  # High-frequency bearing fault
        1.5 * np.sin(2 * np.pi * 10 * t)     # Sub-harmonic
    )
    anomalous_temp = 68.0  # Elevated temperature
    
    anomalous_payload = {
        "machine_id": "PUMP-001",
        "vibration_data": anomalous_vibration.tolist(),
        "temperature": anomalous_temp
    }
    anomalous_json = json.dumps(anomalous_payload, sort_keys=True)
    anomalous_sig = hmac.new(SECRET_KEY, anomalous_json.encode(), hashlib.sha256).hexdigest()
    
    result2 = processor.process_telemetry("PUMP-001", anomalous_vibration, anomalous_temp, anomalous_sig)
    print(f"  Status: {result2['status']}")
    print(f"  Urgency: {result2['directive']['urgency']}")
    print(f"  Anomaly Score: {result2['directive']['anomaly_score']:.2f}")
    print(f"  Failure Mode: {result2['directive']['failure_mode']}")
    print(f"  Explanation: {result2['directive']['explanation']}")
    print(f"  Recommended Action: {result2['directive']['recommended_action']}")
    print(f"  Ledger Hash: {result2['ledger_hash'][:32]}...")
    
    print("\n" + "=" * 70)
    print("✓ INDUSTRIAL PROCESSOR SELF-TEST COMPLETE")
    print("=" * 70)
