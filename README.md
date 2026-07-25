# HDAR & FileVM Passport Canonical Suite

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/overandor/CodeRunnerApp/blob/main/hdar_canonical_proof.ipynb)
[![Open MorphOS in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/overandor/CodeRunnerApp/blob/main/morphos_colab.ipynb)

> **Hardware-Detached Agent Runtime (HDAR)** and **FileVM Passport**: A proof-carrying portable runtime identity system. Seal AI agents into content-addressed seed tokens, transport across any host, and resume with verifiable cryptographic lineage.

---

## ⚡ Direct Colab Notebook Links

Click any button below to launch and execute the notebooks directly in Google Colab:

* 🚀 [**Launch HDAR Canonical Proof Notebook (12-Section Executable)**](https://colab.research.google.com/github/overandor/CodeRunnerApp/blob/main/hdar_canonical_proof.ipynb)
* 🌀 [**Launch MorphOS Unified Kernel Colab Notebook**](https://colab.research.google.com/github/overandor/CodeRunnerApp/blob/main/morphos_colab.ipynb)

---

## 📁 Repository Contents

* `hdar_canonical_proof.ipynb` — 12-Section executable notebook testing 3-epoch continuation (`Host A` → `Host B` → `Host C` → `Verifier D`).
* `hdar_portable.py` — Single-file 3-Epoch migration engine & security tamper guard.
* `verifier.js` — Zero-dependency Node.js 20/20 cryptographic verifier.
* `witnessed_transition_engine.py` — TEE / Provider Execution Witness & Trace Merkle Proof Engine.
* `landing.html` — Dark-themed cryptographic landing page.
* `morphos.py` — MorphOS Unified Kernel Runtime.

---

## 🛠 Quick Start in Terminal

```bash
# 1. Run the canonical 3-epoch migration test
python3 hdar_portable.py demo --out /tmp/hdar_demo

# 2. Run tamper-resistance audit (Attacks A, B, C)
python3 hdar_portable.py demo-failure --out /tmp/hdar_tampered

# 3. Run Node.js Cryptographic Verifier C
node verifier.js /tmp/hdar_demo
```
