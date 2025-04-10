from typing import Any, Dict, Optional
from collections import defaultdict

class Memory:
    """
    Memory management system for the VM.
    Handles storage and retrieval of variables and contract state.
    """
    
    def __init__(self):
        """Initialize memory with empty storage."""
        self.storage: Dict[str, Any] = {}
        self.contract_storage: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.temp_storage: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any, contract_address: Optional[str] = None) -> None:
        """
        Store a value in memory.
        
        Args:
            key: Storage key
            value: Value to store
            contract_address: Optional contract address for contract storage
        """
        if contract_address:
            self.contract_storage[contract_address][key] = value
        else:
            self.storage[key] = value
    
    def load(self, key: str, contract_address: Optional[str] = None) -> Any:
        """
        Load a value from memory.
        
        Args:
            key: Storage key
            contract_address: Optional contract address for contract storage
            
        Returns:
            Stored value or None if not found
        """
        if contract_address:
            return self.contract_storage.get(contract_address, {}).get(key)
        return self.storage.get(key)
    
    def store_temp(self, key: str, value: Any) -> None:
        """
        Store a temporary value (cleared between transactions).
        
        Args:
            key: Storage key
            value: Value to store
        """
        self.temp_storage[key] = value
    
    def load_temp(self, key: str) -> Any:
        """
        Load a temporary value.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None if not found
        """
        return self.temp_storage.get(key)
    
    def clear_temp(self) -> None:
        """Clear temporary storage."""
        self.temp_storage.clear()
    
    def get_contract_state(self, contract_address: str) -> Dict[str, Any]:
        """
        Get the complete state of a contract.
        
        Args:
            contract_address: Contract address
            
        Returns:
            Dictionary of contract state
        """
        return self.contract_storage.get(contract_address, {}).copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory state to dictionary format."""
        return {
            'storage': self.storage,
            'contract_storage': dict(self.contract_storage),
            'temp_storage': self.temp_storage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory instance from dictionary format."""
        memory = cls()
        memory.storage = data['storage']
        memory.contract_storage = defaultdict(dict, data['contract_storage'])
        memory.temp_storage = data['temp_storage']
        return memory 