import pytest
from typing import Dict, Any

def test_mine_endpoint(client: Any) -> None:
    """Test the /mine endpoint."""
    response = client.post('/mine')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'index' in data
    assert 'transactions' in data
    assert 'proof' in data
    assert 'previous_hash' in data

def test_new_transaction_endpoint(client: Any, test_transaction: Dict[str, Any]) -> None:
    """Test the /transactions/new endpoint."""
    response = client.post('/transactions/new',
                         json=test_transaction,
                         content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'transaction' in data

def test_get_chain_endpoint(client: Any) -> None:
    """Test the /chain endpoint."""
    response = client.get('/chain')
    assert response.status_code == 200
    data = response.get_json()
    assert 'chain' in data
    assert 'length' in data
    assert isinstance(data['chain'], list)
    assert isinstance(data['length'], int)

def test_register_node_endpoint(client: Any) -> None:
    """Test the /nodes/register endpoint."""
    nodes = {
        'nodes': ['http://localhost:5001']
    }
    response = client.post('/nodes/register',
                         json=nodes,
                         content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data
    assert 'total_nodes' in data
    assert isinstance(data['total_nodes'], list)

def test_consensus_endpoint(client: Any) -> None:
    """Test the /nodes/resolve endpoint."""
    response = client.get('/nodes/resolve')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'chain' in data
    assert isinstance(data['chain'], list)

def test_get_balance_endpoint(client: Any, wallet: Any) -> None:
    """Test the /balance/<address> endpoint."""
    response = client.get(f'/balance/{wallet.get_address()}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'balance' in data
    assert isinstance(data['balance'], (int, float))

def test_get_transaction_confirmations_endpoint(client: Any, test_transaction: Dict[str, Any]) -> None:
    """Test the /transaction/<hash>/confirmations endpoint."""
    # First create a transaction
    client.post('/transactions/new',
                json=test_transaction,
                content_type='application/json')
    
    # Mine a block to include the transaction
    client.post('/mine')
    
    # Get transaction hash
    transaction_hash = test_transaction.get('hash', 'test_hash')
    
    # Get confirmations
    response = client.get(f'/transaction/{transaction_hash}/confirmations')
    assert response.status_code == 200
    data = response.get_json()
    assert 'confirmations' in data
    assert 'is_confirmed' in data
    assert isinstance(data['confirmations'], int)
    assert isinstance(data['is_confirmed'], bool)

def test_heartbeat_endpoint(client: Any) -> None:
    """Test the /heartbeat endpoint."""
    response = client.post('/heartbeat')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'ok'

def test_get_nodes_endpoint(client: Any) -> None:
    """Test the /nodes endpoint."""
    response = client.get('/nodes')
    assert response.status_code == 200
    data = response.get_json()
    assert 'nodes' in data
    assert isinstance(data['nodes'], list)

def test_rate_limiting(client: Any) -> None:
    """Test API rate limiting."""
    # Make more requests than the rate limit
    for _ in range(1000):
        response = client.get('/chain')
        if response.status_code == 429:
            break
    
    # Verify rate limit response
    assert response.status_code == 429
    data = response.get_json()
    assert 'error' in data
    assert 'Rate limit exceeded' in data['error']

def test_invalid_transaction(client: Any) -> None:
    """Test handling of invalid transactions."""
    invalid_transaction = {
        'sender': 'invalid_sender',
        'recipient': 'test_recipient',
        'amount': -1.0,
        'signature': 'invalid_signature'
    }
    
    response = client.post('/transactions/new',
                         json=invalid_transaction,
                         content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_invalid_node_registration(client: Any) -> None:
    """Test handling of invalid node registration."""
    invalid_nodes = {
        'nodes': ['invalid_url']
    }
    
    response = client.post('/nodes/register',
                         json=invalid_nodes,
                         content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data 