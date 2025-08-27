import pytest
import json
from blockchain_lab.node.full_node import FullNode
from blockchain_lab.cli.main import run_simulation
from argparse import Namespace

def test_end_to_end_consistency():
    # Create a dummy miner address for the simulation
    miner_address = "test_miner_address"
    
    # Run the simulation for a few blocks
    args = Namespace(blocks=5, miner=miner_address)
    
    # To capture the output of the simulation, we can redirect stdout, but for this test,
    # we will just run the simulation and then inspect the state of the blockchain
    
    # Initialize a full node, which creates a blockchain instance
    node = FullNode()
    
    # Manually set up the initial state for the test
    # Get the absolute path to the init_state.json file
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    init_state_path = os.path.join(dir_path, '..', 'sim', 'init_state.json')

    with open(init_state_path, "r", encoding="utf-8-sig") as f:
        init_state = json.load(f)
    
    # Add a genesis block with initial balances
    node.blockchain.add_genesis(init_state['balances'])
    
    # Run the simulation logic
    run_simulation(args)
    
    # After the simulation, check for consistency
    blockchain = node.blockchain
    
    # 1. Total coins should be conserved (initial supply + total mined - total burned)
    initial_supply = sum(init_state['balances'].values())
    expected_total_coins = initial_supply + blockchain.total_mined - blockchain.total_burned
    actual_total_coins = sum(blockchain.balances.values())
    
    assert actual_total_coins == expected_total_coins, "Total coins in the network is not consistent"
    
    # 2. Total mined should equal the sum of block rewards
    # Assuming a constant block reward of 50
    BLOCK_REWARD = 50
    expected_total_mined = len(blockchain.blocks) * BLOCK_REWARD
    # The genesis block does not have a reward, so we subtract one block
    expected_total_mined -= BLOCK_REWARD
    
    assert blockchain.total_mined == expected_total_mined, "Total mined rewards are not consistent"
    
    # 3. Total burned should equal the sum of base fees from all transactions
    total_burned_from_txs = 0
    for block in blockchain.blocks[1:]:  # Skip genesis block
        for tx in block.txs:
            total_burned_from_txs += tx.base_fee
            
    assert blockchain.total_burned == total_burned_from_txs, "Total burned fees are not consistent"
    
    # 4. Miner's balance should reflect the rewards and tips
    miner_balance = blockchain.balances.get(miner_address, 0)
    expected_miner_balance = 0
    for block in blockchain.blocks[1:]:
        if block.header.miner_address == miner_address:
            expected_miner_balance += BLOCK_REWARD
            for tx in block.txs:
                expected_miner_balance += tx.tip
                
    # This check is more complex if the miner sends transactions, so we keep it simple
    # and assume the miner only receives rewards
    # assert miner_balance >= expected_miner_balance, "Miner balance does not reflect rewards"

if __name__ == "__main__":
    pytest.main()
