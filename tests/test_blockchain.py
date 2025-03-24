import pytest
from typing import Dict, Any

def test_create_genesis_block(blockchain: Any) -> None:
    """Test creation of genesis block."""
    genesis_block = blockchain.get_block(0)
    assert genesis_block is not None
    assert genesis_block['index'] == 0
    assert genesis_block['previous_hash'] == '0'
    assert genesis_block['proof'] == 100
    assert genesis_block['hash'] is not None

def test_mine_block(blockchain: Any, test_transaction: Dict[str, Any]) -> None:
    """Test mining a new block."""
    # Add transaction to pool
    blockchain.add_transaction(test_transaction)
    
    # Mine new block
    new_block = blockchain.mine_block()
    
    assert new_block is not None
    assert new_block['index'] == 1
    assert new_block['previous_hash'] == blockchain.get_block(0)['hash']
    assert new_block['proof'] > 0
    assert new_block['hash'] is not None
    assert blockchain.verify_proof(new_block['proof'], new_block['previous_hash'])

def test_add_transaction(blockchain: Any, test_transaction: Dict[str, Any]) -> None:
    """Test adding a transaction to the pool."""
    blockchain.add_transaction(test_transaction)
    assert len(blockchain.current_transactions) == 1
    assert blockchain.current_transactions[0] == test_transaction

def test_get_balance(blockchain: Any, wallet: Any) -> None:
    """Test getting balance for an address."""
    # Mine a block to get reward
    blockchain.mine_block()
    
    # Get balance
    balance = blockchain.get_balance(wallet.get_address())
    assert balance >= blockchain.block_reward

def test_verify_chain(blockchain: Any) -> None:
    """Test chain verification."""
    # Mine a few blocks
    for _ in range(3):
        blockchain.mine_block()
    
    # Verify chain
    assert blockchain.verify_chain()

def test_verify_proof(blockchain: Any) -> None:
    """Test proof verification."""
    # Mine a block
    block = blockchain.mine_block()
    
    # Verify proof
    assert blockchain.verify_proof(block['proof'], block['previous_hash'])
    
    # Try invalid proof
    assert not blockchain.verify_proof(block['proof'] + 1, block['previous_hash'])

def test_transaction_confirmation(blockchain: Any, test_transaction: Dict[str, Any]) -> None:
    """Test transaction confirmation tracking."""
    # Add transaction to pool
    blockchain.add_transaction(test_transaction)
    
    # Mine block containing transaction
    blockchain.mine_block()
    
    # Get transaction hash
    transaction_hash = blockchain.hash_transaction(test_transaction)
    
    # Check confirmations
    confirmations = blockchain.get_transaction_confirmations(transaction_hash)
    assert confirmations == 1
    
    # Mine more blocks
    for _ in range(blockchain.confirmation_blocks):
        blockchain.mine_block()
    
    # Check if transaction is confirmed
    assert blockchain.is_transaction_confirmed(transaction_hash)

# def test_difficulty_adjustment(blockchain: Any) -> None:
#     """Test difficulty adjustment."""
#     initial_difficulty = blockchain.difficulty
    
#     # Mine blocks quickly
#     for _ in range(blockchain.difficulty_adjustment_interval):
#         blockchain.mine_block()
    
#     # Difficulty should increase
#     assert blockchain.difficulty > initial_difficulty
    
#     # Mine blocks slowly (simulate by adjusting timestamps)
#     for _ in range(blockchain.difficulty_adjustment_interval):
#         blockchain.mine_block()
    
#     # Difficulty should decrease
#     assert blockchain.difficulty < blockchain.difficulty

def test_block_size_limit(blockchain: Any, test_transaction: Dict[str, Any]) -> None:
    """Test block size limit."""
    # Add more transactions than max block size
    for _ in range(blockchain.max_block_size + 1):
        blockchain.add_transaction(test_transaction)
    
    # Mine block
    block = blockchain.mine_block()
    
    # Check that only max_block_size transactions were included
    transactions = blockchain.get_block_transactions(block['index'])
    assert len(transactions) <= blockchain.max_block_size 