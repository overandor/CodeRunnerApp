import pytest
from src.hdar_core.attestation.nitro_enclave import NitroEnclaveAttestor

def test_nitro_attestation_generation_and_verification():
    attestor = NitroEnclaveAttestor("nitro-hdar-enclave-prod")
    doc = attestor.generate_attestation_doc(workspace_hash="abc123sha256digest", epoch=2)
    
    valid, msg = NitroEnclaveAttestor.verify_attestation_doc(doc)
    assert valid is True
    assert "VERIFIED: AWS Nitro Enclave" in msg

def test_nitro_attestation_detects_tampering():
    attestor = NitroEnclaveAttestor("nitro-hdar-enclave-prod")
    doc = attestor.generate_attestation_doc(workspace_hash="abc123sha256digest", epoch=2)
    
    # Tamper with PCR measurement
    doc["attestation_doc"]["pcrs"]["0"] = "tampered_pcr_hash"
    
    valid, msg = NitroEnclaveAttestor.verify_attestation_doc(doc)
    assert valid is False
    assert "failed" in msg.lower()
