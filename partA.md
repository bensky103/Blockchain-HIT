--- Slide 1: 🚀 Title + Authors + Requirement Status ---
Title: Minimal Blockchain Framework – Architecture & Features
Authors: <Name1>, <Name2>
Course / Assignment: Blockchain Skeleton (Presentation Part ~20%)

Status Overview:
  ✅ Implemented:
    • Bloom Filter
    • Merkle (core path) + real merkle root in Block.create_header & genesis
    • Light wallet inclusion verification
    • 30 TX JSON initialization
    • Fee model & burning (simplified EIP‑1559)
    • Mining (basic PoW)
    • SegWit: canonical txid excludes signatures + external detached signature (witness) store
    • Dynamic tip suggestion heuristic (fees.suggest_tip based on mempool load)
    • LightWallet key generation & create_transaction (detached signing) helpers
    • Network accounting summary
  🟡 Partial:
  • Enforce exactly 4 tx per block (config flag available, off by default; still mines "up to 4")
    - Rationale: Strict enforcement would force the miner loop to WAIT until 4 tx accumulate; with sparse test/demo traffic this adds idle time, slows simulations, and risks user confusion ("why no new block?"). Left configurable so demos remain fast while still documenting the stricter policy.
    • Full signature pruning: legacy in‑object signatures remain unless wallet uses detached mode
  🔲 Missing (acceptable): P2P / broadcast layer, GUI

--- Slide 2: 🛠️ Installation & Basic Run ---
Prerequisites: Python 3.12+, pip, (optional) virtualenv
Setup (PowerShell):
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r blockchain_lab/requirements.txt
Run tests:
  pytest -q
Run simulation (5 blocks):
  python -m blockchain_lab.cli.main simulate --blocks 5 --miner demo_miner
Mine a single block (debug):
  python -m blockchain_lab.cli.main mine-once --miner demo_miner --difficulty 3
Light wallet verification (after grabbing real tx_id & block index):
  python -m blockchain_lab.cli.main light-check --tx_id <TX_ID> --block <INDEX>

--- Slide 3: 🏗️ High-Level Architecture ---
Directories:
  core/   : Tx, Block, Blockchain, fee helpers
  crypto/ : bloom, merkle, segwit (signature store), keys, signatures
  node/   : full_node, mempool, mining, light_wallet
  cli/    : command entrypoints (simulate, mine-once, light-check)
Data Flow:
  init_state.json + mempool_init.json → Mempool → Mining (candidate + PoW) → apply_block (fees, burn, reward) → Bloom filter per block + Merkle root → Light wallet inclusion verification.

--- Slide 4: 💸 Transaction Model & Simplified EIP‑1559 ---
Snippet (canonical tx_id independent of signature):
  class Tx:
      def _calculate_tx_id(self):
          tx_dict = self.to_dict(include_signature=False, include_pubkey=False)
          canonical = json.dumps(tx_dict, sort_keys=True, separators=(',', ':'))
          return hashlib.sha256(canonical.encode()).hexdigest()
Fields: sender, recipient, amount, nonce, base_fee (default 2, burned), tip (default 3, to miner)
Total sender debit = amount + base_fee + tip
Security: Signature covers deterministic preimage without signature → stable txid (SegWit style separation potential).

--- Slide 5: 🔥 Fees, Burning & Block Reward ---
Snippet (apply_block logic excerpt):
  for tx in block.txs:
      if not tx.verify_signature(): return False
      total_cost = tx.amount + tx.base_fee + tx.tip
      temp_balances[tx.sender] -= total_cost
      temp_balances[tx.recipient] += tx.amount
      temp_balances[miner_addr] += tx.tip
      block_burned += tx.base_fee   # burned
  temp_balances[miner_addr] += 50  # BLOCK_REWARD
  self.total_burned += block_burned
  self.total_mined += 50
Concepts: base_fee burned (deflationary), tip = miner incentive ordering, reward = new issuance.
Invariant: sum(balances) = initial_supply + total_mined − total_burned.

--- Slide 6: 📥 Mempool Admission Logic ---
Snippet (mempool.accept):
  if tx.tx_id in self.transactions: return False
  sender_balance = self.balances.get(tx.sender, 0)
  if sender_balance < (tx.amount + tx.base_fee + tx.tip): return False
  self.transactions[tx.tx_id] = tx
  self.tx_queue.append(tx.tx_id)
  return True
Points: duplicate prevention, affordability check, FIFO (deque) ensures deterministic batching.

--- Slide 7: ⛏️ Mining & Proof‑of‑Work ---
Candidate block: real_merkle_root = merkle_root(tx_batch)
Header uses prev_block.hash, index+1, timestamp, nonce=0.
Mining loop:
  target = '0' * difficulty
  for nonce in range(max_nonce):
      block.header.nonce = nonce
      if block.block_hash.startswith(target): return True
