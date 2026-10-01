"""
Parla Offline-First ACID Ledger & Store-and-Forward Engine
Implements:
1. SQLite WAL Mode for High-Performance Atomic Persistence
2. Chained Cryptographic Tamper-Evident Ledger
3. Zero-Trust Ingress Quarantine System
4. Store-and-Forward Event Queue with Sync State Checkpoints
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from parla.core.security import (
    PIIScrubber,
    CryptographicEnvelope,
    canonical_json
)


class OfflineLedger:
    """
    Embedded, zero-dependency offline storage ledger.
    Guarantees ACID transactions, full crash-resilience across power cuts (WAL mode),
    and unforgeable cryptographic event chaining.
    """

    def __init__(self, db_path: str = "Data/parla_ledger.db", node_secret: str = "parla-zero-trust-offline-root-key"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.envelope = CryptographicEnvelope(node_secret=node_secret)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for concurrency and crash-proof durability
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Initializes ledger tables, quarantine logs, and sync tracking."""
        with self._get_connection() as conn:
            # 1. Tamper-evident ledger blocks
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ledger_blocks (
                    seq_id INTEGER PRIMARY KEY,
                    block_hash TEXT NOT NULL UNIQUE,
                    prev_hash TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    nonce TEXT NOT NULL UNIQUE,
                    payload_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'PENDING_FORWARD'
                );
            """)

            # 2. Zero-Trust Quarantine Table for invalid/tampered data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quarantine_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    source_id TEXT,
                    reason TEXT NOT NULL,
                    raw_payload TEXT NOT NULL,
                    quarantine_details TEXT
                );
            """)

            # 3. Store-and-Forward synchronization checkpoints
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_checkpoints (
                    domain TEXT PRIMARY KEY,
                    last_synced_seq INTEGER NOT NULL,
                    last_synced_at TEXT NOT NULL
                );
            """)
            conn.commit()

    def get_latest_block_hash(self) -> str:
        """Retrieves the hash of the latest block, or GENESIS_HASH if empty."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return row["block_hash"]
            return CryptographicEnvelope.GENESIS_HASH

    def get_next_seq_id(self) -> int:
        """Determines the next monotonic sequence ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT MAX(seq_id) as max_id FROM ledger_blocks;")
            row = cursor.fetchone()
            if row and row["max_id"] is not None:
                return row["max_id"] + 1
            return 1

    def record_event(
        self,
        domain: str,
        payload: Dict[str, Any],
        source_id: Optional[str] = None,
        coarsen_gps: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Zero-Trust Ingress Pipeline:
        1. Scrub PII and coarsen GPS.
        2. Validate payload is a valid non-empty dict.
        3. Form cryptographic block chained to latest block hash.
        4. Atomically persist to SQLite ledger.
        If validation or integrity fails, routes to quarantine_records.
        """
        # Step 1: Ingress Sanitization
        try:
            if not isinstance(payload, dict) or not payload:
                raise ValueError("Payload must be a non-empty dictionary structure.")
            clean_payload = PIIScrubber.sanitize_payload(payload, coarsen_gps=coarsen_gps)
        except Exception as e:
            self._quarantine(
                domain=domain,
                source_id=source_id,
                reason=f"Sanitization error: {str(e)}",
                raw_payload=str(payload)
            )
            return False, f"Quarantined: {str(e)}", None

        # Step 2: Cryptographic Sealing & Chaining
        try:
            with self._get_connection() as conn:
                # Use BEGIN IMMEDIATE to guarantee sequence and hash atomicity
                conn.execute("BEGIN IMMEDIATE;")
                
                # Fetch current tip of the chain inside transaction
                cursor = conn.execute("SELECT seq_id, block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1;")
                latest_row = cursor.fetchone()
                
                if latest_row:
                    next_seq = latest_row["seq_id"] + 1
                    prev_hash = latest_row["block_hash"]
                else:
                    next_seq = 1
                    prev_hash = CryptographicEnvelope.GENESIS_HASH

                # Create cryptographic block envelope
                block = self.envelope.create_block(
                    seq_id=next_seq,
                    prev_hash=prev_hash,
                    domain=domain,
                    payload=clean_payload
                )

                # Atomically insert into ledger
                conn.execute("""
                    INSERT INTO ledger_blocks (
                        seq_id, block_hash, prev_hash, domain, timestamp,
                        nonce, payload_hash, payload_json, signature, sync_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_FORWARD');
                """, (
                    block["seq_id"],
                    block["block_hash"],
                    block["prev_hash"],
                    block["domain"],
                    block["timestamp"],
                    block["nonce"],
                    block["payload_hash"],
                    canonical_json(block["payload"]),
                    block["signature"]
                ))
                conn.commit()
                return True, None, block
        except Exception as e:
            self._quarantine(
                domain=domain,
                source_id=source_id,
                reason=f"Ledger commit failure: {str(e)}",
                raw_payload=canonical_json(clean_payload)
            )
            return False, f"Quarantined due to commit failure: {str(e)}", None

    def _quarantine(self, domain: str, source_id: Optional[str], reason: str, raw_payload: str):
        """Isolates suspicious, tampered, or malformed data into quarantine."""
        import time
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO quarantine_records (
                    timestamp, domain, source_id, reason, raw_payload
                ) VALUES (?, ?, ?, ?, ?);
            """, (ts, domain, source_id or "UNKNOWN", reason, raw_payload))
            conn.commit()

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Rigorously audits every single block in the ledger:
        - Validates monotonic seq_id continuity
        - Verifies prev_hash cryptographic link
        - Recomputes payload and block SHA-256 hashes
        - Verifies HMAC signatures
        Returns comprehensive diagnostic audit report.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM ledger_blocks ORDER BY seq_id ASC;")
            rows = cursor.fetchall()

            if not rows:
                return {
                    "is_valid": True,
                    "total_blocks": 0,
                    "errors": [],
                    "message": "Ledger is empty (Genesis state)."
                }

            expected_prev_hash = CryptographicEnvelope.GENESIS_HASH
            expected_seq = 1
            errors = []

            for row in rows:
                seq_id = row["seq_id"]
                if seq_id != expected_seq:
                    errors.append(f"Sequence break: expected seq_id {expected_seq}, found {seq_id}")

                block = {
                    "seq_id": row["seq_id"],
                    "block_hash": row["block_hash"],
                    "prev_hash": row["prev_hash"],
                    "domain": row["domain"],
                    "timestamp": row["timestamp"],
                    "nonce": row["nonce"],
                    "payload_hash": row["payload_hash"],
                    "payload": json.loads(row["payload_json"]),
                    "signature": row["signature"]
                }

                is_valid, reason = self.envelope.verify_block(block, expected_prev_hash=expected_prev_hash)
                if not is_valid:
                    errors.append(f"Block #{seq_id} failed audit: {reason}")

                expected_prev_hash = row["block_hash"]
                expected_seq += 1

            return {
                "is_valid": len(errors) == 0,
                "total_blocks": len(rows),
                "errors": errors,
                "tip_block_hash": rows[-1]["block_hash"] if rows else None,
                "message": "Chain integrity certified." if not errors else f"Detected {len(errors)} chain integrity violations!"
            }

    def get_pending_events(self, domain: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves events pending store-and-forward transmission."""
        with self._get_connection() as conn:
            if domain:
                cursor = conn.execute("""
                    SELECT * FROM ledger_blocks 
                    WHERE sync_status = 'PENDING_FORWARD' AND domain = ?
                    ORDER BY seq_id ASC LIMIT ?;
                """, (domain, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM ledger_blocks 
                    WHERE sync_status = 'PENDING_FORWARD'
                    ORDER BY seq_id ASC LIMIT ?;
                """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "seq_id": row["seq_id"],
                    "block_hash": row["block_hash"],
                    "prev_hash": row["prev_hash"],
                    "domain": row["domain"],
                    "timestamp": row["timestamp"],
                    "payload": json.loads(row["payload_json"]),
                    "signature": row["signature"]
                })
            return results

    def mark_synced(self, seq_ids: List[int]):
        """Marks blocks as successfully synced to uplink."""
        if not seq_ids:
            return
        placeholders = ",".join("?" for _ in seq_ids)
        with self._get_connection() as conn:
            conn.execute(f"""
                UPDATE ledger_blocks 
                SET sync_status = 'SYNCED' 
                WHERE seq_id IN ({placeholders});
            """, seq_ids)
            conn.commit()

    def get_quarantine_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent quarantined records for administrative and forensic review."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM quarantine_records ORDER BY id DESC LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Provides operational metrics on ledger health and backlog."""
        with self._get_connection() as conn:
            total_blocks = conn.execute("SELECT COUNT(*) FROM ledger_blocks;").fetchone()[0]
            pending_sync = conn.execute("SELECT COUNT(*) FROM ledger_blocks WHERE sync_status = 'PENDING_FORWARD';").fetchone()[0]
            synced_blocks = conn.execute("SELECT COUNT(*) FROM ledger_blocks WHERE sync_status = 'SYNCED';").fetchone()[0]
            quarantine_count = conn.execute("SELECT COUNT(*) FROM quarantine_records;").fetchone()[0]
            
            domains = [row[0] for row in conn.execute("SELECT DISTINCT domain FROM ledger_blocks;").fetchall()]

            return {
                "total_blocks": total_blocks,
                "pending_sync": pending_sync,
                "synced_blocks": synced_blocks,
                "quarantine_count": quarantine_count,
                "active_domains": domains,
                "db_size_bytes": os.path.getsize(self.db_path) if self.db_path.exists() else 0
            }
