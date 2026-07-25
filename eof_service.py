#!/usr/bin/env python3
"""
Epistemic Overlay File (EOF) Web Service v1.0
Exposes HTTP endpoints for Four-Hash Commitments & 719° Adversarial Resolution.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from eof_resolver import EpistemicOverlayResolver, EpistemicClaim, AcquisitionReceipt, sha256_digest, canonical_json_bytes

BASE_DOCUMENT = b"# Epistemic Overlay File (EOF) Service Document\nImmutable base artifact."
resolver = EpistemicOverlayResolver()
current_overlay = {}

class EOFServiceHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        global current_overlay
        if self.path in ['/', '/health']:
            self._send_json(200, {
                "service": "Epistemic Overlay File (EOF) Service",
                "status": "healthy",
                "version": "1.0.0",
                "endpoints": [
                    "GET /health",
                    "GET /api/eof/status",
                    "POST /api/eof/resolve"
                ]
            })
        elif self.path == '/api/eof/status':
            materialized_view = (
                BASE_DOCUMENT.decode('utf-8') + 
                f"\n\n--- CURRENT OVERLAY ---\n" + 
                json.dumps(current_overlay, indent=2)
            ).encode('utf-8')
            
            four_hashes = resolver.compute_four_hashes(
                base_bytes=BASE_DOCUMENT,
                overlay_manifest=current_overlay,
                materialized_view_bytes=materialized_view
            )
            self._send_json(200, {
                "four_hashes": four_hashes,
                "current_overlay": current_overlay
            })
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        global current_overlay
        if self.path == '/api/eof/resolve':
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                body = json.loads(body_bytes.decode('utf-8'))
            except Exception as e:
                self._send_json(400, {"error": f"Invalid JSON body: {str(e)}"})
                return

            statement = body.get("statement", "State transitions maintain cryptographic lineage.")
            origin = body.get("origin", "external_derivation")
            evidence_sufficiency = float(body.get("evidence_sufficiency", 0.90))
            source_reliability = float(body.get("source_reliability", 0.85))
            derivation_reproducibility = float(body.get("derivation_reproducibility", 1.0))
            truth_confidence = float(body.get("truth_confidence", 0.88))

            claim = EpistemicClaim(
                statement=statement,
                origin=origin,
                status="contested",
                evidence_sufficiency=evidence_sufficiency,
                source_reliability=source_reliability,
                derivation_reproducibility=derivation_reproducibility,
                truth_confidence=truth_confidence
            )

            rec = AcquisitionReceipt(
                snapshot_id="snap:api_request",
                content_hash=sha256_digest(statement.encode('utf-8')),
                source_uri="http://localhost:8090/api/eof/resolve",
                retriever_identity="did:key:api_client",
                certificate_fingerprint="sha256:api_tls",
                response_headers_hash="sha256:api_headers"
            )

            current_overlay = resolver.execute_719deg_epoch_update(
                previous_overlay=current_overlay,
                supporting_evidence=[rec],
                opposing_evidence=[],
                candidate_claims=[claim]
            )

            materialized_view = (
                BASE_DOCUMENT.decode('utf-8') + 
                f"\n\n--- EPOCH {current_overlay['epoch_number']} OVERLAY ---\n" + 
                json.dumps(current_overlay, indent=2)
            ).encode('utf-8')

            four_hashes = resolver.compute_four_hashes(
                base_bytes=BASE_DOCUMENT,
                overlay_manifest=current_overlay,
                materialized_view_bytes=materialized_view
            )

            self._send_json(200, {
                "message": f"Successfully executed Epoch {current_overlay['epoch_number']} 719° traversal",
                "four_hashes": four_hashes,
                "overlay_epoch": current_overlay
            })
        else:
            self._send_json(404, {"error": "Endpoint not found"})

def run_server(port=8090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, EOFServiceHandler)
    print(f"Starting EOF HTTP Service on http://127.0.0.1:{port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