Goal: illustrate PoW concept; bounded iterations for test speed.
Possible extension: difficulty retarget + metrics.

--- Slide 8: 🌳 Merkle Tree & Inclusion Proof ---
Leaves: sha256(tx_id). Pairwise hash upward; duplicate last if odd count.
Proof: sequence of (side, sibling_hash) pairs.
Verification: fold proof to reconstruct candidate root; compare to header.merkle_root.
Benefit: O(log n) inclusion proofs for light clients without full block.

--- Slide 9: 🌼 Bloom Filter (Fast Probabilistic Membership) ---
Snippet:
  bloom = BloomFilter(m_bits=2048, k=3)
  for tx in block.txs: bloom.add(tx.tx_id.encode())
  bloom.might_contain(tx_id.encode())  # True/False (possibly false positive)
Usage: quick pre-check before Merkle proof request → reduces bandwidth/CPU.

--- Slide 10: 💡 Light Wallet Two‑Step Verification ---
Process:
 1. Bloom filter: if false → guaranteed absent.
 2. If maybe → fetch Merkle proof.
 3. verify_proof(root, tx_id, proof) → inclusion confirmed.
Handles non-existent block indexes with explicit exception.

--- Slide 11: 🧩 SegWit / Witness Separation ---
Principle: txid independent of signature; witness data detachable.
Current Implementation:
  • Tx.sign(detach=True) (used by LightWallet) stores signature in segwit.SIGNATURE_STORE and leaves Tx.signature None.
  • Legacy signing path (detach=False, default) keeps signature in-memory; apply_block still mirrors it to the store.
  • Block serialization omits signatures by default; optional witnesses map if include_witness=True.
Benefits: Stable txid & merkle root unaffected by signatures; lighter light‑client proofs.
Remaining Gap: Mined tx objects still often carry signatures (needs pruning or enforced detached signing policy).

--- Slide 12: 📊 Network State & Reporting ---
Simulation output highlights:
  Mined Block <n> with <k> transactions.
  Final Balances: wallet name + truncated address + balance.
  Network State: Total Coins, Total Mined, Total Burned.
  Mining Log: per block (tx_count, reward, burned_fees).
Interpretation: Monetary policy = initial + mined − burned; burning reduces net issuance.

--- Slide 13: 🎬 Live Demo Script (Commands + Expected Output) ---
1. Tests:
   pytest -q → all tests pass (summary: X passed).
2. Simulation (5 blocks):
   python -m blockchain_lab.cli.main simulate --blocks 5 --miner demo_miner
   Expect: init message, loaded <N> transactions, per‑block mining lines, final balances + totals.
   Check: Total Mined = 50 * mined_blocks (excluding genesis); Total Burned = 2 * total_transactions_included.
3. Inclusion proof (interactive):
   Grab tx_id from a mined block, fetch proof via full_node, run verify_proof(...) → True.
4. Light wallet verification:
   python -m blockchain_lab.cli.main light-check --tx_id <TX_ID> --block <INDEX>
   Expect: PRESENT for valid tx, NOT PRESENT for fake.
5. SegWit store size:
   print(len(blockchain_lab.crypto.segwit.SIGNATURE_STORE)) → equals total signed tx included so far.
6. Monetary invariant:
   sum(balances.values()) == initial + chain.total_mined - chain.total_burned → True.
7. Optional fast mine:
   python -m blockchain_lab.cli.main mine-once --miner quick --difficulty 2 → quick success line.

--- Slide 14: ⚠️ Known Issues & Potential Improvements ---
1. Enforce-4 policy disabled by default (currently "up to 4") — could auto-wait for full batches.
2. Signature pruning not enforced for legacy paths (need global detach or post-block cleanup).
3. No P2P networking (single process simulation).
4. Difficulty retargeting & richer fee market absent.
5. Witness serialization format could be standardized (e.g., separate witness block section on disk).
Fast Wins: enable enforce_block_tx_count=4 by default; enforce detach=True on all signing; add pruning step; add simple peer gossip stub.

--- Slide 15: 📚 References & Module Mapping ---
References:
  - Simplified EIP‑1559 (base fee burn + tip model)
  - Standard Merkle tree & Bloom filter literature
  - Segregated Witness concept (Bitcoin SegWit inspiration)
Module Mapping:
  Bloom Filter: crypto/bloom.py
  Merkle Tree : crypto/merkle.py
  SegWit Store: crypto/segwit.py
  Fees/Burning : core/fees.py + core/chain.py (apply_block)
  Mining       : node/mining.py
  Mempool      : node/mempool.py
  Light Client : node/light_wallet.py

