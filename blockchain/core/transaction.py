import time
from typing import Dict, Any, Optional
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import json

class Transaction:
    """
    Represents a single transaction in the blockchain.
    Handles transaction creation, validation, and signing.
    """
    
    def __init__(self, sender: str, recipient: str, amount: float, timestamp: Optional[float] = None):
        """
        Initialize a new transaction.
        
        Args:
            sender: Sender's public address
            recipient: Recipient's public address
            amount: Amount to transfer
            timestamp: Optional timestamp (defaults to current time)
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.signature = None
    
    def sign(self, private_key: RSA.RsaKey) -> None:
        """
        Sign the transaction with a private key.
        
        Args:
            private_key: Private key to sign with
        """
        # Create a hash of the transaction data
        transaction_hash = SHA256.new(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        )
        
        # Sign the hash with the private key
        self.signature = pkcs1_15.new(private_key).sign(transaction_hash).hex()
    
    def verify(self) -> bool:
        """
        Verify the transaction signature.
        
        Returns:
            True if signature is valid, False otherwise
        """
        # System transactions (mining rewards) are always valid
        if self.sender == "system":
            return True
        
        # If no signature, transaction is invalid
        if not self.signature:
            return False
        
        try:
            # Create a hash of the transaction data
            transaction_hash = SHA256.new(
                json.dumps(self.to_dict(), sort_keys=True).encode()
            )
            
            # Import the public key from the sender's address
            public_key = RSA.import_key(self.sender)
            
            # Verify the signature
            pkcs1_15.new(public_key).verify(
                transaction_hash,
                bytes.fromhex(self.signature)
            )
            return True
        except (ValueError, TypeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the transaction
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Create a Transaction instance from a dictionary.
        
        Args:
            data: Dictionary containing transaction data
            
        Returns:
            Transaction: New Transaction instance
        """
        # Handle both field naming conventions
        sender = data.get('sender') or data.get('from')
        recipient = data.get('recipient') or data.get('to')
        
        if not sender or not recipient:
            raise ValueError("Transaction must have sender and recipient")
        
        transaction = cls(
            sender=sender,
            recipient=recipient,
            amount=data['amount'],
            timestamp=data.get('timestamp')
        )
        if 'signature' in data:
            transaction.signature = data['signature']
        return transaction
    
    def __str__(self) -> str:
        """Return a string representation of the transaction."""
        return (
            f"Transaction(sender={self.sender}, recipient={self.recipient}, "
            f"amount={self.amount}, timestamp={self.timestamp})"
        ) 