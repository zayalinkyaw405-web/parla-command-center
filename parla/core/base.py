"""
Parla Modular Adapter & Protocol Abstractions
Defines standard interfaces for:
1. Ingestors (Streams, CSV Chunks, OSINT, Edge Packets)
2. Guards (PII Scrubbers, Red Team bounds checking, Temporal checks)
3. Processors (ML Classifiers, TreeSHAP, DBSCAN, Association Miners, Early Warning)
4. Emitters (Local Sirens, LoRa Mesh, Store-and-Forward Syncers, HMI)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Generator, Optional
from parla.core.ledger import OfflineLedger


class BaseIngestor(ABC):
    """Abstract interface for data ingestion sources."""

    def __init__(self, domain: str, ledger: OfflineLedger):
        self.domain = domain
        self.ledger = ledger

    @abstractmethod
    def ingest(self, source_input: Any) -> int:
        """Ingests raw inputs, sanitizes them, and persists to ledger. Returns count of ingested events."""
        pass

    @abstractmethod
    def stream_chunks(self, source_path: str, chunk_size: int = 1000) -> Generator[Dict[str, Any], None, None]:
        """Safely streams large datasets without memory saturation."""
        pass


class BaseProcessor(ABC):
    """Abstract interface for analytics, machine learning, and pattern discovery modules."""

    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    @abstractmethod
    def process_event(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processes a single event payload and returns computed inferences."""
        pass

    @abstractmethod
    def batch_train_or_mine(self, dataset: Any) -> Dict[str, Any]:
        """Trains or mines patterns across an aggregated dataset."""
        pass


class BaseEmitter(ABC):
    """Abstract interface for dispatching actionable alerts and forward syncing."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def emit_alert(self, alert_payload: Dict[str, Any]) -> bool:
        """Emits an immediate local alert (e.g. siren, RF packet, dashboard alert)."""
        pass

    @abstractmethod
    def sync_forward(self, pending_events: List[Dict[str, Any]]) -> List[int]:
        """Transmits pending events to external uplink when connectivity is available. Returns synced seq_ids."""
        pass
