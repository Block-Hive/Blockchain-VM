import pytest
import time
from blockchain.core.block import Block
from blockchain.core.blockchain import Blockchain
from blockchain.core.transaction import Transaction
from blockchain.crypto.wallet import Wallet
from blockchain.utils.initializer import Initializer

@pytest.fixture(scope="session")
def setup_blockchain():
    """Initialize the blockchain for testing."""
    Initializer.initialize()
    blockchain = Blockchain()
    return blockchain

@pytest.fixture
def wallet():
    """Create a test wallet."""
    return Wallet()

def test_block_creation():
    """Example of testing block creation."""
    # Create a block
    block = Block(
        index=0,
        transactions=[],
        previous_hash="0" * 64
    )
    
    # Test block properties
    assert block.index == 0
    assert block.previous_hash == "0" * 64
    assert isinstance(block.timestamp, float)
    assert isinstance(block.hash, str)
    assert len(block.hash) == 64

def test_transaction_creation(wallet):
    """Example of testing transaction creation and signing."""
    # Create a transaction
    transaction = Transaction(
        sender=wallet.address,
        recipient="recipient_address",
        amount=10.0
    )
    
    # Sign the transaction
    transaction.sign(wallet.private_key)
    
    # Verify the transaction
    assert transaction.verify()
    assert transaction.sender == wallet.address
    assert transaction.recipient == "recipient_address"
    assert transaction.amount == 10.0

def test_blockchain_operations(setup_blockchain, wallet):
    """Example of testing blockchain operations."""
    blockchain = setup_blockchain
    
    # Create and add a transaction
    transaction = Transaction(
        sender=wallet.address,
        recipient="recipient_address",
        amount=10.0
    )
    transaction.sign(wallet.private_key)
    
    # Add transaction to pool
    assert blockchain.add_transaction(transaction)
    
    # Mine a new block
    new_block = blockchain.mine_block(wallet.address)
    
    # Verify the block
    assert new_block is not None
    assert new_block.index == len(blockchain.chain) - 1
    assert new_block.previous_hash == blockchain.chain[-2].hash
    assert len(new_block.transactions) > 0
    assert blockchain._is_valid_block(new_block)

def test_wallet_operations():
    """Example of testing wallet operations."""
    # Create a new wallet
    wallet = Wallet()
    
    # Test wallet properties
    assert isinstance(wallet.address, str)
    assert len(wallet.address) > 0
    assert wallet.public_key is not None
    assert wallet.private_key is not None
    
    # Test wallet persistence
    wallet_data = wallet.to_dict()
    new_wallet = Wallet.from_dict(wallet_data)
    
    assert new_wallet.address == wallet.address
    assert new_wallet.public_key == wallet.public_key 