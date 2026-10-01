"""
parla/core/feedback_loop.py
Human-in-the-Loop Feedback & Adaptive Threshold Adjustment
Stores operator corrections immutably and auto-adjusts confidence weights.
"""

import sqlite3
import json
import hashlib
import hmac
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Database path - auto-detect relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "parla_ledger.db")

SECRET_KEY = b"parla_feedback_loop_key_2026"


class FeedbackLoop:
    """
    Human-in-the-Loop Feedback Module.
    
    Records operator confirmations/rejections immutably in the ledger
    and automatically adjusts confidence thresholds based on historical accuracy.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path else DB_PATH
        self._validate_database()
    
    def _validate_database(self):
        """Ensure the database exists and has the required table."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"Ledger database not found at: {self.db_path}\n"
                f"Run the stress test or OSINT injector first to create the ledger."
            )
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ledger_blocks'")
            if not cursor.fetchone():
                raise ValueError("ledger_blocks table does not exist in database")
            conn.close()
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Database connection failed: {e}")
    
    def _get_current_tip_hash(self) -> str:
        """Get the latest block hash to maintain chain integrity."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "GENESIS"
        except sqlite3.OperationalError:
            return "GENESIS"
    
    def record_feedback(
        self,
        alert_id: str,
        event_type: str,
        original_confidence: float,
        operator_action: str,
        operator_reason: str = ""
    ) -> Dict[str, Any]:
        """
        Record human operator feedback immutably.
        
        Args:
            alert_id: Unique identifier for the alert being reviewed
            event_type: Type of event (AIRSTRIKE, GROUND_CONFLICT, etc.)
            original_confidence: The confidence score Parla assigned
            operator_action: "CONFIRM" or "REJECT"
            operator_reason: Optional explanation from the operator
        
        Returns:
            Dict with status, block_hash, and message
        """
        if operator_action not in ["CONFIRM", "REJECT"]:
            return {
                "status": "ERROR",
                "message": "operator_action must be 'CONFIRM' or 'REJECT'"
            }
        
        if not (0.0 <= original_confidence <= 1.0):
            return {
                "status": "ERROR",
                "message": "original_confidence must be between 0.0 and 1.0"
            }
        
        # Build feedback payload
        feedback_payload = {
            "alert_id": alert_id,
            "event_type": event_type,
            "original_confidence": original_confidence,
            "operator_action": operator_action,
            "operator_reason": operator_reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cryptographic signing
        payload_json = json.dumps(feedback_payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        signature = hmac.new(SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
        
        # Block construction
        prev_hash = self._get_current_tip_hash()
        timestamp = datetime.now().isoformat()
        nonce = hashlib.sha256(f"{prev_hash}{timestamp}{alert_id}".encode()).hexdigest()[:16]
        block_data = f"{prev_hash}{payload_hash}{timestamp}{nonce}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        # Insert into ledger
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ledger_blocks 
                (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                block_hash, prev_hash, "feedback", timestamp, nonce,
                payload_hash, payload_json, signature, "SYNCED"
            ))
            conn.commit()
            conn.close()
            
            # Trigger threshold recalculation
            new_thresholds = self._adjust_thresholds()
            
            return {
                "status": "SUCCESS",
                "block_hash": block_hash,
                "message": f"Feedback recorded. Thresholds recalculated.",
                "new_thresholds": new_thresholds
            }
            
        except sqlite3.OperationalError as e:
            return {
                "status": "ERROR",
                "message": f"Database write failed: {e}"
            }
    
    def _adjust_thresholds(self) -> Dict[str, float]:
        """
        Analyze historical feedback to adjust confidence thresholds.
        
        Uses a Bayesian-inspired approach:
        - High accuracy (many confirms) → Lower threshold (trust the detector)
        - Low accuracy (many rejects) → Higher threshold (require more evidence)
        
        Returns:
            Dict mapping event_type to recommended confidence threshold
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT payload_json FROM ledger_blocks WHERE domain = 'feedback'
            """)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {}
            
            # Parse feedback history
            feedback_history = []
            for row in rows:
                try:
                    feedback_history.append(json.loads(row['payload_json']))
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if not feedback_history:
                return {}
            
            # Aggregate stats per event type
            event_stats = {}
            for fb in feedback_history:
                evt = fb['event_type']
                if evt not in event_stats:
                    event_stats[evt] = {
                        "confirms": 0,
                        "rejects": 0,
                        "total_confidence": 0.0,
                        "count": 0
                    }
                
                event_stats[evt]["count"] += 1
                event_stats[evt]["total_confidence"] += fb['original_confidence']
                
                if fb['operator_action'] == "CONFIRM":
                    event_stats[evt]["confirms"] += 1
                else:
                    event_stats[evt]["rejects"] += 1
            
            # Calculate adjusted thresholds
            new_thresholds = {}
            for evt, stats in event_stats.items():
                total = stats["confirms"] + stats["rejects"]
                if total == 0:
                    continue
                
                accuracy = stats["confirms"] / total
                avg_confidence = stats["total_confidence"] / stats["count"]
                
                # Bayesian adjustment:
                # - If accuracy is high (>0.7), we can trust lower confidence scores
                # - If accuracy is low (<0.5), we need higher confidence to trigger alerts
                adjustment = (accuracy - 0.5) * 0.3  # Range: -0.15 to +0.15
                new_threshold = max(0.3, min(0.9, avg_confidence - adjustment))
                
                new_thresholds[evt] = round(new_threshold, 2)
            
            return new_thresholds
            
        except sqlite3.OperationalError:
            return {}
    
    def get_current_thresholds(self) -> Dict[str, float]:
        """
        Retrieve the dynamically adjusted confidence thresholds.
        
        Returns:
            Dict mapping event_type to required confidence threshold
        """
        return self._adjust_thresholds()
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all feedback recorded.
        
        Returns:
            Dict with total counts, accuracy rates, and per-event breakdown
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT payload_json FROM ledger_blocks WHERE domain = 'feedback'
            """)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {
                    "total_feedback": 0,
                    "confirms": 0,
                    "rejects": 0,
                    "overall_accuracy": 0.0,
                    "by_event_type": {}
                }
            
            feedback_history = []
            for row in rows:
                try:
                    feedback_history.append(json.loads(row['payload_json']))
                except (json.JSONDecodeError, KeyError):
                    continue
            
            total = len(feedback_history)
            confirms = sum(1 for fb in feedback_history if fb['operator_action'] == "CONFIRM")
            rejects = total - confirms
            accuracy = confirms / total if total > 0 else 0.0
            
            # Breakdown by event type
            by_event = {}
            for fb in feedback_history:
                evt = fb['event_type']
                if evt not in by_event:
                    by_event[evt] = {"confirms": 0, "rejects": 0}
                
                if fb['operator_action'] == "CONFIRM":
                    by_event[evt]["confirms"] += 1
                else:
                    by_event[evt]["rejects"] += 1
            
            return {
                "total_feedback": total,
                "confirms": confirms,
                "rejects": rejects,
                "overall_accuracy": round(accuracy, 2),
                "by_event_type": by_event
            }
            
        except sqlite3.OperationalError:
            return {"error": "Database connection failed"}


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔄 PARLA HUMAN-IN-THE-LOOP FEEDBACK LOOP - SELF-TEST")
    print("=" * 70)
    
    try:
        feedback = FeedbackLoop()
        print(f"\n✓ Connected to ledger: {feedback.db_path}")
        
        # Test 1: Record a REJECT (false positive)
        print("\n[1] Recording REJECT feedback (False Positive UAV detection)")
        result1 = feedback.record_feedback(
            alert_id="ALERT-001",
            event_type="UAV_DRONE",
            original_confidence=0.75,
            operator_action="REJECT",
            operator_reason="Confirmed as wind noise, not a drone."
        )
        print(f"  Status: {result1['status']}")
        if result1['status'] == "SUCCESS":
            print(f"  Block Hash: {result1['block_hash'][:32]}...")
            print(f"  Message: {result1['message']}")
        
        # Test 2: Record a CONFIRM (true positive)
        print("\n[2] Recording CONFIRM feedback (True Positive AIRSTRIKE)")
        result2 = feedback.record_feedback(
            alert_id="ALERT-002",
            event_type="AIRSTRIKE",
            original_confidence=0.88,
            operator_action="CONFIRM",
            operator_reason="Verified by secondary acoustic node and OSINT."
        )
        print(f"  Status: {result2['status']}")
        if result2['status'] == "SUCCESS":
            print(f"  Block Hash: {result2['block_hash'][:32]}...")
            print(f"  Message: {result2['message']}")
        
        # Test 3: Get adjusted thresholds
        print("\n[3] Dynamically Adjusted Confidence Thresholds")
        print("-" * 70)
        thresholds = feedback.get_current_thresholds()
        if thresholds:
            for evt, threshold in thresholds.items():
                print(f"  {evt:<20} : Required Confidence >= {threshold}")
        else:
            print("  No thresholds calculated yet (need more feedback data)")
        
        # Test 4: Get feedback summary
        print("\n[4] Feedback Summary")
        print("-" * 70)
        summary = feedback.get_feedback_summary()
        print(f"  Total Feedback: {summary['total_feedback']}")
        print(f"  Confirms: {summary['confirms']}")
        print(f"  Rejects: {summary['rejects']}")
        print(f"  Overall Accuracy: {summary['overall_accuracy']:.1%}")
        
        if summary['by_event_type']:
            print(f"\n  Breakdown by Event Type:")
            for evt, counts in summary['by_event_type'].items():
                total = counts['confirms'] + counts['rejects']
                accuracy = counts['confirms'] / total if total > 0 else 0
                print(f"    • {evt}: {counts['confirms']} confirms, {counts['rejects']} rejects ({accuracy:.0%} accuracy)")
        
        print("\n" + "=" * 70)
        print("✓ FEEDBACK LOOP SELF-TEST COMPLETE")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTo fix this, run one of these first:")
        print("  1. python inject_osint_events.py")
        print("  2. python parla/domains/industrial.py")
        print("  3. Any script that creates the ledger_blocks table")
    
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()