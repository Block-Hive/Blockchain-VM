from flask import Flask, jsonify, request
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import re
import hashlib
import json
from urllib.parse import urlparse

from .blockchain import Blockchain
from .transaction import Transaction
from .network import NetworkManager
from .wallet import Wallet
from .config import Config

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100
request_counts = defaultdict(list)

def rate_limit():
    """Rate limiting decorator."""
    def decorator(f):
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.now()
            
            # Remove old requests
            request_counts[ip] = [t for t in request_counts[ip] 
                                if now - t < timedelta(seconds=RATE_LIMIT_WINDOW)]
            
            # Check rate limit
            if len(request_counts[ip]) >= RATE_LIMIT_MAX_REQUESTS:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            request_counts[ip].append(now)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_amount(amount: float) -> bool:
    """Validate transaction amount."""
    return isinstance(amount, (int, float)) and amount > 0

def validate_address(address: str) -> bool:
    """Validate blockchain address format."""
    # Basic validation - should be a non-empty string
    return isinstance(address, str) and len(address) > 0

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Initialize blockchain components
    blockchain = Blockchain()
    network = NetworkManager(blockchain)
    wallet = Wallet()
    
    # Configure the app
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)
    
    @app.route('/mine', methods=['GET'], endpoint='mine_block')
    @rate_limit()
    def mine():
        """Mine a new block."""
        # Get the last block
        last_block = blockchain.get_last_block()
        
        # Calculate proof of work
        proof = blockchain.proof_of_work(last_block)
        
        # Create new block
        block = blockchain.mine_block()
        
        response = {
            'message': "New Block Forged",
            'index': block.index,
            'transactions': block.transactions,
            'proof': block.proof,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        }
        return jsonify(response), 200

    @app.route('/transactions/new', methods=['POST'], endpoint='create_transaction')
    @rate_limit()
    def new_transaction():
        """Create a new transaction."""
        values = request.get_json()
        
        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400
        
        # Create a new transaction
        transaction = Transaction(
            sender=values['sender'],
            recipient=values['recipient'],
            amount=values['amount']
        )
        
        # Sign the transaction
        transaction.sign(wallet.private_key)
        
        # Add the transaction to the blockchain
        index = blockchain.add_transaction(transaction)
        
        response = {
            'message': f'Transaction will be added to Block {index}',
            'transaction': transaction.to_dict()
        }
        return jsonify(response), 201

    @app.route('/chain', methods=['GET'], endpoint='get_chain')
    @rate_limit()
    def full_chain():
        """Get the full blockchain."""
        response = {
            'chain': [block.to_dict() for block in blockchain.chain],
            'length': len(blockchain.chain)
        }
        return jsonify(response), 200

    @app.route('/nodes', methods=['GET'], endpoint='get_nodes')
    @rate_limit()
    def get_nodes():
        """Get list of active nodes."""
        response = {
            'nodes': list(blockchain.nodes)
        }
        return jsonify(response), 200

    @app.route('/nodes/register', methods=['POST'], endpoint='register_nodes')
    @rate_limit()
    def register_nodes():
        """Register new nodes."""
        values = request.get_json()
        
        nodes = values.get('nodes')
        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400
        
        for node in nodes:
            blockchain.register_node(node)
        
        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes)
        }
        return jsonify(response), 201

    @app.route('/nodes/resolve', methods=['GET'], endpoint='resolve_conflicts')
    @rate_limit()
    def consensus():
        """Resolve conflicts between nodes."""
        replaced = blockchain.resolve_conflicts()
        
        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': [block.to_dict() for block in blockchain.chain]
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': [block.to_dict() for block in blockchain.chain]
            }
        
        return jsonify(response), 200

    @app.route('/balance/<address>', methods=['GET'], endpoint='get_balance')
    @rate_limit()
    def get_balance(address: str):
        """Get balance for an address."""
        balance = blockchain.get_balance(address)
        response = {
            'address': address,
            'balance': balance
        }
        return jsonify(response), 200

    @app.route('/transactions/<transaction_hash>/confirmations', methods=['GET'], endpoint='get_transaction_confirmations')
    @rate_limit()
    def get_confirmations(transaction_hash: str):
        """Get number of confirmations for a transaction."""
        confirmations = blockchain.get_transaction_confirmations(transaction_hash)
        response = {
            'transaction_hash': transaction_hash,
            'confirmations': confirmations,
            'is_confirmed': blockchain.is_transaction_confirmed(transaction_hash)
        }
        return jsonify(response), 200

    @app.route('/difficulty', methods=['GET'], endpoint='get_difficulty')
    @rate_limit()
    def get_difficulty():
        """Get current mining difficulty."""
        response = {
            'difficulty': blockchain.difficulty,
            'target_block_time': blockchain.target_block_time,
            'adjustment_interval': blockchain.difficulty_adjustment_interval
        }
        return jsonify(response), 200

    @app.route('/wallet/address', methods=['GET'], endpoint='get_wallet_address')
    @rate_limit()
    def get_wallet_address():
        """Get the current wallet's address."""
        response = {
            'address': wallet.get_address(),
            'public_key': wallet.get_public_key()
        }
        return jsonify(response), 200

    @app.route('/wallet/balance', methods=['GET'], endpoint='get_wallet_balance')
    @rate_limit()
    def get_wallet_balance():
        """Get the current wallet's balance."""
        balance = wallet.get_balance(blockchain)
        response = {
            'address': wallet.get_address(),
            'balance': balance
        }
        return jsonify(response), 200

    @app.route('/heartbeat', methods=['GET'], endpoint='heartbeat')
    @rate_limit()
    def heartbeat():
        """Heartbeat endpoint for node health check."""
        return jsonify({'status': 'ok'}), 200

    @app.route('/blocks/new', methods=['POST'], endpoint='receive_block')
    @rate_limit()
    def receive_block():
        """Receive a new block from the network."""
        values = request.get_json()
        
        # TODO: Add proper block validation
        # For now, we'll just accept any block
        block = Block.from_dict(values)
        blockchain.chain.append(block)
        
        response = {
            'message': 'Block received',
            'block': block.to_dict()
        }
        return jsonify(response), 201

    return app

# Create the app instance for running directly
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 