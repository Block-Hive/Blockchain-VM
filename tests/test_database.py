import pytest
from typing import Dict, Any

def test_save_and_get_block(db_manager: Any) -> None:
    """Test saving and retrieving a block."""
    block = {
        'index': 0,
        'timestamp': 1234567890.0,
        'previous_hash': '0',
        'proof': 100,
        'hash': 'test_hash'
    }
    
    db_manager.save_block(block)
    retrieved_block = db_manager.get_block(0)
    
    assert retrieved_block is not None
    assert retrieved_block['index'] == block['index']
    assert retrieved_block['timestamp'] == block['timestamp']
    assert retrieved_block['previous_hash'] == block['previous_hash']
    assert retrieved_block['proof'] == block['proof']
    assert retrieved_block['hash'] == block['hash']

def test_save_and_get_transaction(db_manager: Any) -> None:
    """Test saving and retrieving a transaction."""
    # First save a block to reference
    block = {
        'index': 0,
        'timestamp': 1234567890.0,
        'previous_hash': '0',
        'proof': 100,
        'hash': 'test_hash'
    }
    db_manager.save_block(block)
    
    transaction = {
        'sender': 'test_sender',
        'recipient': 'test_recipient',
        'amount': 1.0,
        'signature': 'test_signature'
    }
    
    db_manager.save_transaction(transaction, 0)
    transactions = db_manager.get_block_transactions(0)
    
    assert len(transactions) == 1
    assert transactions[0]['sender'] == transaction['sender']
    assert transactions[0]['recipient'] == transaction['recipient']
    assert transactions[0]['amount'] == transaction['amount']
    assert transactions[0]['signature'] == transaction['signature']

def test_save_and_get_transaction_confirmations(db_manager: Any) -> None:
    """Test saving and retrieving transaction confirmations."""
    # First save a block to reference
    block = {
        'index': 0,
        'timestamp': 1234567890.0,
        'previous_hash': '0',
        'proof': 100,
        'hash': 'test_hash'
    }
    db_manager.save_block(block)
    
    transaction_hash = 'test_transaction_hash'
    db_manager.save_transaction_confirmation(transaction_hash, 0, 1)
    
    confirmations = db_manager.get_transaction_confirmations(transaction_hash)
    assert confirmations == 1

def test_save_and_get_difficulty(db_manager: Any) -> None:
    """Test saving and retrieving difficulty data."""
    # First save a block to reference
    block = {
        'index': 0,
        'timestamp': 1234567890.0,
        'previous_hash': '0',
        'proof': 100,
        'hash': 'test_hash'
    }
    db_manager.save_block(block)
    
    db_manager.save_difficulty(0, 4, 10.0)
    
    # Note: We don't have a direct getter for difficulty history
    # This is just to verify the save operation doesn't raise an error

def test_save_and_get_nodes(db_manager: Any) -> None:
    """Test saving and retrieving nodes."""
    node_address = 'http://localhost:5000'
    db_manager.save_node(node_address)
    
    nodes = db_manager.get_active_nodes()
    assert len(nodes) == 1
    assert nodes[0] == node_address

def test_clear_database(db_manager: Any) -> None:
    """Test clearing the database."""
    # Save some test data
    block = {
        'index': 0,
        'timestamp': 1234567890.0,
        'previous_hash': '0',
        'proof': 100,
        'hash': 'test_hash'
    }
    db_manager.save_block(block)
    
    transaction = {
        'sender': 'test_sender',
        'recipient': 'test_recipient',
        'amount': 1.0,
        'signature': 'test_signature'
    }
    db_manager.save_transaction(transaction, 0)
    
    db_manager.save_node('http://localhost:5000')
    
    # Clear the database
    db_manager.clear_database()
    
    # Verify everything is cleared
    assert db_manager.get_block(0) is None
    assert len(db_manager.get_block_transactions(0)) == 0
    assert len(db_manager.get_active_nodes()) == 0 