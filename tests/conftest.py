import os
import pytest
from typing import Generator, Dict, Any
from dotenv import load_dotenv

from blockchain.src.database import DatabaseManager
from blockchain.src.blockchain import Blockchain
from blockchain.src.wallet import Wallet
from blockchain.src.api import create_app

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def db_manager():
    """Create a database manager for testing."""
    db = DatabaseManager()
    db.clear_database()  # Clear the database before each test
    return db

@pytest.fixture
def blockchain(db_manager):
    """Create a blockchain instance for testing."""
    chain = Blockchain(db_manager)
    return chain

@pytest.fixture
def wallet():
    """Create a wallet instance for testing."""
    return Wallet("test_wallet.json")

@pytest.fixture(scope='session')
def app(blockchain: Blockchain) -> Generator[Any, None, None]:
    """Create a Flask app instance for testing."""
    app = create_app(blockchain)
    app.config['TESTING'] = True
    yield app

@pytest.fixture(scope='session')
def client(app: Any) -> Generator[Any, None, None]:
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def test_transaction(wallet: Wallet) -> Dict[str, Any]:
    """Create a test transaction."""
    return {
        'sender': wallet.get_address(),
        'recipient': 'test_recipient',
        'amount': 1.0,
        'signature': wallet.sign_transaction({
            'sender': wallet.get_address(),
            'recipient': 'test_recipient',
            'amount': 1.0
        })
    } 