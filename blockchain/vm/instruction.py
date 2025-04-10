from enum import Enum, auto
from typing import Any, Dict, List, Optional

class OpCode(Enum):
    """Operation codes for the VM instruction set."""
    # Stack operations
    PUSH = auto()        # Push value onto stack
    POP = auto()         # Pop value from stack
    DUP = auto()         # Duplicate top stack value
    SWAP = auto()        # Swap top two stack values
    
    # Arithmetic operations
    ADD = auto()         # Add top two stack values
    SUB = auto()         # Subtract top two stack values
    MUL = auto()         # Multiply top two stack values
    DIV = auto()         # Divide top two stack values
    MOD = auto()         # Modulo of top two stack values
    
    # Comparison operations
    EQ = auto()          # Equal comparison
    LT = auto()          # Less than comparison
    GT = auto()          # Greater than comparison
    LTE = auto()         # Less than or equal comparison
    GTE = auto()         # Greater than or equal comparison
    
    # Control flow
    JUMP = auto()        # Unconditional jump
    JUMPI = auto()       # Conditional jump
    CALL = auto()        # Call function
    RETURN = auto()      # Return from function
    
    # Memory operations
    LOAD = auto()        # Load from memory
    STORE = auto()       # Store to memory
    
    # Blockchain operations
    BALANCE = auto()     # Get account balance
    TRANSFER = auto()    # Transfer tokens
    CONTRACT = auto()    # Deploy contract
    CALL_CONTRACT = auto()  # Call contract method
    
    # System operations
    HALT = auto()        # Stop execution
    LOG = auto()         # Log message
    REVERT = auto()      # Revert execution

class Instruction:
    """Represents a single VM instruction."""
    
    def __init__(self, opcode: OpCode, operands: Optional[List[Any]] = None):
        self.opcode = opcode
        self.operands = operands or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction to dictionary format."""
        return {
            'opcode': self.opcode.name,
            'operands': self.operands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Instruction':
        """Create instruction from dictionary format."""
        return cls(
            opcode=OpCode[data['opcode']],
            operands=data['operands']
        )
    
    def __str__(self) -> str:
        """String representation of the instruction."""
        return f"{self.opcode.name}({', '.join(str(op) for op in self.operands)})" 