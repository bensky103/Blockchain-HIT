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
from core.chain import Blockchain
from core.block import Block
from node.mempool import Mempool
from node.mining import build_candidate_block, mine_block, calculate_mining_reward, calculate_burned_fees

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Blockchain Lab CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create node subcommand
    node_parser = subparsers.add_parser("node", help="Run a full node")
    node_parser.add_argument("--port", type=int, default=8333, help="Port to listen on")
    
    # Create wallet subcommand
    wallet_parser = subparsers.add_parser("wallet", help="Wallet operations")
    wallet_subparsers = wallet_parser.add_subparsers(dest="wallet_command", help="Wallet commands")
    
    # Create wallet
    create_parser = wallet_subparsers.add_parser("create", help="Create a new wallet")
    
    # Get balance
    balance_parser = wallet_subparsers.add_parser("balance", help="Get wallet balance")
    balance_parser.add_argument("--address", type=str, required=True, help="Wallet address")
    
    # Create transaction
    tx_parser = wallet_subparsers.add_parser("send", help="Send coins")
    tx_parser.add_argument("--from", dest="sender", type=str, required=True, help="Sender address")
    tx_parser.add_argument("--to", dest="recipient", type=str, required=True, help="Recipient address")
    tx_parser.add_argument("--amount", type=float, required=True, help="Amount to send")
    tx_parser.add_argument("--fee", type=float, default=0.001, help="Transaction fee")
    
    # Create mining subcommand
    mine_parser = subparsers.add_parser("mine-once", help="Mine a single block")
    mine_parser.add_argument("--miner", type=str, required=True, help="Miner address to receive rewards")
    mine_parser.add_argument("--difficulty", type=int, default=4, help="Mining difficulty (default: 4)")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    if args.command == "node":
        run_node(args)
    elif args.command == "wallet":
        run_wallet(args)
    elif args.command == "mine-once":
        run_mining(args)

def run_node(args):
    """Run a full node."""
    print(f"Starting full node on port {args.port}...")
    # Import only when needed to avoid circular imports
    from node.full_node import FullNode
    node = FullNode()
    # TODO: Implement node functionality
    print("Node started (not yet implemented)")

def run_wallet(args):
    """Run wallet operations."""
    if args.wallet_command is None:
        print("Missing wallet command")
        return
    
    # Import only when needed to avoid circular imports
    from node.light_wallet import LightWallet
    
    if args.wallet_command == "create":
        wallet = LightWallet()
        wallet.generate_keys()
        print(f"New wallet created (not yet implemented)")
    
    elif args.wallet_command == "balance":
        print(f"Balance for address {args.address}: (not yet implemented)")
    
    elif args.wallet_command == "send":
        print(f"Sending {args.amount} from {args.sender} to {args.recipient} with fee {args.fee}")
        print("Transaction creation not yet implemented")

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
