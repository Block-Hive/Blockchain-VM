import pytest
import time
from blockchain.core.block import Block
from blockchain.core.blockchain import Blockchain
from blockchain.core.transaction import Transaction
from blockchain.core.transaction_pool import TransactionPool
from blockchain.crypto.wallet import Wallet

def test_block_creation():
    """Test block creation and validation."""
    # Create a block
    block = Block(
        index=0,
        transactions=[],
        timestamp=time.time(),
        previous_hash="0" * 64
    )
    
    # Verify block properties
    assert block.index == 0
    assert len(block.transactions) == 0
    assert block.previous_hash == "0" * 64
    assert block.hash is not None
    
    # Test block mining
    block.mine_block(4)  # Mine with difficulty 4
    assert block.hash.startswith("0" * 4)
    assert block.is_valid(4)

def test_blockchain_creation():
    """Test blockchain creation and basic operations."""
    # Create blockchain
    blockchain = Blockchain(difficulty=4)
    
    # Verify genesis block
    assert len(blockchain.chain) == 1
    assert blockchain.chain[0].index == 0
    assert blockchain.chain[0].previous_hash == "0" * 64
    
    # Test adding transaction
    transaction = {
        'from': 'test_sender',
        'to': 'test_recipient',
        'amount': 10.0,
        'timestamp': time.time()
    }
    assert blockchain.add_transaction(transaction)
    
    # Test mining new block
    block = blockchain.mine_pending_transactions('test_miner')
    assert len(blockchain.chain) == 2
    assert block.index == 1
    assert len(block.transactions) == 2  # Including mining reward
    assert block.is_valid(4)

def test_transaction_creation_and_validation():
    """Test transaction creation and validation."""
    # Create wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    # Create transaction
    transaction = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=10.0
    )
    
    # Sign transaction
    transaction.sign(sender_wallet)
    
    # Verify transaction
    assert transaction.is_valid(sender_wallet)
    assert not transaction.is_valid(recipient_wallet)  # Wrong wallet

def test_transaction_pool():
    """Test transaction pool operations."""
    # Create pool
    pool = TransactionPool(max_size=2)
    
    # Create wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    # Create and add transaction
    transaction = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=10.0
    )
    transaction.sign(sender_wallet)
    
    assert pool.add_transaction(transaction, sender_wallet)
    assert pool.get_transaction_count() == 1
    
    # Test pool size limit
    transaction2 = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=20.0
    )
    transaction2.sign(sender_wallet)
    
    assert pool.add_transaction(transaction2, sender_wallet)
    assert pool.get_transaction_count() == 2
    
    # Pool should be full now
    transaction3 = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=30.0
    )
    transaction3.sign(sender_wallet)
    
    assert not pool.add_transaction(transaction3, sender_wallet)
    assert pool.get_transaction_count() == 2

def test_blockchain_consensus():
    """Test blockchain consensus mechanism."""
    # Create two blockchains
    blockchain1 = Blockchain(difficulty=4)
    blockchain2 = Blockchain(difficulty=4)
    
    # Add different transactions to each
    blockchain1.add_transaction({
        'from': 'test1',
        'to': 'test2',
        'amount': 10.0,
        'timestamp': time.time()
    })
    
    blockchain2.add_transaction({
        'from': 'test3',
        'to': 'test4',
        'amount': 20.0,
        'timestamp': time.time()
    })
    
    # Mine blocks
    blockchain1.mine_pending_transactions('miner1')
    blockchain2.mine_pending_transactions('miner2')
    
    # Try to replace chain
    assert blockchain1.replace_chain(blockchain2.to_dict()['chain'])
    assert len(blockchain1.chain) == 2  # Should have adopted the longer chain

def test_wallet_operations():
    """Test wallet operations."""
    # Create wallet
    wallet = Wallet(password="test_password")
    
    # Verify wallet properties
    assert wallet.private_key is not None
    assert wallet.public_key is not None
    assert wallet.get_address() is not None
    
    # Test transaction signing
    transaction = Transaction(
        sender=wallet.get_address(),
        recipient="test_recipient",
        amount=10.0
    )
    
    transaction.sign(wallet)
    assert transaction.signature is not None
    assert transaction.is_valid(wallet)
    
    # Test wallet persistence
    wallet_data = wallet.to_dict()
    assert 'public_key' in wallet_data
    assert 'address' in wallet_data 