import hashlib
import json
from time import time
from typing import List, Dict, Any


class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], timestamp: float,
                 previous_hash: str, proof: int = 0):
        """
        Initialize a new block in the blockchain.
        
        Args:
            index: Index of the block in the chain
            transactions: List of transactions in the block
            timestamp: Time when the block was created
            previous_hash: Hash of the previous block
            proof: Proof of work number
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.proof = proof
        self._hash = None  # Initialize hash as None

    @property
    def hash(self) -> str:
        """Get the block's hash, calculating it if necessary."""
        if self._hash is None:
            self._hash = self.calculate_hash()
        return self._hash

    @hash.setter
    def hash(self, value: str) -> None:
        """Set the block's hash value."""
        self._hash = value

    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block using SHA-256.
        
        Returns:
            str: Hash of the block
        """
        # Create a temporary dict without the hash field
        block_dict = {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'proof': self.proof
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the block to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the block
        """
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'proof': self.proof,
            'hash': self.hash  # This will trigger hash calculation if needed
        }

    @staticmethod
    def from_dict(block_dict: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from a dictionary.
        
        Args:
            block_dict: Dictionary containing block data
            
        Returns:
            Block: New Block instance
        """
        block = Block(
            index=block_dict['index'],
            transactions=block_dict['transactions'],
            timestamp=block_dict['timestamp'],
            previous_hash=block_dict['previous_hash'],
            proof=block_dict['proof']
        )
        if 'hash' in block_dict:
            block.hash = block_dict['hash']  # Use the setter
        return block 