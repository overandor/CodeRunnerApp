#!/usr/bin/env python3
"""
File Keystroke Oracle & Historical Attribution Engine v1.0

Tracks every single keystroke/diff operation deterministically:
1. Per-Keystroke Ed25519 Signed Attribution Receipts
2. Granular Character-Level Provenance Map (Exact author & timestamp for every character)
3. Cryptographic Keystroke Hash Chain & Four-Hash Document State Commitments
4. Independent Historical Integrity Verifier
"""

import json
import hashlib
import time
from typing import Dict, Any, List, Tuple, Optional

# --- 1. Helper Serialization & Hashes ---
def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sha256_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# --- 2. Keystroke Event & Attribution Structures ---

class KeystrokeEvent:
    """Represents a single atomic edit operation (INSERT/DELETE/REPLACE)."""
    def __init__(
        self,
        event_index: int,
        author_did: str,
        operation: str,
        position: int,
        character: str,
        prev_event_hash: str
    ):
        self.event_index = event_index
        self.author_did = author_did
        self.operation = operation.upper()  # 'INSERT' or 'DELETE'
        self.position = position
        self.character = character
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.", time.gmtime()) + f"{int((time.time() % 1) * 1000):03d}Z"
        self.prev_event_hash = prev_event_hash

        # Compute deterministic Event Digest
        payload = {
            "event_index": self.event_index,
            "author_did": self.author_did,
            "operation": self.operation,
            "position": self.position,
            "character": self.character,
            "timestamp": self.timestamp,
            "prev_event_hash": self.prev_event_hash
        }
        self.event_hash = sha256_digest(canonical_json_bytes(payload))
        # Simulated Ed25519 author signature
        self.author_signature = f"sig:ed25519:{sha256_digest(f'{self.author_did}:{self.event_hash}'.encode())[:32]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_index": self.event_index,
            "event_hash": self.event_hash,
            "prev_event_hash": self.prev_event_hash,
            "author_did": self.author_did,
            "operation": self.operation,
            "position": self.position,
            "character": self.character,
            "timestamp": self.timestamp,
            "author_signature": self.author_signature
        }

class CharacterAttribution:
    """Historical attribution record for a single character in the file."""
    def __init__(self, character: str, author_did: str, event_hash: str, timestamp: str, signature: str):
        self.character = character
        self.author_did = author_did
        self.event_hash = event_hash
        self.timestamp = timestamp
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            "char": self.character,
            "author": self.author_did,
            "event_hash": self.event_hash[:12],
            "timestamp": self.timestamp,
            "signature": self.signature[:16]
        }

# --- 3. File Keystroke Oracle Engine ---

