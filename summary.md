# Project Summary

## Overview
This is a mini educational blockchain project designed to demonstrate the core concepts of blockchain technology. It provides a simplified but functional implementation of a blockchain system including blocks, transactions, consensus mechanisms, and cryptographic primitives. The goal is to create a learning resource that can be used to understand how blockchains work under the hood without the complexity of production-grade systems.

## Decisions & Assumptions
- Python language with no specific version enforced for broader accessibility
- Virtual environment management with venv + pip for dependency isolation
- Minimal dependencies, focusing on standard library functionality with pytest for testing
- Modular architecture separating core blockchain elements, node functionality, and cryptographic utilities
- Simplified implementations of complex features like SegWit and Merkle trees
- Account-based model (like Ethereum) rather than UTXO model (like Bitcoin)
- Deterministic hashing for transaction IDs and blocks using canonical JSON representation
- EIP-1559 style fee mechanism with base fee and tips

## Completed Work
- Created project structure with the following files:
  - core/block.py, core/tx.py, core/chain.py, core/fees.py
  - node/full_node.py, node/light_wallet.py, node/mempool.py, node/mining.py
  - crypto/merkle.py, crypto/bloom.py, crypto/keys.py, crypto/signatures.py, crypto/segwit.py
  - sim/init_state.json, sim/mempool_init.json
  - cli/main.py
  - tests/test_smoke.py
  - README.md, summary.md, requirements.txt
  - make_venv.sh, make_venv.ps1
- Added placeholder code for core functionality
- Created initial test framework
- Implemented environment setup scripts
- Implemented core blockchain models:
  - Transaction (Tx) class with sender, recipient, amount, nonce, base_fee, tip
  - Deterministic transaction serialization and ID generation
  - Block and BlockHeader classes with proper structure
  - Blockchain class with account balances tracking (without fees/signatures)
- Implemented fee rules + mempool integration:
  - Fee constants (BLOCK_REWARD=50, BASE_FEE=2, TIP=3)
  - Fee calculation helpers in core/fees.py
  - FIFO-based Mempool implementation
  - Updated Blockchain.apply_block to process transactions with fees
  - Added test cases to validate fee collection and blockchain balance invariants
- Implemented basic mining flow:
  - Added build_candidate_block function in mining.py
  - Implemented simple nonce increment loop for proof-of-work
  - Enhanced Blockchain.validate_block_structure to enforce max 4 transactions per block
  - Added Blockchain.add_block method for validation and application
  - Created CLI command for single-block mining
  - Added tests for mining and block validation

## Completed Work (continued)
- Implemented Merkle tree library for efficient verification:
  - Added merkle_root, merkle_proof, and verify_proof functions in crypto/merkle.py
  - Integrated with mining module to use real Merkle roots for candidate blocks
  - Enhanced FullNode to support generating Merkle proofs for transactions
  - Created test cases to validate Merkle functionality

## Completed Work (Bloom + light wallet)
- Implemented Bloom filter for fast transaction lookups:
  - Created BloomFilter class in crypto/bloom.py with SHA-256 based hashing
  - Configurable parameters for bit size (m_bits) and hash function count (k)
  - Methods for adding items and checking potential membership
- Enhanced FullNode with Bloom filter integration:
  - Added functionality to build Bloom filters for finalized blocks
  - Implemented API for might_contain_tx and improved get_merkle_proof
  - Optimized transaction lookup with fast Bloom filter checks
- Implemented light wallet transaction verification:
  - Two-step verification process using Bloom filters and Merkle proofs
  - Efficient check_tx_in_block method for verifying transaction inclusion
  - No false negatives by design, proof validation for all positive matches
- Created comprehensive tests for Bloom filter and light wallet functionality

## Open TODOs / Next Steps
- Implement simplified SegWit functionality
- Create simulation environment for testing and demonstration

## Known Issues / Risks
- Project is currently a basic implementation with limited functionality
- No signature verification implemented yet
- Implementations are educational/simplified and not suitable for production use
- Many TODOs throughout the codebase that need implementation
- Security considerations for a real blockchain are not fully addressed

## Decisions Made
- Fee structure constants: BLOCK_REWARD=50, BASE_FEE=2, TIP=3
- FIFO ordering for mempool transactions for simplicity
- Mempool capacity management using batch extraction (get_batch method)
- Simple balance tracking with burn/mine counters for consistency checks
