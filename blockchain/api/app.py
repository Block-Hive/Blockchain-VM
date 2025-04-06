from flask import Flask, request, jsonify
from ..core.blockchain import Blockchain
from ..core.transaction import Transaction
from ..core.transaction_pool import TransactionPool
from ..crypto.wallet import Wallet
from ..config import API_CONFIG

app = Flask(__name__)
blockchain = Blockchain()
transaction_pool = TransactionPool()

@app.route('/chain', methods=['GET'])
def get_chain():
    """Get the full blockchain."""
    return jsonify(blockchain.to_dict()), 200

@app.route('/transactions/pending', methods=['GET'])
def get_pending_transactions():
    """Get pending transactions."""
    return jsonify({
        'pending_transactions': [tx.to_dict() for tx in transaction_pool.get_transactions()]
    }), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Create a new transaction."""
    data = request.get_json()
    
    # Check required fields
    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create transaction
    transaction = Transaction(
        sender=data['sender'],
        recipient=data['recipient'],
        amount=data['amount']
    )
    transaction.signature = data['signature']
    
    # Add transaction to pool
    if blockchain.add_transaction(transaction):
        return jsonify({'message': 'Transaction added to pool'}), 201
    else:
        return jsonify({'error': 'Invalid transaction'}), 400

@app.route('/mine', methods=['GET'])
def mine():
    """Mine a new block with pending transactions."""
    # Get miner's address from query parameter
    miner_address = request.args.get('address')
    if not miner_address:
        return jsonify({'error': 'Miner address required'}), 400
    
    # Mine new block
    block = blockchain.mine_pending_transactions(miner_address)
    if block:
        return jsonify({
            'message': 'New block mined',
            'block': block.to_dict()
        }), 201
    else:
        return jsonify({'error': 'Mining failed'}), 400

@app.route('/nodes/register', methods=['POST'])
def register_node():
    """Register a new node."""
    data = request.get_json()
    
    if not data or 'node_id' not in data:
        return jsonify({'error': 'Node ID required'}), 400
    
    # Add node to network (implementation depends on network layer)
    return jsonify({'message': 'Node registered'}), 201

@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    """Resolve blockchain conflicts."""
    # Implement chain resolution (implementation depends on network layer)
    return jsonify({
        'message': 'Chain resolved',
        'chain_length': len(blockchain.chain)
    }), 200

@app.route('/wallet/new', methods=['GET'])
def create_wallet():
    """Create a new wallet."""
    wallet = Wallet()
    return jsonify(wallet.to_dict()), 200

@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    """Get balance for a wallet address."""
    address = request.args.get('address')
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    balance = 0.0
    
    # Calculate balance from blockchain
    for block in blockchain.chain:
        for transaction in block.transactions:
            if transaction.sender == address:
                balance -= transaction.amount
            if transaction.recipient == address:
                balance += transaction.amount
    
    # Add pending transactions
    for transaction in transaction_pool.get_transactions():
        if transaction.sender == address:
            balance -= transaction.amount
        if transaction.recipient == address:
            balance += transaction.amount
    
    return jsonify({'balance': balance}), 200

if __name__ == '__main__':
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    ) 