from typing import Any, Dict, List, Optional
from .instruction import Instruction, OpCode

class Contract:
    """
    Represents a smart contract in the blockchain.
    """
    
    def __init__(self, address: str, code: List[Instruction], owner: str):
        """
        Initialize a new contract.
        
        Args:
            address: Contract address
            code: Contract bytecode
            owner: Contract owner's address
        """
        self.address = address
        self.code = code
        self.owner = owner
        self.state: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary format."""
        return {
            'address': self.address,
            'code': [inst.to_dict() for inst in self.code],
            'owner': self.owner,
            'state': self.state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create contract from dictionary format."""
        contract = cls(
            address=data['address'],
            code=[Instruction.from_dict(inst) for inst in data['code']],
            owner=data['owner']
        )
        contract.state = data['state']
        return contract

class ContractManager:
    """
    Manages smart contracts in the blockchain.
    """
    
    def __init__(self):
        """Initialize contract manager."""
        self.contracts: Dict[str, Contract] = {}
    
    def deploy_contract(self, address: str, code: List[Instruction], owner: str) -> Contract:
        """
        Deploy a new contract.
        
        Args:
            address: Contract address
            code: Contract bytecode
            owner: Contract owner's address
            
        Returns:
            Deployed contract
        """
        contract = Contract(address, code, owner)
        self.contracts[address] = contract
        return contract
    
    def get_contract(self, address: str) -> Optional[Contract]:
        """
        Get a contract by address.
        
        Args:
            address: Contract address
            
        Returns:
            Contract if found, None otherwise
        """
        return self.contracts.get(address)
    
    def update_contract_state(self, address: str, state: Dict[str, Any]) -> None:
        """
        Update a contract's state.
        
        Args:
            address: Contract address
            state: New state
        """
        if contract := self.contracts.get(address):
            contract.state.update(state)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract manager to dictionary format."""
        return {
            'contracts': {
                addr: contract.to_dict()
                for addr, contract in self.contracts.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContractManager':
        """Create contract manager from dictionary format."""
        manager = cls()
        manager.contracts = {
            addr: Contract.from_dict(contract_data)
            for addr, contract_data in data['contracts'].items()
        }
        return manager 