#!/usr/bin/env python3
"""
Command-line interface for the blockchain lab.
"""

import argparse
import sys
import os
import json

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use relative imports from parent directory
from ..core.chain import Blockchain
from ..core.block import Block
from ..core.tx import Tx
from ..node.mempool import Mempool
from ..node.mining import build_candidate_block, mine_block
from ..node.light_wallet import LightWallet
from ..node.full_node import FullNode
from ..crypto.keys import deserialize_private_key
from ..crypto.signatures import sign_data
from ..core.fees import calculate_mining_reward, calculate_burned_fees

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Blockchain Lab CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # --- Simulation Command ---
    sim_parser = subparsers.add_parser("simulate", help="Run a blockchain simulation")
    sim_parser.add_argument("--blocks", type=int, required=True, help="Number of blocks to mine")
    sim_parser.add_argument("--miner", type=str, required=True, help="Miner address for rewards")

    # --- Light Check Command ---
    light_parser = subparsers.add_parser("light-check", help="Verify a transaction with a light client")
    light_parser.add_argument("--tx_id", type=str, required=True, help="Transaction ID to verify")
    light_parser.add_argument("--block", type=int, required=True, help="Block index to check")

    # --- Mine Once Command (for debugging) ---
    mine_parser = subparsers.add_parser("mine-once", help="Mine a single block")
    mine_parser.add_argument("--miner", type=str, required=True, help="Miner address to receive rewards")
    mine_parser.add_argument("--difficulty", type=int, default=4, help="Mining difficulty")

    args = parser.parse_args()

    if args.command == "simulate":
        run_simulation(args)
    elif args.command == "light-check":
        run_light_check(args)
    elif args.command == "mine-once":
        run_mining(args)
    else:
        parser.print_help()

def run_simulation(args):
    """Runs a full simulation, mining N blocks and printing a summary."""
    print("--- Starting Blockchain Simulation ---")

    # 1. Initialize Full Node and Blockchain
    node = FullNode()
    blockchain = node.blockchain
    # Optionally enforce exactly 4 tx per block by enabling flag below:
    # blockchain.enforce_block_tx_count = 4

    # Load initial state
    # Get the absolute path to the init_state.json file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    init_state_path = os.path.join(dir_path, '..', 'sim', 'init_state.json')
    with open(init_state_path, "r", encoding="utf-8-sig") as f:
        init_state = json.load(f)
    blockchain.add_genesis(init_state['balances'])
    wallets = init_state['wallets']
    print(f"Initialized blockchain with {len(wallets)} wallets and genesis block.")

    # 2. Load Mempool
    mempool_init_path = os.path.join(dir_path, '..', 'sim', 'mempool_init.json')
    with open(mempool_init_path, "r", encoding="utf-8-sig") as f:
        mempool_data = json.load(f)
    
    for tx_data in mempool_data['transactions']:
        # Find the sender's private key from the wallets dict
        sender_pk = None
        for wallet_info in wallets.values():
            if wallet_info['public_key'] == tx_data['sender']:
                sender_pk = wallet_info['private_key']
                break
        
        if not sender_pk:
            # print(f"Skipping transaction with unknown sender: {tx_data['sender'][:10]}...")
            continue

        tx = Tx.from_dict(tx_data)
        
        # Sign the transaction before adding to mempool
        private_key = deserialize_private_key(sender_pk)
        tx.sign(private_key)
        
        # Add to signature store and mempool
        node.signature_store[tx.tx_id] = tx.signature
        node.mempool.accept(tx)

    print(f"Loaded {len(node.mempool.transactions)} transactions into the mempool.")

    # 3. Mining Loop
    mining_log = []
    for i in range(args.blocks):
        prev_block = blockchain.get_latest_block()
        tx_batch = node.mempool.get_batch(max_txs=4)
        # If enforcing exactly 4 and we have fewer pending, we could skip or mine empty.
        if getattr(blockchain, 'enforce_block_tx_count', None) == 4 and tx_batch and len(tx_batch) not in (0,4):
            # Put transactions back (simple rollback) and break for demo purposes
            for tx in tx_batch:
                node.mempool.accept(tx)
            print("Skipping mining this round to wait for a full batch of 4 transactions")
            continue

        if not tx_batch:
            print(f"Block {i+1}: No valid transactions in mempool. Mining an empty block.")
        
        candidate_block = build_candidate_block(prev_block, args.miner, tx_batch)
        mine_block(candidate_block, difficulty=4)
        
        if blockchain.add_block(candidate_block, args.miner):
            block_reward = blockchain.blocks[-1].header.block_reward
            block_burned = blockchain.blocks[-1].header.burned_fees
            mining_log.append({
                "index": candidate_block.header.index,
                "tx_count": len(tx_batch),
                "rewards": block_reward,
                "burned": block_burned
            })
            print(f"Mined Block {candidate_block.header.index} with {len(tx_batch)} transactions.")
        else:
            print(f"Failed to add block {i+1} to the chain.")

    # 4. Print Final Report
    print("\n--- Simulation Complete ---")
    print("\nFinal Balances:")
    for address, balance in blockchain.balances.items():
        # Find wallet name for readability
        wallet_name = "Unknown"
        for name, info in wallets.items():
            if info['address'] == address:
                wallet_name = name
                break
        print(f"  - {wallet_name} ({address[:10]}...): {balance} coins")
    
    print("\nNetwork State:")
    total_coins = sum(blockchain.balances.values())
    print(f"  - Total Coins in Network: {total_coins}")
    print(f"  - Total Mined: {blockchain.total_mined}")
    print(f"  - Total Burned: {blockchain.total_burned}")

    print("\nMining Log:")
    for entry in mining_log:
        print(f"  - Block {entry['index']}: {entry['tx_count']} txs, Reward: {entry['rewards']}, Burned: {entry['burned']}")

