import pytest
from blockchain.api.app import app
from blockchain.crypto.wallet import Wallet
import json

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_chain(client):
    """Test getting the blockchain."""
    response = client.get('/chain')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'chain' in data
    assert len(data['chain']) == 1  # Should have genesis block

def test_get_pending_transactions(client):
    """Test getting pending transactions."""
    response = client.get('/transactions/pending')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'pending_transactions' in data
    assert isinstance(data['pending_transactions'], list)

def test_new_transaction(client):
    """Test creating a new transaction."""
    # Create wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    # Create transaction data
    transaction_data = {
        'sender': sender_wallet.get_address(),
        'recipient': recipient_wallet.get_address(),
        'amount': 10.0
    }
    
    # Sign transaction
    transaction_data['signature'] = sender_wallet.sign_transaction(transaction_data)
    
    # Send request
    response = client.post(
        '/transactions/new',
        data=json.dumps(transaction_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Transaction added to pool'

def test_mine_block(client):
    """Test mining a new block."""
    # Create wallet for miner
    miner_wallet = Wallet()
    
    # Send request
    response = client.get(f'/mine?address={miner_wallet.get_address()}')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert 'block' in data
    assert data['message'] == 'New block mined'

def test_register_node(client):
    """Test registering a new node."""
    node_data = {
        'node_id': 'test_node'
    }
    
    response = client.post(
        '/nodes/register',
        data=json.dumps(node_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Node registered'

def test_resolve_conflicts(client):
    """Test resolving blockchain conflicts."""
    response = client.get('/nodes/resolve')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'chain_length' in data
    assert data['message'] == 'Chain sync initiated'

def test_create_wallet(client):
    """Test creating a new wallet."""
    response = client.get('/wallet/new')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'address' in data
    assert 'public_key' in data
    assert isinstance(data['address'], str)
    assert isinstance(data['public_key'], str)

def test_get_balance(client):
    """Test getting wallet balance."""
    # Create wallet
    wallet = Wallet()
    address = wallet.get_address()
    
    # Send request
    response = client.get(f'/wallet/balance?address={address}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'balance' in data
    assert isinstance(data['balance'], (int, float))

def test_invalid_transaction(client):
    """Test creating an invalid transaction."""
    # Send request with missing fields
    response = client.post(
        '/transactions/new',
        data=json.dumps({
            'sender': 'test_sender',
            'recipient': 'test_recipient'
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Missing required fields'

def test_mine_without_address(client):
    """Test mining without providing miner address."""
    response = client.get('/mine')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Miner address required'

def test_register_node_without_id(client):
    """Test registering a node without ID."""
    response = client.post(
        '/nodes/register',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Node ID required'

def test_get_balance_without_address(client):
    """Test getting balance without providing address."""
    response = client.get('/wallet/balance')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Address required' 