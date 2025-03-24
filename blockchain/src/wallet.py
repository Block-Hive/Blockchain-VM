import json
import os
import hashlib
import base64
from typing import Dict, Any, Optional
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base58

from .transaction import Transaction
from .blockchain import Blockchain

class Wallet:
    def __init__(self, wallet_file: str = "wallet.json"):
        """Initialize a new wallet."""
        self.wallet_file = wallet_file
        self.private_key = None
        self.public_key = None
        self.address = None
        self._load_or_create_wallet()

    def _load_or_create_wallet(self) -> None:
        """Load existing wallet or create a new one."""
        try:
            self._load_wallet()
        except FileNotFoundError:
            self._create_wallet()

    def _create_wallet(self) -> None:
        """Create a new wallet with a key pair."""
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        self.address = self._generate_address()
        self._save_wallet()

    def _load_wallet(self) -> None:
        """Load wallet from file."""
        with open(self.wallet_file, 'rb') as f:
            wallet_data = json.load(f)
            self.private_key = RSA.import_key(wallet_data['private_key'])
            self.public_key = self.private_key.publickey()
            self.address = wallet_data['address']

    def _save_wallet(self) -> None:
        """Save wallet to file."""
        wallet_data = {
            'private_key': self.private_key.export_key().decode(),
            'address': self.address
        }
        with open(self.wallet_file, 'w') as f:
            json.dump(wallet_data, f)

    def save_wallet(self) -> None:
        """Public method to save wallet."""
        self._save_wallet()

    def _generate_address(self) -> str:
        """Generate a unique address for the wallet."""
        public_key_bytes = self.public_key.export_key(format='DER')
        return base58.b58encode(hashlib.sha256(public_key_bytes).digest()).decode()[:40]

    def sign_transaction(self, transaction: Dict[str, Any]) -> str:
        """Sign a transaction with the wallet's private key."""
        transaction_str = json.dumps(transaction, sort_keys=True)
        h = SHA256.new(transaction_str.encode())
        signature = pkcs1_15.new(self.private_key).sign(h)
        return base64.b64encode(signature).decode()

    def verify_signature(self, transaction: Dict[str, Any], signature: str) -> bool:
        """Verify a transaction signature."""
        try:
            transaction_str = json.dumps(transaction, sort_keys=True)
            h = SHA256.new(transaction_str.encode())
            pkcs1_15.new(self.public_key).verify(h, base64.b64decode(signature))
            return True
        except:
            return False

    def get_address(self) -> str:
        """Get the wallet's address."""
        return self.address

    def get_public_key(self) -> str:
        """Get the wallet's public key in PEM format."""
        return self.public_key.export_key().decode()

    def get_balance(self, blockchain: Blockchain) -> float:
        """Get the wallet's current balance."""
        balance = 0.0
        
        # Check all blocks in the chain
        for block in blockchain.chain:
            for transaction in block.transactions:
                if transaction['recipient'] == self.address:
                    balance += transaction['amount']
                if transaction['sender'] == self.address:
                    balance -= transaction['amount']
        
        return balance

    def create_transaction(self, recipient: str, amount: float, blockchain: Blockchain) -> Dict[str, Any]:
        """Create a new transaction."""
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        # Check if we have enough balance
        balance = self.get_balance(blockchain)
        if balance < amount:
            raise ValueError("Insufficient funds")
        
        # Create transaction
        transaction = {
            'sender': self.address,
            'recipient': recipient,
            'amount': amount,
            'timestamp': blockchain.get_current_timestamp()
        }
        
        # Sign transaction
        transaction['signature'] = self.sign_transaction(transaction)
        
        return transaction

    def cleanup(self):
        """Clean up wallet resources."""
        self.save_wallet() 