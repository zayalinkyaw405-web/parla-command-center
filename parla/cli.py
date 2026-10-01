"""
Parla Unified Command-Line Interface (CLI)
Provides operators and edge nodes with direct tools to:
- Verify Zero-Trust cryptographic hash chains & run adversarial self-audits (`parla verify`)
- Inspect local offline ledger health & store-and-forward sync status (`parla status`)
- Securely ingest telemetry with automated PII scrubbing (`parla ingest`)
- Review quarantined anomalies and tampering incidents (`parla quarantine`)
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output handling on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from parla.core.ledger import OfflineLedger
from parla.core.verifier import RedTeamAuditor


def main():
    parser = argparse.ArgumentParser(
        prog="parla",
        description="Parla Zero-Trust Offline Autonomous IoT Framework"
    )
    parser.add_argument("--db", type=str, default="Data/parla_ledger.db", help="Path to SQLite ledger database")

    subparsers = parser.add_subparsers(dest="command", help="Operational Subcommands")

    # Command: verify
    verify_p = subparsers.add_parser("verify", help="Run cryptographic audits and adversarial Red Team self-tests")
    verify_p.add_argument("--suite", action="store_true", help="Run full adversarial stress-test suite in sandbox")

    # Command: status
    status_p = subparsers.add_parser("status", help="Inspect offline ledger metrics and sync queue")

    # Command: ingest
    ingest_p = subparsers.add_parser("ingest", help="Ingest a JSON payload into the Zero-Trust ledger")
    ingest_p.add_argument("--domain", type=str, required=True, help="Domain identifier (e.g. industrial, humanitarian)")
    ingest_p.add_argument("--payload", type=str, required=True, help="JSON payload string or path to JSON file")
    ingest_p.add_argument("--source", type=str, default=None, help="Identifier of source node/sensor")

    # Command: quarantine
    quar_p = subparsers.add_parser("quarantine", help="Inspect quarantined payloads and tamper attempts")
    quar_p.add_argument("--limit", type=int, default=20, help="Max records to display")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    ledger = OfflineLedger(db_path=args.db)

    if args.command == "verify":
        print("\n=======================================================")
        print("🔒 PARLA ZERO-TRUST CRYPTOGRAPHIC AUDIT")
        print("=======================================================")

        # 1. Active ledger audit
        print(f"\n[1] Auditing Active Production Ledger: {args.db}")
        active_audit = ledger.verify_chain_integrity()
        if active_audit["is_valid"]:
            print(f"  ✓ Integrity Certified: {active_audit['total_blocks']} blocks verified with zero broken links.")
            if active_audit.get("tip_block_hash"):
                print(f"  ✓ Tip Block Hash: {active_audit['tip_block_hash']}")
        else:
            print(f"  ✗ INTEGRITY FAILURE: {len(active_audit['errors'])} violations detected!")
            for err in active_audit["errors"]:
                print(f"    - {err}")

        # 2. Adversarial test suite
        if args.suite or not Path(args.db).exists() or active_audit["total_blocks"] == 0:
            print("\n[2] Executing Adversarial Red Team Self-Correction Battery...")
            results = RedTeamAuditor.run_adversarial_suite()
            for item in results["details"]:
                status_icon = "✓" if item["status"] == "PASS" else "✗"
                print(f"  {status_icon} Test '{item['test']}': {item['status']}")
            
            print(f"\nAudit Summary: {results['tests_passed']}/{results['tests_run']} passed.")
            if results["all_passed"]:
                print("🌟 All Zero-Trust assertions certified. Parla is fortified against tampering.")
            else:
                sys.exit(1)

    elif args.command == "status":
        stats = ledger.get_stats()
        print("\n=======================================================")
        print("📊 PARLA OFFLINE LEDGER & SYNC QUEUE STATUS")
        print("=======================================================")
        print(f"  Database Path        : {args.db}")
        print(f"  Size on Disk         : {stats['db_size_bytes'] / 1024:.2f} KB")
        print(f"  Total Blocks Sealed  : {stats['total_blocks']}")
        print(f"  Pending Sync Forward : {stats['pending_sync']}")
        print(f"  Confirmed Synced     : {stats['synced_blocks']}")
        print(f"  Quarantined Anomalies: {stats['quarantine_count']}")
        print(f"  Active Domains       : {', '.join(stats['active_domains']) or 'None'}")
        print("=======================================================\n")

    elif args.command == "ingest":
        payload_data = None
        if Path(args.payload).exists():
            with open(args.payload, 'r', encoding='utf-8') as f:
                payload_data = json.load(f)
        else:
            try:
                payload_data = json.loads(args.payload)
            except Exception:
                try:
                    import ast
                    payload_data = ast.literal_eval(args.payload)
                except Exception as e:
                    print(f"Error parsing payload: {e}")
                    sys.exit(1)

        success, err, block = ledger.record_event(
            domain=args.domain,
            payload=payload_data,
            source_id=args.source
        )

        if success:
            print(f"✓ Event successfully sealed in Block #{block['seq_id']}")
            print(f"  Hash: {block['block_hash']}")
            print(f"  Domain: {block['domain']}")
            print(f"  Sync Status: PENDING_FORWARD")
        else:
            print(f"✗ Event rejected by Zero-Trust Ingress: {err}")
            sys.exit(1)

    elif args.command == "quarantine":
        records = ledger.get_quarantine_records(limit=args.limit)
        print(f"\n⚠️ QUARANTINED RECORDS (Total: {len(records)})")
        print("-------------------------------------------------------")
        for rec in records:
            print(f"ID #{rec['id']} | Timestamp: {rec['timestamp']} | Domain: {rec['domain']}")
            print(f"  Reason : {rec['reason']}")
            print(f"  Source : {rec['source_id']}")
            print(f"  Payload: {rec['raw_payload'][:120]}...")
            print("-------------------------------------------------------")


if __name__ == "__main__":
    main()
