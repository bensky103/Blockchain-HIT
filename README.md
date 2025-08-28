# Blockchain Lab

Educational blockchain prototype in Python showcasing core concepts: deterministic blocks, Merkle roots, Bloom pre-filtering, simplified EIP‑1559-style fee burning, dynamic tips, and SegWit‑style detached signatures with light client verification.

## Quick Start

### Create and Activate Virtual Environment

#### Windows
```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### Linux/macOS
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the tests
```
pytest -q
```

## Project Structure

- `core/`: Core blockchain components (blocks, transactions, chain)
- `node/`: Node implementations (full node, light wallet)
- `crypto/`: Cryptographic utilities (merkle trees, bloom filters, keys)
- `sim/`: Simulation data and utilities
- `cli/`: Command-line interface
- `tests/`: Test suite

## Features

Core:
- Block creation & validation (fixed reward = 50)
- Transactions with fees (base_fee=2 burned, tip to miner; dynamic tip suggestion heuristic)
- Mining (simple PoW nonce search, adjustable difficulty flag in CLI)
- Deterministic Merkle root & inclusion proofs
- Bloom filter for fast (probabilistic) tx presence pre-check
- SegWit‑lite detached signatures (tx_id stable pre/post signing)
- Light wallet membership verification (Bloom + Merkle proof) via CLI
- Mempool initialized from JSON fixture (~30 tx) for deterministic sims
- Supply accounting: total_mined, total_burned, balance invariant

Optional / Configurable:
- Enforce exactly 4 transactions per block (disabled by default; can enable on chain object)
- Detached signature store pruning (future enhancement)

Invariant:
```
sum(balances) == initial_supply + total_mined - total_burned
```

Referenced Docs: See `partA.md` (design/status) and `partB.md` (action & evidence plan).

## CLI Usage

From project root (after installing dependencies):

```powershell
# Run full simulation of N blocks
python -m blockchain_lab.cli.main simulate --blocks 5 --miner alice

# Mine a single block (debug)
python -m blockchain_lab.cli.main mine-once --miner alice --difficulty 3

# Light client transaction presence check
python -m blockchain_lab.cli.main light-check --tx_id <TX_ID> --block <INDEX>
```

Enable strict 4-tx blocks (optional) by setting after constructing the blockchain (e.g. inside `simulate` before mining):
```python
blockchain.enforce_block_tx_count = 4
```

## Evidence Collection

Follow `partB.md` for step-by-step commands producing expected outputs (Bloom demo, Merkle proof, segwit stability, invariant verification, final reporting). Store outputs under an `evidence/` folder for submission.

## SegWit-Lite Notes
- Signatures stored externally; tx serialization & Merkle root exclude witness data
- `tx_id` unchanged by signing/detaching
- Verification retrieves detached signature when missing inline

## Fee Model (Simplified EIP‑1559 Subset)
- Base fee (2) burned permanently
- Tip (default 3 or dynamic via heuristic) credited to miner
- Miner also receives block reward (50) per non-genesis block
- Reported totals printed at end of simulation

## Light Wallet Flow
1. Bloom check (definite absence shortcut)
2. Fetch Merkle proof + verify against block header root
3. Output presence status

## Running Tests Selectively
```powershell
pytest -q                      # all tests
pytest -q blockchain_lab/tests/test_merkle.py::test_merkle_root
```

## License

This project is for educational purposes.
