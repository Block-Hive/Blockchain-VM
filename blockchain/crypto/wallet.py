from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import json
import hashlib
from typing import Dict, Any

class Wallet:
    """Handles cryptographic operations including key generation, signing, and verification."""
    
    def __init__(self, password: str = None):
        """Initialize a new wallet."""
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        self.address = self.generate_address()
    
    def get_address(self) -> str:
        """Get the wallet's public address."""
        return self.address
    
    def generate_address(self) -> str:
        """Generate a unique address for the wallet."""
        public_key_bytes = self.public_key.export_key()
        return hashlib.sha256(public_key_bytes).hexdigest()
    
    def sign_transaction(self, transaction: Dict[str, Any]) -> str:
        """Sign a transaction with the private key."""
        # Create a string representation of the transaction
        transaction_str = json.dumps(transaction, sort_keys=True)
        
        # Create a hash of the transaction
        transaction_hash = SHA256.new(transaction_str.encode())
        
        # Sign the hash
        signature = pkcs1_15.new(self.private_key).sign(transaction_hash)
        return signature.hex()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert wallet to dictionary."""
        return {
            'address': self.address,
            'public_key': self.public_key.export_key().decode(),
            'private_key': self.private_key.export_key().decode()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Wallet':
        """Create a wallet from dictionary data."""
        wallet = cls()
        wallet.address = data['address']
        wallet.public_key = RSA.import_key(data['public_key'])
        wallet.private_key = RSA.import_key(data['private_key'])
        return wallet 