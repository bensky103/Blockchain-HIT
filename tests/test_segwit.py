import pytest
from blockchain_lab.crypto import keys, signatures, segwit
from blockchain_lab.core.tx import Tx
from blockchain_lab.core.block import Block
from blockchain_lab.core.chain import Blockchain

@pytest.fixture
def key_pair():
    return keys.generate_key_pair()

@pytest.fixture
def another_key_pair():
    return keys.generate_key_pair()

def test_segwit_signature_verification(key_pair, another_key_pair):
    private_key, public_key = key_pair
    address = keys.get_address_from_pubkey(public_key)

    tx = Tx(
        sender=address,
        recipient=keys.get_address_from_pubkey(another_key_pair[1]),
        amount=10,
        nonce=0
    )
    
    tx.sign(private_key)
    assert tx.signature is not None
    assert tx.sender_pubkey is not None

    # Store signature externally
    segwit.store_signature(tx.tx_id, tx.signature)

    # Verify with the correct public key
    retrieved_sig = segwit.get_signature(tx.tx_id)
    assert retrieved_sig is not None
    
    pub_key_obj = keys.deserialize_public_key(tx.sender_pubkey)
    preimage = tx.get_preimage()
    assert signatures.verify_signature(pub_key_obj, retrieved_sig, preimage)

    # Verification should fail with a different key
    wrong_pub_key = another_key_pair[1]
    assert not signatures.verify_signature(wrong_pub_key, retrieved_sig, preimage)

def test_block_rejection_on_invalid_signature(key_pair, another_key_pair):
    private_key, public_key = key_pair
    address = keys.get_address_from_pubkey(public_key)

    chain = Blockchain()
    chain.add_genesis({"miner": 100, address: 100})

    tx = Tx(
        sender=address,
        recipient=keys.get_address_from_pubkey(another_key_pair[1]),
        amount=10,
        nonce=0
    )
    tx.sign(private_key)
    
    # Tamper with the signature
    tampered_signature = tx.signature[:-5] + b'abcde'
    tx.signature = tampered_signature

    block = Block(
        header=Block.create_genesis_block("miner").header, # dummy header
        txs=[tx]
    )
    block.header.index = 1
    block.header.prev_hash = chain.get_latest_block().block_hash
    
    assert not chain.apply_block(block, "miner")

def test_merkle_root_unaffected_by_signature(key_pair):
    private_key, public_key = key_pair
    address = keys.get_address_from_pubkey(public_key)

    tx1 = Tx(sender=address, recipient="B", amount=10, nonce=0)
    tx_id_before_signing = tx1.tx_id

    tx1.sign(private_key)
    tx_id_after_signing = tx1._calculate_tx_id()

    assert tx_id_before_signing == tx_id_after_signing

    tx2 = Tx(sender=address, recipient="C", amount=5, nonce=1)
    tx2.sign(private_key)

    block1 = Block(header=Block.create_genesis_block("miner").header, txs=[tx1, tx2])
    merkle_root_with_sigs = block1.header.merkle_root

    # Create transactions without signatures
    tx1_no_sig = Tx(sender=address, recipient="B", amount=10, nonce=0)
    tx2_no_sig = Tx(sender=address, recipient="C", amount=5, nonce=1)
    
    block2 = Block(header=Block.create_genesis_block("miner").header, txs=[tx1_no_sig, tx2_no_sig])
    merkle_root_without_sigs = block2.header.merkle_root
    
    # This test is conceptual. The current implementation of Block calculates merkle root
    # on tx_ids from the passed Tx objects. Since tx_id calculation excludes the signature,
    # the merkle root will be the same.
    # A more explicit test would involve stripping signatures before calculating the root.
    from blockchain_lab.crypto.merkle import merkle_root
    root1 = merkle_root([tx1, tx2])
    root2 = merkle_root([tx1_no_sig, tx2_no_sig])
    assert root1 == root2
