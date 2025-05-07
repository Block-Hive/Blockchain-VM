from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class InstructionError(Exception):
    """Base exception for instruction-related errors."""
    pass

class InvalidOperandError(InstructionError):
    """Raised when operand validation fails."""
    pass

class InvalidOpCodeError(InstructionError):
    """Raised when opcode validation fails."""
    pass

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

class Operand(BaseModel):
    """Model for instruction operands with validation."""
    value: Union[int, str, bytes]
    type: str = Field(default="int")  # Type of operand: int, str, bytes
    
    @validator('value')
    def validate_value(cls, v, values):
        if values.get('type') == 'int':
            if not isinstance(v, int):
                try:
                    v = int(v)
                except (ValueError, TypeError):
                    raise ValueError("Invalid integer operand")
            if v.bit_length() > 256:
                raise ValueError("Integer operand too large")
        elif values.get('type') == 'str':
            if not isinstance(v, str):
                v = str(v)
            if len(v.encode()) > 64:
                raise ValueError("String operand too large")
        elif values.get('type') == 'bytes':
            if not isinstance(v, bytes):
                try:
                    v = bytes(v)
                except (ValueError, TypeError):
                    raise ValueError("Invalid bytes operand")
            if len(v) > 64:
                raise ValueError("Bytes operand too large")
        return v

class Instruction(BaseModel):
    """Represents a single VM instruction with validation."""
    opcode: OpCode
    operands: List[Operand] = Field(default_factory=list)
    
    @validator('operands')
    def validate_operands(cls, v, values):
        opcode = values.get('opcode')
        if opcode:
            # Validate operand count based on opcode
            expected_count = {
                OpCode.PUSH: 1,
                OpCode.JUMP: 1,
                OpCode.JUMPI: 2,
                OpCode.CALL: 2,
                OpCode.LOAD: 1,
                OpCode.STORE: 2,
                OpCode.TRANSFER: 2,
                OpCode.CALL_CONTRACT: 2,
            }.get(opcode, 0)
            
            if len(v) != expected_count:
                raise ValueError(f"Invalid number of operands for {opcode.name}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction to dictionary format."""
        return {
            'opcode': self.opcode.name,
            'operands': [{'value': op.value, 'type': op.type} for op in self.operands]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Instruction':
        """Create instruction from dictionary format."""
        try:
            opcode = OpCode[data['opcode']]
            operands = [
                Operand(value=op['value'], type=op.get('type', 'int'))
                for op in data.get('operands', [])
            ]
            return cls(opcode=opcode, operands=operands)
        except KeyError as e:
            logger.error(f"Invalid opcode in instruction data: {e}")
            raise InvalidOpCodeError(f"Invalid opcode: {e}")
        except ValueError as e:
            logger.error(f"Invalid operand in instruction data: {e}")
            raise InvalidOperandError(f"Invalid operand: {e}")
    
    def __str__(self) -> str:
        """String representation of the instruction."""
        return f"{self.opcode.name}({', '.join(str(op.value) for op in self.operands)})" 