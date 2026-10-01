"""
enhanced_risk_analysis.py
90-Day Temporal & Escalation Analysis for Regional Risk
Strictly privacy-preserving (uses region hashes only).
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = "c:/Users/james/VuZiNat/iot_agent/Data/parla_ledger.db"

def analyze_90_day_trends():
    print("=" * 70)
    print("🗺️ 90-DAY ENHANCED REGIONAL RISK & TEMPORAL ANALYSIS")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        
        query = """
            SELECT payload_json, timestamp FROM ledger_blocks 
            WHERE domain = 'osint_nlp' AND timestamp >= ?
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (cutoff,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n[!] No OSINT events found in the ledger for the last 90 days.")
            return
            
        events = []
        for row in rows:
            try:
                payload = json.loads(row['payload_json'])
                if 'event' in payload:
                    event = payload['event']
                    event['timestamp'] = row['timestamp']
                    events.append(event)
            except (json.JSONDecodeError, KeyError):
                continue

        print(f"\n[✓] Analyzed {len(events)} verified events over the last 90 days.")
        print("-" * 70)

        # 1. TEMPORAL DENSITY
        print("\n📅 1. TEMPORAL DENSITY (Events per 15-day period)")
        periods = defaultdict(int)
        for event in events:
            try:
                dt = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                period_num = (dt.day - 1) // 15 + 1
                month_key = dt.strftime("%Y-%m")
                if period_num == 1:
                    periods[f"{month_key} (Days 1-15)"] += 1
                else:
                    periods[f"{month_key} (Days 16-31)"] += 1
            except (ValueError, KeyError):
                continue
                
        for period, count in sorted(periods.items()):
            bar = "█" * count
            print(f"  {period:<20} | {bar} ({count} events)")

        # 2. THREAT ESCALATION (First 45 vs Last 45 days)
        print("\n📈 2. THREAT ESCALATION ANALYSIS")
        mid_index = len(events) // 2
        first_half = events[:mid_index]
        second_half = events[mid_index:]
        
        # Score: AIRSTRIKE=10, other=5
        first_score = sum(10 if e.get("event_type") == "AIRSTRIKE" else 5 for e in first_half)
        second_score = sum(10 if e.get("event_type") == "AIRSTRIKE" else 5 for e in second_half)
        
        change = ((second_score - first_score) / max(first_score, 1)) * 100
        trend_icon = "🔴" if change > 10 else ("🟢" if change < -10 else "🟡")
        trend_text = "ESCALATING" if change > 10 else ("STABILIZING" if change < -10 else "STABLE")
        
        print(f"  First 45 Days Risk Index : {first_score}")
        print(f"  Last 45 Days Risk Index  : {second_score}")
        print(f"  Trend                    : {trend_icon} {trend_text} ({change:+.1f}%)")

        # 3. REGIONAL EVENT DENSITY
        print("\n🎯 3. REGIONAL EVENT CLUSTERING")
        region_clusters = defaultdict(lambda: {"count": 0, "primary": "", "latest": ""})
        
        for event in events:
            region_hash = event.get("region_hash", "UNKNOWN")
            event_type = event.get("event_type", "UNKNOWN")
            timestamp = event.get("timeframe", "")
            
            region_clusters[region_hash]["count"] += 1
            if timestamp > region_clusters[region_hash]["latest"]:
                region_clusters[region_hash]["latest"] = timestamp
            
            # Track primary event type
            if region_clusters[region_hash]["primary"] == "":
                region_clusters[region_hash]["primary"] = event_type
                
        # Sort by density (most events first)
        sorted_regions = sorted(region_clusters.items(), key=lambda x: x[1]["count"], reverse=True)
        
        for i, (r_hash, data) in enumerate(sorted_regions[:5], 1):
            print(f"\n  [{i}] Region Hash: {r_hash}")
            print(f"      Density     : {data['count']} events (High clustering)" if data['count'] >= 3 else f"      Density     : {data['count']} events")
            print(f"      Primary Event: {data['primary']}")
            print(f"      Latest      : {data['latest']}")

        # 4. HUMANITARIAN ACTIONABLE DIRECTIVE
        print("\n" + "=" * 70)
        print("🛡️ HUMANITARIAN ACTIONABLE DIRECTIVE (90-DAY)")
        print("=" * 70)
        
        if sorted_regions:
            top_region = sorted_regions[0]
            print(f"Based on 90-day telemetry, Region {top_region[0]} exhibits the highest event")
            print(f"density ({top_region[1]['count']} events), primarily driven by {top_region[1]['primary']}.")
        else:
            print("No regional data available to determine specific location.")
            
        print(f"Current trend is {trend_text.replace('🔴 ', '').replace('🟢 ', '').replace('🟡 ', '')}.")
        print("\nRECOMMENDATION:")
        print("• Prioritize early-warning acoustic sensor deployment to high-density hashed regions.")
        print("• Pre-position medical and displacement aid based on the primary threat profile.")
        print("• Exact geographic coordinates remain cryptographically sealed per Zero-Trust mandate")
        print("=" * 70)

    except Exception as e:
        print(f"[!] Analysis failed: {e}")

if __name__ == "__main__":
    analyze_90_day_trends()