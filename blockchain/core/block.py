import hashlib
import json
import time
from typing import List, Dict, Any
from .transaction import Transaction

class Block:
    """
    Represents a single block in the blockchain.
    Each block contains a list of transactions, timestamp, previous block's hash,
    and a proof of work (nonce).
    """
    
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, timestamp: float = None):
        """
        Initialize a new block.
        
        Args:
            index: The block's position in the blockchain
            transactions: List of transactions to be included in the block
            previous_hash: Hash of the previous block in the chain
            timestamp: Block creation timestamp (defaults to current time)
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block using SHA-256.
        The hash includes all block data except the current hash.
        
        Returns:
            str: The calculated hash of the block
        """
        block_string = json.dumps({
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """
        Mine the block by finding a nonce that produces a hash with the required
        number of leading zeros (difficulty).
        
        Args:
            difficulty: Number of leading zeros required in the hash
        """
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def is_valid(self, difficulty: int) -> bool:
        """
        Verify if the block's hash meets the difficulty requirement.
        
        Args:
            difficulty: Number of leading zeros required in the hash
            
        Returns:
            bool: True if the block is valid, False otherwise
        """
        return (
            self.hash[:difficulty] == '0' * difficulty and
            self.hash == self.calculate_hash()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the block to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the block
        """
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from a dictionary.
        
        Args:
            data: Dictionary containing block data
            
        Returns:
            Block: New Block instance
        """
        block = cls(
            index=data['index'],
            transactions=[Transaction.from_dict(tx) for tx in data['transactions']],
            previous_hash=data['previous_hash'],
            timestamp=data['timestamp']
        )
        block.nonce = data['nonce']
        block.hash = data['hash']
        return block 