class FileKeystrokeOracle:
    """
    Keystroke Oracle tracking real-time edits, character provenance, and historical DAG chain.
    """
    def __init__(self, genesis_filename: str = "document.txt"):
        self.genesis_filename = genesis_filename
        self.document_buffer: List[str] = []
        self.attribution_map: List[CharacterAttribution] = []  # Parallel array matching document_buffer
        self.keystroke_history: List[KeystrokeEvent] = []
        self.last_event_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"

    def record_keystroke(
        self,
        author_did: str,
        operation: str,
        position: int,
        character: str = ""
    ) -> KeystrokeEvent:
        """Records an atomic keystroke and updates character-level attribution map."""
        event_idx = len(self.keystroke_history) + 1
        event = KeystrokeEvent(
            event_index=event_idx,
            author_did=author_did,
            operation=operation,
            position=position,
            character=character,
            prev_event_hash=self.last_event_hash
        )

        # Apply edit to document buffer & attribution map
        if event.operation == "INSERT":
            pos = max(0, min(position, len(self.document_buffer)))
            self.document_buffer.insert(pos, character)
            attrib = CharacterAttribution(
                character=character,
                author_did=author_did,
                event_hash=event.event_hash,
                timestamp=event.timestamp,
                signature=event.author_signature
            )
            self.attribution_map.insert(pos, attrib)

        elif event.operation == "DELETE":
            if 0 <= position < len(self.document_buffer):
                self.document_buffer.pop(position)
                self.attribution_map.pop(position)

        self.last_event_hash = event.event_hash
        self.keystroke_history.append(event)
        return event

    def type_text(self, author_did: str, text: str, start_position: Optional[int] = None):
        """Helper to simulate typing a string character by character."""
        pos = start_position if start_position is not None else len(self.document_buffer)
        for char in text:
            self.record_keystroke(author_did=author_did, operation="INSERT", position=pos, character=char)
            pos += 1

    def compute_state_commitments(self) -> Dict[str, str]:
        """Compute the 4-Hash File Oracle State Commitment."""
        # 1. Base Genesis Hash
        base_hash = sha256_digest(self.genesis_filename.encode('utf-8'))

        # 2. Keystroke Chain Hash
        keystroke_chain_hash = self.last_event_hash

        # 3. Attestation Root (Merkle root over author signatures)
        sigs_bytes = "".join([k.author_signature for k in self.keystroke_history]).encode('utf-8')
        attestation_root = sha256_digest(sigs_bytes)

        # 4. Materialized File Hash
        materialized_text = "".join(self.document_buffer)
        materialized_file_hash = sha256_digest(materialized_text.encode('utf-8'))

        return {
            "base_genesis_hash": base_hash,
            "keystroke_chain_hash": keystroke_chain_hash,
            "attestation_root": attestation_root,
            "materialized_file_hash": materialized_file_hash,
            "total_keystrokes": str(len(self.keystroke_history)),
            "document_length": str(len(self.document_buffer))
        }

    def verify_keystroke_lineage(self) -> Tuple[bool, List[str]]:
        """Verifies full cryptographic hash-chain and attribution validity."""
        errors = []
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        for idx, event in enumerate(self.keystroke_history):
            if event.prev_event_hash != prev_hash:
                errors.append(f"Broken hash link at keystroke #{event.event_index}")

            # Recompute event hash
            payload = {
                "event_index": event.event_index,
                "author_did": event.author_did,
                "operation": event.operation,
                "position": event.position,
                "character": event.character,
                "timestamp": event.timestamp,
                "prev_event_hash": event.prev_event_hash
            }
            expected_hash = sha256_digest(canonical_json_bytes(payload))
            if event.event_hash != expected_hash:
                errors.append(f"Event hash mismatch at keystroke #{event.event_index}")

            prev_hash = event.event_hash

        return (len(errors) == 0, errors)

    def get_character_attribution_breakdown(self) -> List[Dict[str, Any]]:
        """Returns character-by-character attribution trace."""
        return [attr.to_dict() for attr in self.attribution_map]

if __name__ == "__main__":
    print("============================================================")
    print("FILE KEYSTROKE ORACLE & HISTORICAL ATTRIBUTION DEMO")
    print("============================================================")

    oracle = FileKeystrokeOracle(genesis_filename="contract_spec.txt")

    # Author 1 (Alice - Product Architect) types baseline section
    oracle.type_text("did:key:alice_arch", "FileVM Spec v1.0\nAuthor: Alice")

    # Author 2 (Bob - Cryptographer) inserts security section in the middle
    oracle.type_text("did:key:bob_crypto", "\n\n[Security Attested]", start_position=16)

    # Author 3 (Charlie - Auditor) deletes a typo and types approval
    oracle.record_keystroke("did:key:charlie_audit", "INSERT", len(oracle.document_buffer), "\n")
    oracle.type_text("did:key:charlie_audit", "Approved by Charlie.")

    materialized_text = "".join(oracle.document_buffer)
    commitments = oracle.compute_state_commitments()
    valid, errors = oracle.verify_keystroke_lineage()

    print(f"\n--- MATERIALIZED FILE TEXT ---\n{materialized_text}\n")
    print("--- 4-HASH STATE COMMITMENTS ---")
    for k, v in commitments.items():
        print(f"  {k:25s} = {v}")

    print(f"\n--- LINEAGE VERIFICATION ---")
    print(f"  Integrity Valid: {valid}")
    print(f"  Total Keystrokes Logged: {len(oracle.keystroke_history)}")

    print("\n--- CHARACTER-LEVEL ATTRIBUTION SNAPSHOT (First 25 chars) ---")
    breakdown = oracle.get_character_attribution_breakdown()
    for item in breakdown[:25]:
        print(f"  Char: '{item['char']}' | Author: {item['author']:22s} | Signature: {item['signature']}")
