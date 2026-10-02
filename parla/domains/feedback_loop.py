"""
parla/domains/feedback_loop.py
Reinforcement Learning Feedback Loop & Adaptive Parameter Tuning.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FeedbackSignal:
    event_id: str
    original_prediction: str
    true_label: str
    reward: float  # +1.0 for correct, -1.0 for incorrect
    confidence: float

class FeedbackLoop:
    """
    Implements a simple but effective Reinforcement Learning loop.
    Uses reward signals to adaptively tune anomaly detection and classification thresholds.
    """
    
    def __init__(self, kb_dir: str = "Project"):
        self.kb_dir = kb_dir
        self.learning_log_path = os.path.join(kb_dir, "rl_learning_log.md")
        os.makedirs(kb_dir, exist_ok=True)
        
        # Adaptive Parameters (Initial State)
        self.dbscan_eps = 0.5       # DBSCAN neighborhood radius
        self.classification_threshold = 0.6 # Confidence threshold for alerts
        self.reward_history: List[float] = []
        
    def process_feedback(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """
        Ingests human/system feedback and updates model parameters.
        """
        self.reward_history.append(signal.reward)
        
        # Keep a rolling window of the last 50 feedback signals
        if len(self.reward_history) > 50:
            self.reward_history.pop(0)
            
        # Calculate average recent reward
        avg_reward = sum(self.reward_history) / len(self.reward_history)
        
        # ADAPTIVE TUNING LOGIC
        # If avg reward is negative, the model is making too many false positives/negatives.
        # We adjust the DBSCAN epsilon to be more/less sensitive.
        if avg_reward < -0.2:
            # Too many false positives (flagging normal as anomaly). Increase eps to cluster tighter.
            self.dbscan_eps = min(self.dbscan_eps * 1.1, 2.0) 
            adjustment = "Increased DBSCAN eps (reduced sensitivity)"
        elif avg_reward > 0.5:
            # Model is doing well, can afford to be slightly more sensitive to catch subtle anomalies.
            self.dbscan_eps = max(self.dbscan_eps * 0.95, 0.1)
            adjustment = "Decreased DBSCAN eps (increased sensitivity)"
        else:
            adjustment = "Parameters stable"
            
        # Log the learning event to the Knowledge Base (SKILL.md Module 2)
        self._log_learning_event(signal, avg_reward, adjustment)
        
        return {
            "status": "LEARNED",
            "event_id": signal.event_id,
            "new_dbscan_eps": round(self.dbscan_eps, 4),
            "avg_recent_reward": round(avg_reward, 4),
            "adjustment_made": adjustment
        }

    def _log_learning_event(self, signal: FeedbackSignal, avg_reward: float, adjustment: str):
        """Appends RL learning metrics to the project documentation."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (
            f"- **Timestamp**: {timestamp}\n"
            f"- **Event ID**: `{signal.event_id}`\n"
            f"- **Correction**: Predicted `{signal.original_prediction}` -> True Label `{signal.true_label}`\n"
            f"- **Reward Signal**: `{signal.reward}`\n"
            f"- **Rolling Avg Reward**: `{round(avg_reward, 4)}`\n"
            f"- **System Adaptation**: {adjustment}\n\n"
        )
        
        if not os.path.exists(self.learning_log_path):
            with open(self.learning_log_path, "w", encoding="utf-8") as f:
                f.write("# Parla RL Learning Log\n\n## Adaptive Parameter Updates\n" + entry)
        else:
            with open(self.learning_log_path, "a", encoding="utf-8") as f:
                f.write(f"\n## Adaptive Parameter Updates\n{entry}")
                
        logger.info(f"Feedback processed. New DBSCAN eps: {self.dbscan_eps}")# ============================================================
# SELF-TEST & EXECUTION
# ============================================================

if __name__ == "__main__":
    # Initialize the loop
    loop = FeedbackLoop()
    
    print("=" * 70)
    print("🧠 PARLA RL FEEDBACK LOOP - SELF-TEST")
    print("=" * 70)
    
    # 1. Simulate a False Positive (Operator corrects the AI)
    print("\n[1] Simulating Operator Correction (False Positive)...")
    signal_1 = FeedbackSignal(
        event_id="EVT-998",
        original_prediction="KINETIC_CONFLICT",
        true_label="NORMAL_WEATHER",
        reward=-1.0,
        confidence=0.85
    )
    result_1 = loop.process_feedback(signal_1)
    print(f"  Status: {result_1['status']}")
    print(f"  Adjustment: {result_1['adjustment_made']}")
    print(f"  New DBSCAN eps: {result_1['new_dbscan_eps']}")
    
    # 2. Simulate a series of correct predictions to trigger positive adaptation
    print("\n[2] Simulating 5 Correct Predictions (High Confidence)...")
    for i in range(5):
        signal_correct = FeedbackSignal(
            event_id=f"EVT-{1000+i}",
            original_prediction="LOGISTICS_SUPPLY",
            true_label="LOGISTICS_SUPPLY",
            reward=1.0,
            confidence=0.95
        )
        result = loop.process_feedback(signal_correct)
        
    print(f"  Final Adjustment: {result['adjustment_made']}")
    print(f"  Final DBSCAN eps: {result['new_dbscan_eps']}")
    
    print("\n" + "=" * 70)
    print("✓ FEEDBACK LOOP SELF-TEST COMPLETE.")
    print("✓ Check Project/rl_learning_log.md for the audit trail.")
    print("=" * 70)