def run_light_check(args):
    """Uses a light wallet to verify a transaction's presence."""
    print(f"--- Light Wallet Check ---")
    # In a real app, the light wallet would connect to a full node's API.
    # Here, we simulate it by giving it direct access to the node's state.
    
    # 1. Setup a full node and run a simulation to populate it
    node = FullNode()
    # For this check, we need a populated blockchain. We can run a mini-simulation.
    # This is not efficient but sufficient for a CLI tool demonstration.
    sim_args = argparse.Namespace(blocks=5, miner="light_check_miner")
    run_simulation(sim_args) # This will populate the node instance passed by reference implicitly
    
    # 2. Perform the check
    light_wallet = LightWallet(full_node_ref=node)
    is_present = light_wallet.check_tx_in_block(args.block, args.tx_id)
    
    print(f"\nVerification Result:")
    print(f"  - Transaction ID: {args.tx_id}")
    print(f"  - Block Index:    {args.block}")
    if is_present:
        print("  - Status:         ✅ Verified as PRESENT in the block.")
    else:
        print("  - Status:         ❌ Verified as NOT PRESENT in the block.")


def run_mining(args):
    """Run mining operations."""
    print(f"Mining a block with miner address: {args.miner}")
    
    # Load blockchain state or create a new one
    # In a real implementation, this would load from disk
    blockchain = Blockchain()
    
    # For demonstration, create a genesis block if chain is empty
    if not blockchain.blocks:
        initial_balances = {
            "alice": 1000,
            "bob": 500,
            "charlie": 200,
            args.miner: 0  # Ensure miner has an account
        }
        blockchain.add_genesis(initial_balances)
        print("Created genesis block with initial balances")
    
    # Create a mempool with some transactions
    mempool = Mempool(blockchain.balances)
    
    # In a real implementation, the mempool would be persisted
    # For now, we'll just use it locally
    
    # Get batch of transactions from mempool (max 4)
    tx_batch = mempool.get_batch(max_txs=4)
    
    # Get the previous block
    prev_block = blockchain.get_latest_block()
    
    # Build a candidate block
    candidate_block = build_candidate_block(
        prev_block=prev_block,
        miner_address=args.miner,
        mempool_batch=tx_batch
    )
    
    print(f"Created candidate block with {len(tx_batch)} transactions")
    
    # Mine the block
    print("Mining block...")
    success = mine_block(candidate_block, difficulty=args.difficulty)
    
    if not success:
        print("Failed to mine block within nonce limit!")
        return
    
    print(f"Successfully mined block at index {candidate_block.header.index} with nonce {candidate_block.header.nonce}")
    
    # Add the block to the chain
    if blockchain.add_block(candidate_block, args.miner):
        # Calculate rewards and fees
        mining_reward = calculate_mining_reward(tx_batch)
        burned_fees = calculate_burned_fees(tx_batch)
        
        print("\nBlock mining summary:")
        print(f"  Block index: {candidate_block.header.index}")
        print(f"  Transactions: {len(tx_batch)}")
        print(f"  Miner rewards: {mining_reward} coins")
        print(f"  Fees burned: {burned_fees} coins")
        print(f"  Miner balance: {blockchain.balances.get(args.miner, 0)} coins")
        print(f"  Total burned to date: {blockchain.total_burned} coins")
        print(f"  Total mined to date: {blockchain.total_mined} coins")
    else:
        print("Failed to add block to chain - validation failed!")

if __name__ == "__main__":
    main()
