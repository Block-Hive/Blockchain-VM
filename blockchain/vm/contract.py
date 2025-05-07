from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
import logging
from .instruction import Instruction, OpCode, InvalidOperandError, InvalidOpCodeError

logger = logging.getLogger(__name__)

class ContractError(Exception):
    """Base exception for contract-related errors."""
    pass

class ContractNotFoundError(ContractError):
    """Raised when a contract is not found."""
    pass

class ContractAccessError(ContractError):
    """Raised when access to a contract is denied."""
    pass

class InvalidContractError(ContractError):
    """Raised when contract validation fails."""
    pass

class ContractState(BaseModel):
    """Model for contract state with validation."""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('data')
    def validate_data(cls, v):
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError("State keys must be strings")
            if isinstance(value, (int, str, bytes)):
                if isinstance(value, int) and value.bit_length() > 256:
                    raise ValueError("Integer state value too large")
                if isinstance(value, (str, bytes)) and len(str(value).encode()) > 64:
                    raise ValueError("String/bytes state value too large")
        return v

class Contract(BaseModel):
    """
    Represents a smart contract in the blockchain with validation.
    """
    address: str
    code: List[Instruction]
    owner: str
    state: ContractState = Field(default_factory=ContractState)
    
    @validator('address')
    def validate_address(cls, v):
        if not isinstance(v, str) or len(v) != 42 or not v.startswith('0x'):
            raise ValueError("Invalid contract address format")
        return v
    
    @validator('owner')
    def validate_owner(cls, v):
        if not isinstance(v, str) or len(v) != 42 or not v.startswith('0x'):
            raise ValueError("Invalid owner address format")
        return v
    
    @validator('code')
    def validate_code(cls, v):
        if not v:
            raise ValueError("Contract code cannot be empty")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary format."""
        return {
            'address': self.address,
            'code': [inst.to_dict() for inst in self.code],
            'owner': self.owner,
            'state': self.state.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create contract from dictionary format."""
        try:
            return cls(
                address=data['address'],
                code=[Instruction.from_dict(inst) for inst in data['code']],
                owner=data['owner'],
                state=ContractState(data=data.get('state', {}))
            )
        except (KeyError, ValueError, InvalidOperandError, InvalidOpCodeError) as e:
            logger.error(f"Error creating contract from dict: {e}")
            raise InvalidContractError(f"Invalid contract data: {e}")

class ContractManager:
    """
    Manages smart contracts in the blockchain with access control.
    """
    
    def __init__(self):
        """Initialize contract manager."""
        self.contracts: Dict[str, Contract] = {}
        self._access_control = True
    
    def deploy_contract(self, address: str, code: List[Instruction], owner: str) -> Contract:
        """
        Deploy a new contract.
        
        Args:
            address: Contract address
            code: Contract bytecode
            owner: Contract owner's address
            
        Returns:
            Deployed contract
            
        Raises:
            InvalidContractError: If contract validation fails
            ContractError: If contract already exists
        """
        try:
            if address in self.contracts:
                raise ContractError(f"Contract already exists at address {address}")
            
            contract = Contract(address=address, code=code, owner=owner)
            self.contracts[address] = contract
            logger.info(f"Contract deployed at {address}")
            return contract
        except ValueError as e:
            logger.error(f"Error deploying contract: {e}")
            raise InvalidContractError(f"Invalid contract data: {e}")
    
    def get_contract(self, address: str) -> Contract:
        """
        Get a contract by address.
        
        Args:
            address: Contract address
            
        Returns:
            Contract if found
            
        Raises:
            ContractNotFoundError: If contract not found
            ContractAccessError: If access control check fails
        """
        if not self._access_control:
            logger.warning("Access control disabled")
            raise ContractAccessError("Operation not allowed under current access control")
        
        if address not in self.contracts:
            logger.error(f"Contract not found at address {address}")
            raise ContractNotFoundError(f"Contract not found at address {address}")
        
        return self.contracts[address]
    
    def update_contract_state(self, address: str, state: Dict[str, Any], caller: str) -> None:
        """
        Update a contract's state.
        
        Args:
            address: Contract address
            state: New state
            caller: Address of the caller
            
        Raises:
            ContractNotFoundError: If contract not found
            ContractAccessError: If caller is not the owner
            InvalidContractError: If state validation fails
        """
        contract = self.get_contract(address)
        
        if caller != contract.owner:
            logger.error(f"Unauthorized state update attempt by {caller}")
            raise ContractAccessError("Only contract owner can update state")
        
        try:
            contract.state = ContractState(data=state)
            logger.info(f"Contract state updated at {address}")
        except ValueError as e:
            logger.error(f"Error updating contract state: {e}")
            raise InvalidContractError(f"Invalid state data: {e}")
    
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
        try:
            manager.contracts = {
                addr: Contract.from_dict(contract_data)
                for addr, contract_data in data['contracts'].items()
            }
            return manager
        except (KeyError, ValueError, InvalidContractError) as e:
            logger.error(f"Error creating contract manager from dict: {e}")
            raise InvalidContractError(f"Invalid contract manager data: {e}") 