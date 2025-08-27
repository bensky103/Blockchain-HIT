# Slides Outline

## Team Names
- Add team member names here.

## Implemented vs Not Implemented
- **Implemented:**
  - Core blockchain models (Tx, Block, Blockchain)
  - Fee rules and mempool integration
  - Mining and validation
  - Merkle tree and proofs
  - Bloom filter and light wallet
  - SegWit-lite
  - Simulation and outputs
- **Not Implemented:**
  - Peer-to-peer networking
  - Advanced consensus mechanisms

## Install/Run
### Installation
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.

### Running the Project
- To simulate mining: `python cli/main.py simulate --blocks <N> --miner <address>`
- To verify transactions: `python cli/main.py --light-check <tx_id> --block <i>`

## Demo Log Screenshots Suggestions
- Screenshot of the `simulate` command output showing balances, mined, and burned totals.
- Screenshot of the `light-check` command verifying a transaction.
- Screenshot of the mining log showing block creation.
