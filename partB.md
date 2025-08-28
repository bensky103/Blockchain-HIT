# Part B – Direct Action Plan & Evidence Collection Guide

Purpose: Concrete, sequential tasks to implement, verify, and collect evidence for grading. Follow in order; check off each box. PowerShell commands assume you're in the project root (where partB.md lives). All commands are safe to copy/paste.

Legend:
- [ ] Task not started  |  [x] Done
- Evidence = artifact (screenshot, copied CLI lines, test output) you must save in your submission folder (suggest create `evidence/`).

## 0. Prerequisites
1. Python 3.12 available (verify):
   powershell> python --version
   Expected: Python 3.12.x
2. Install dependencies (one time):
   powershell> pip install -r blockchain_lab/requirements.txt
   Expected tail: Successfully installed pytest ... cryptography ...
3. (Optional) Create evidence directory:
   powershell> New-Item -ItemType Directory evidence -ErrorAction SilentlyContinue | Out-Null

## 1. Run Full Test Suite (Baseline)
Command:
  powershell> pytest -q
Capture: Total tests collected & pass/fail summary.
Expected: All tests pass (0 failed). If failures exist, note them before proceeding.
Evidence: Save output to `evidence/00_baseline_tests.txt`.

## 2. Bloom Filter (a) Verification
Already implemented; verify behavior manually.
Quick REPL check:
  powershell> python - <<'PY'
from blockchain_lab.crypto import bloom
bf = bloom.BloomFilter(m_bits=256,k=3)
items=[f"tx{i}".encode() for i in range(5)]
for it in items: bf.add(it)
print('All present ->', all(bf.might_contain(it) for it in items))
print('Random miss example ->', bf.might_contain(b'not_there'))
PY
Expected: All present -> True; second line can be True or False (explain FP if True).
Evidence: Copy output -> `evidence/01_bloom_repl.txt`.

## 3. Merkle Tree (b) Root Stability & Proofs
Command:
  powershell> python - <<'PY'
from blockchain_lab.crypto import merkle
from blockchain_lab.core.tx import Tx
txs=[Tx('a','b',i,nonce=i,base_fee=2,tip=3) for i in range(4)]
root1=merkle.merkle_root(txs)
root2=merkle.merkle_root(txs)
proof=merkle.merkle_proof(txs, txs[2].tx_id())
print('Root deterministic:', root1==root2, root1)
print('Proof verifies:', merkle.verify_proof(root1, txs[2].tx_id(), proof))
PY
Expected: Root deterministic: True <hash>; Proof verifies: True
Evidence: Save to `evidence/02_merkle.txt`.

## 4. Light Wallet Presence Check (c)
Run existing test subset:
  powershell> pytest -q blockchain_lab/tests/test_bloom_light_wallet.py::test_light_wallet_membership
Expected: 1 passed.
Evidence: `evidence/03_lightwallet_test.txt`.

## 5. Mempool Initialization (d)
Inspect JSON count:
  powershell> (Get-Content blockchain_lab/sim/mempool_init.json | ConvertFrom-Json).Count
Expected: ~30
Run simulation one block to ensure load executed (use small mempool sample):
  powershell> python -m blockchain_lab.cli.main simulate --blocks 1 --miner demo_miner | Select-String 'Loaded mempool'
Evidence: `evidence/04_mempool_load.txt` (include line showing load + count).

## 6. Chain Fees & Invariant (e,f)
Run core tests:
  powershell> pytest -q blockchain_lab/tests/test_core_models.py::test_invariant_conservation
  powershell> pytest -q blockchain_lab/tests/test_fees_and_mempool.py::test_fee_accounting
Expected: both pass.
Evidence: combine outputs -> `evidence/05_invariant_fees.txt`.
Manual invariant check after a short sim (3 blocks):
  powershell> python -m blockchain_lab.cli.main simulate --blocks 3 --miner alice > evidence/05_sim3.txt
Then open file and verify: Sum balances = initial + mined - burned.

## 7. SegWit Detached Signature (g)
Check tx_id stability:
  powershell> python - <<'PY'
from blockchain_lab.core.tx import Tx
from blockchain_lab.crypto import keys, segwit
sk, pk = keys.generate_key_pair()
tx=Tx('u1','u2',10,nonce=0,base_fee=2,tip=3)
id_before=tx.tx_id()
tx.sign(sk, detach=True)
id_after=tx.tx_id()
print('Detached stored:', bool(segwit.get_signature(id_after)))
print('ID stable:', id_before==id_after)
PY
Expected: Detached stored: True; ID stable: True
Evidence: `evidence/06_segwit.txt`.

## 8. Light Wallet End-to-End Membership (c again)
Mine a few blocks then query one tx:
  powershell> python -m blockchain_lab.cli.main simulate --blocks 2 --miner m1 > evidence/07_sim2.txt
Pick a tx_id from output (or from mempool) and run:
  powershell> python -m blockchain_lab.cli.main light-check --tx_id <TX_ID> --block 1
Expected: prints FOUND / True style message.
Evidence: `evidence/07_lightcheck.txt`.

## 9. Final Reporting (h)
Full run (e.g., 5 blocks):
  powershell> python -m blockchain_lab.cli.main simulate --blocks 5 --miner final_miner > evidence/08_final_run.txt
Expected sections: Per-block lines, Final Balances, Totals (mined, burned, supply).
Verify mined == 50 * blocks_mined (excluding genesis). Burned == 2 * total_tx_included.

## 10. Optional: Enforce Exactly 4 Tx/Block
If enabling: set enforce flag in chain or CLI (documented in partA). Re-run a short sim; confirm blocks with <4 tx are skipped or delayed. Save output as `evidence/09_enforce4.txt`.

## 11. Summary Checklist
- [ ] Baseline tests captured
- [ ] Bloom evidence
- [ ] Merkle root & proof evidence
- [ ] Light wallet test
- [ ] Mempool load evidence
- [ ] Invariant & fee tests
- [ ] SegWit tx_id stability
- [ ] Light wallet manual membership check
- [ ] Final reporting run
- [ ] (Optional) 4-tx enforcement evidence

## 12. Packaging for Submission
Include: `partA.md`, this `partB.md`, `evidence/` directory, and a brief README note citing any deviations (e.g., optional enforcement disabled by default).

## 13. Stretch Ideas (Do Only After All Above ✅)
- Dynamic base_fee mock adjustment & show changing burn.
- JSON export of per-block stats: modify CLI to write `reports/run_timestamp.json`.
- Witness pruning after block application.

End of Action Plan.
