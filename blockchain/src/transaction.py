from typing import Dict, Any
import json
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float):
        """
        Initialize a new transaction.
        
        Args:
            sender: Public key of the sender
            recipient: Public key of the recipient
            amount: Amount to transfer
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the transaction
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

    def calculate_hash(self) -> str:
        """
        Calculate the hash of the transaction.
        
        Returns:
            str: Hash of the transaction
        """
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign(self, private_key: RSA.RsaKey) -> None:
        """
        Sign the transaction using the sender's private key.
        
        Args:
            private_key: RSA private key of the sender
        """
        transaction_hash = SHA256.new(json.dumps(self.to_dict(), sort_keys=True).encode())
        self.signature = pkcs1_15.new(private_key).sign(transaction_hash)

    def verify_signature(self, public_key: RSA.RsaKey) -> bool:
        """
        Verify the transaction signature using the sender's public key.
        
        Args:
            public_key: RSA public key of the sender
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not self.signature:
            return False
        
        try:
            transaction_hash = SHA256.new(json.dumps(self.to_dict(), sort_keys=True).encode())
            pkcs1_15.new(public_key).verify(transaction_hash, self.signature)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def generate_key_pair() -> tuple[RSA.RsaKey, RSA.RsaKey]:
        """
        Generate a new RSA key pair.
        
        Returns:
            tuple[RSA.RsaKey, RSA.RsaKey]: (private_key, public_key)
        """
        private_key = RSA.generate(2048)
        public_key = private_key.publickey()
        return private_key, public_key 