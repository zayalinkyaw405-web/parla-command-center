"""
parla/domains/risk_mapper.py
Regional Risk Mapping & Aggregation Engine
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
from pathlib import Path

# Risk weights for different event types
RISK_WEIGHTS = {
    "AIRSTRIKE": 10.0,
    "GROUND_CONFLICT": 7.0,
    "DISPLACEMENT": 5.0,
    "HUMANITARIAN_CRISIS": 8.0,
    "ARTILLERY_SHELLING": 7.5,
    "CIVIC_INFRASTRUCTURE_ATTACK": 9.0,
    "UNKNOWN": 1.0
}

class RegionalRiskMapper:
    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.db_path = str(project_root / "Data" / "parla_ledger.db")
        else:
            self.db_path = db_path

    def _get_recent_events(self, days: int = 30) -> List[Dict[str, Any]]:
        """Fetch recent OSINT events from the ledger."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT payload_json, domain FROM ledger_blocks 
                WHERE domain = 'osint_nlp'
                ORDER BY timestamp DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                try:
                    payload = json.loads(row['payload_json'])
                    if 'structured_event' in payload:
                        events.append(payload['structured_event'])
                    elif 'event' in payload:
                        events.append(payload['event'])
                except (json.JSONDecodeError, KeyError):
                    continue
                    
            return events
            
        except sqlite3.OperationalError as e:
            print(f"[!] Warning: Could not connect to {self.db_path}. Error: {e}")
            return []

    def calculate_regional_risk(self, days: int = 30) -> Dict[str, Any]:
        """Aggregate events by region_hash and calculate risk score."""
        events = self._get_recent_events(days)
        
        region_data = defaultdict(lambda: {
            "total_events": 0,
            "risk_score": 0.0,
            "event_breakdown": defaultdict(int),
            "latest_event_date": None
        })
        
        for event in events:
            region_hash = event.get("region_hash", "UNKNOWN_REGION")
            event_type = event.get("event_type", "UNKNOWN")
            confidence = event.get("confidence", 0.5)
            timeframe = event.get("timeframe", "UNKNOWN")
            
            weight = RISK_WEIGHTS.get(event_type, 1.0)
            risk_contribution = weight * confidence
            
            region_data[region_hash]["total_events"] += 1
            region_data[region_hash]["risk_score"] += risk_contribution
            region_data[region_hash]["event_breakdown"][event_type] += 1
            
            if timeframe != "UNKNOWN":
                current_latest = region_data[region_hash]["latest_event_date"]
                if current_latest is None or timeframe > current_latest:
                    region_data[region_hash]["latest_event_date"] = timeframe

        risk_report = {
            "generated_at": datetime.now().isoformat(),
            "analysis_window_days": days,
            "total_regions_monitored": len(region_data),
            "regions": []
        }
        
        for region_hash, data in region_data.items():
            risk_report["regions"].append({
                "region_hash": region_hash,
                "risk_score": round(data["risk_score"], 2),
                "total_events": data["total_events"],
                "event_breakdown": dict(data["event_breakdown"]),
                "latest_activity": data["latest_event_date"]
            })
            
        risk_report["regions"].sort(key=lambda x: x["risk_score"], reverse=True)
        
        return risk_report

    def generate_digest(self, days: int = 30) -> str:
        """Generate plain-language digest."""
        report = self.calculate_regional_risk(days)
        
        if not report["regions"]:
            return "No OSINT events recorded in the ledger for the specified window."
            
        highest_risk = report["regions"][0]
        
        digest = (
            f"HUMANITARIAN RISK DIGEST (Last {days} Days)\n"
            f"--------------------------------------------------\n"
            f"Total Regions Monitored: {report['total_regions_monitored']}\n"
            f"Highest Risk Region Hash: {highest_risk['region_hash']}\n"
            f"Risk Score: {highest_risk['risk_score']}/100\n"
            f"Primary Threat: {max(highest_risk['event_breakdown'], key=highest_risk['event_breakdown'].get)}\n"
            f"Latest Activity: {highest_risk['latest_activity']}\n"
            f"--------------------------------------------------\n"
            f"Actionable Directive: Humanitarian partners should prioritize resource allocation \n"
            f"and early-warning sensor deployment to the highest-risk hashed regions. \n"
            f"Exact locations remain cryptographically protected."
        )
        return digest


if __name__ == "__main__":
    mapper = RegionalRiskMapper()
    
    print("=" * 60)
    print("🗺️ REGIONAL RISK MAPPING ENGINE")
    print("=" * 60)
    
    print("\n[1] Calculating Regional Risk Scores...")
    report = mapper.calculate_regional_risk(days=30)
    print(json.dumps(report, indent=2))
    
    print("\n[2] Generating Humanitarian Digest...")
    print("-" * 60)
    print(mapper.generate_digest(days=30))
    print("-" * 60)