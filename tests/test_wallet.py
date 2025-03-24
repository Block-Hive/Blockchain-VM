import os
import pytest
from typing import Dict, Any

def test_create_wallet(wallet: Any) -> None:
    """Test wallet creation."""
    assert wallet is not None
    assert wallet.private_key is not None
    assert wallet.public_key is not None
    assert wallet.address is not None

def test_wallet_persistence(wallet: Any) -> None:
    """Test wallet persistence."""
    # Save wallet
    wallet.save_wallet()
    
    # Create new wallet instance
    new_wallet = Wallet()
    new_wallet.load_wallet()
    
    # Verify wallet data is preserved
    assert new_wallet.private_key == wallet.private_key
    assert new_wallet.public_key == wallet.public_key
    assert new_wallet.address == wallet.address

def test_get_address(wallet: Any) -> None:
    """Test getting wallet address."""
    address = wallet.get_address()
    assert address is not None
    assert isinstance(address, str)
    assert len(address) > 0

def test_get_public_key(wallet: Any) -> None:
    """Test getting wallet public key."""
    public_key = wallet.get_public_key()
    assert public_key is not None
    assert isinstance(public_key, str)
    assert len(public_key) > 0

def test_sign_transaction(wallet: Any) -> None:
    """Test transaction signing."""
    transaction = {
        'sender': wallet.get_address(),
        'recipient': 'test_recipient',
        'amount': 1.0
    }
    
    signature = wallet.sign_transaction(transaction)
    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) > 0

def test_verify_signature(wallet: Any) -> None:
    """Test signature verification."""
    transaction = {
        'sender': wallet.get_address(),
        'recipient': 'test_recipient',
        'amount': 1.0
    }
    
    signature = wallet.sign_transaction(transaction)
    assert wallet.verify_signature(transaction, signature)
    
    # Try with modified transaction
    modified_transaction = transaction.copy()
    modified_transaction['amount'] = 2.0
    assert not wallet.verify_signature(modified_transaction, signature)

def test_get_balance(blockchain: Any, wallet: Any) -> None:
    """Test getting wallet balance from blockchain."""
    # Mine a block to get reward
    blockchain.mine_block()
    
    # Get balance
    balance = wallet.get_balance(blockchain)
    assert balance >= blockchain.block_reward

def test_create_transaction(wallet: Any, blockchain: Any) -> None:
    """Test creating a new transaction."""
    # Mine a block to get some coins
    blockchain.mine_block()
    
    # Create transaction
    transaction = wallet.create_transaction('test_recipient', 1.0, blockchain)
    
    assert transaction is not None
    assert transaction['sender'] == wallet.get_address()
    assert transaction['recipient'] == 'test_recipient'
    assert transaction['amount'] == 1.0
    assert transaction['signature'] is not None
    
    # Verify transaction
    assert wallet.verify_signature(transaction, transaction['signature'])

def test_cleanup(wallet: Any) -> None:
    """Test wallet cleanup."""
    # Save wallet
    wallet.save_wallet()
    
    # Verify file exists
    assert os.path.exists(wallet.wallet_file)
    
    # Clean up
    if os.path.exists(wallet.wallet_file):
        os.remove(wallet.wallet_file)
    
    # Verify file is removed
    assert not os.path.exists(wallet.wallet_file) 