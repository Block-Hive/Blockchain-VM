from typing import List, Dict, Any
from .transaction import Transaction
from ..config import MAX_TRANSACTION_POOL_SIZE

class TransactionPool:
    """Manages a pool of pending transactions."""
    
    def __init__(self, max_size: int = MAX_TRANSACTION_POOL_SIZE):
        """Initialize an empty transaction pool."""
        self.transactions: List[Transaction] = []
        self.max_size = max_size
    
    def add_transaction(self, transaction: Dict[str, Any] | Transaction) -> bool:
        """
        Add a transaction to the pool.
        
        Args:
            transaction: Transaction to add (can be dict or Transaction object)
            
        Returns:
            True if transaction was added, False otherwise
        """
        if len(self.transactions) >= self.max_size:
            return False
        
        # Convert dict to Transaction if needed
        if isinstance(transaction, dict):
            transaction = Transaction.from_dict(transaction)
        
        if transaction.verify():
            self.transactions.append(transaction)
            return True
        return False
    
    def get_transactions(self) -> List[Transaction]:
        """Get all transactions in the pool."""
        return self.transactions
    
    def remove_transactions(self, transactions: List[Transaction]) -> None:
        """Remove transactions from the pool."""
        self.transactions = [tx for tx in self.transactions if tx not in transactions]
    
    def clear_transactions(self) -> None:
        """Clear all transactions from the pool."""
        self.transactions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction pool to dictionary."""
        return {
            'transactions': [tx.to_dict() for tx in self.transactions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionPool':
        """Create a transaction pool from dictionary data."""
        pool = cls()
        pool.transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        return pool 