import pytest
from blockchain.network.dht_node import DHTNode
from blockchain.core.block import Block
from blockchain.core.transaction import Transaction
from blockchain.crypto.wallet import Wallet
import time

@pytest.fixture
def node():
    """Create a test DHT node."""
    return DHTNode(
        node_id="test_node",
        host="localhost",
        port=5000
    )

@pytest.fixture
def blockchain():
    """Create a test blockchain."""
    from blockchain.core.blockchain import Blockchain
    return Blockchain(difficulty=4)

@pytest.fixture
def transaction_pool():
    """Create a test transaction pool."""
    from blockchain.core.transaction_pool import TransactionPool
    return TransactionPool()

def test_node_initialization(node):
    """Test node initialization."""
    assert node.node_id == "test_node"
    assert node.host == "localhost"
    assert node.port == 5000
    assert isinstance(node.peers, set)
    assert len(node.peers) == 0

def test_register_components(node, blockchain, transaction_pool):
    """Test registering blockchain and transaction pool with node."""
    node.register_blockchain(blockchain)
    node.register_transaction_pool(transaction_pool)
    
    assert node.blockchain == blockchain
    assert node.transaction_pool == transaction_pool

def test_peer_management(node):
    """Test adding and removing peers."""
    # Add peer
    node.add_peer("peer1")
    assert "peer1" in node.peers
    assert len(node.peers) == 1
    
    # Add another peer
    node.add_peer("peer2")
    assert "peer2" in node.peers
    assert len(node.peers) == 2
    
    # Remove peer
    node.remove_peer("peer1")
    assert "peer1" not in node.peers
    assert len(node.peers) == 1

def test_broadcast_block(node, blockchain):
    """Test broadcasting a new block."""
    node.register_blockchain(blockchain)
    
    # Create a test block
    block = Block(
        index=1,
        transactions=[],
        timestamp=time.time(),
        previous_hash=blockchain.chain[0].hash
    )
    block.mine_block(4)
    
    # Add some peers
    node.add_peer("peer1")
    node.add_peer("peer2")
    
    # Broadcast block
    node.broadcast_block(block)
    # Note: Actual message sending is mocked in the implementation

def test_broadcast_transaction(node, transaction_pool):
    """Test broadcasting a new transaction."""
    node.register_transaction_pool(transaction_pool)
    
    # Create wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    # Create transaction
    transaction = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=10.0
    )
    transaction.sign(sender_wallet)
    
    # Add some peers
    node.add_peer("peer1")
    node.add_peer("peer2")
    
    # Broadcast transaction
    node.broadcast_transaction(transaction)
    # Note: Actual message sending is mocked in the implementation

def test_handle_new_block(node, blockchain, transaction_pool):
    """Test handling a new block message."""
    node.register_blockchain(blockchain)
    node.register_transaction_pool(transaction_pool)
    
    # Create a test block
    block = Block(
        index=1,
        transactions=[],
        timestamp=time.time(),
        previous_hash=blockchain.chain[0].hash
    )
    block.mine_block(4)
    
    # Handle block message
    message = {
        'type': 'new_block',
        'data': block.to_dict()
    }
    node.handle_message(message, "peer1")
    
    # Verify block was added to chain
    assert len(blockchain.chain) == 2
    assert blockchain.chain[1].hash == block.hash

def test_handle_new_transaction(node, transaction_pool):
    """Test handling a new transaction message."""
    node.register_transaction_pool(transaction_pool)
    
    # Create wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    
    # Create transaction
    transaction = Transaction(
        sender=sender_wallet.get_address(),
        recipient=recipient_wallet.get_address(),
        amount=10.0
    )
    transaction.sign(sender_wallet)
    
    # Handle transaction message
    message = {
        'type': 'new_transaction',
        'data': {
            'transaction': transaction.to_dict(),
            'signature': transaction.signature
        }
    }
    node.handle_message(message, "peer1")
    
    # Verify transaction was added to pool
    assert transaction_pool.get_transaction_count() == 1

def test_handle_chain_request(node, blockchain):
    """Test handling a chain request message."""
    node.register_blockchain(blockchain)
    
    # Add some transactions and mine a block
    blockchain.add_transaction({
        'from': 'test1',
        'to': 'test2',
        'amount': 10.0,
        'timestamp': time.time()
    })
    blockchain.mine_pending_transactions('miner1')
    
    # Handle chain request
    message = {
        'type': 'request_chain',
        'data': {
            'node_id': 'peer1'
        }
    }
    node.handle_message(message, "peer1")
    # Note: Actual message sending is mocked in the implementation

def test_handle_chain_response(node, blockchain):
    """Test handling a chain response message."""
    node.register_blockchain(blockchain)
    
    # Create a longer chain
    longer_chain = blockchain.to_dict()
    longer_chain['chain'].append({
        'index': 2,
        'transactions': [],
        'timestamp': time.time(),
        'previous_hash': longer_chain['chain'][1]['hash'],
        'nonce': 0,
        'hash': '0' * 64
    })
    
    # Handle chain response
    message = {
        'type': 'chain_response',
        'data': {
            'chain': longer_chain['chain'],
            'node_id': node.node_id
        }
    }
    node.handle_message(message, "peer1")
    
    # Verify chain was replaced
    assert len(blockchain.chain) == 3

def test_node_serialization(node):
    """Test node serialization and deserialization."""
    # Add some peers
    node.add_peer("peer1")
    node.add_peer("peer2")
    
    # Convert to dictionary
    node_dict = node.to_dict()
    assert node_dict['node_id'] == node.node_id
    assert node_dict['host'] == node.host
    assert node_dict['port'] == node.port
    assert set(node_dict['peers']) == node.peers
    
    # Create new node from dictionary
    new_node = DHTNode.from_dict(node_dict)
    assert new_node.node_id == node.node_id
    assert new_node.host == node.host
    assert new_node.port == node.port
    assert new_node.peers == node.peers 