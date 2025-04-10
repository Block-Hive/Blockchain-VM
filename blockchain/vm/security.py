from typing import Any, Dict, List, Optional
from .instruction import Instruction, OpCode

class SecurityManager:
    """
    Manages security features for the VM.
    """
    
    def __init__(self):
        """Initialize security manager."""
        self.max_stack_size = 1024
        self.max_memory_size = 1024 * 1024  # 1MB
        self.max_contract_size = 1024 * 1024  # 1MB
        self.max_gas_per_instruction = 1000
        self.blacklisted_instructions: List[OpCode] = []
    
    def validate_instruction(self, instruction: Instruction) -> bool:
        """
        Validate an instruction for security.
        
        Args:
            instruction: Instruction to validate
            
        Returns:
            True if instruction is valid, False otherwise
        """
        # Check if instruction is blacklisted
        if instruction.opcode in self.blacklisted_instructions:
            return False
        
        # Check operands
        if not self._validate_operands(instruction):
            return False
        
        return True
    
    def _validate_operands(self, instruction: Instruction) -> bool:
        """
        Validate instruction operands.
        
        Args:
            instruction: Instruction to validate
            
        Returns:
            True if operands are valid, False otherwise
        """
        # Validate based on opcode
        if instruction.opcode == OpCode.PUSH:
            return self._validate_push_operands(instruction.operands)
        elif instruction.opcode == OpCode.JUMP:
            return self._validate_jump_operands(instruction.operands)
        elif instruction.opcode == OpCode.CALL:
            return self._validate_call_operands(instruction.operands)
        
        return True
    
    def _validate_push_operands(self, operands: List[Any]) -> bool:
        """
        Validate PUSH instruction operands.
        
        Args:
            operands: Operands to validate
            
        Returns:
            True if operands are valid, False otherwise
        """
        if not operands:
            return False
        
        # Check operand type
        value = operands[0]
        if not isinstance(value, (int, float, str, bool)):
            return False
        
        return True
    
    def _validate_jump_operands(self, operands: List[Any]) -> bool:
        """
        Validate JUMP instruction operands.
        
        Args:
            operands: Operands to validate
            
        Returns:
            True if operands are valid, False otherwise
        """
        if not operands:
            return False
        
        # Check operand type
        target = operands[0]
        if not isinstance(target, int):
            return False
        
        # Check if target is non-negative
        if target < 0:
            return False
        
        return True
    
    def _validate_call_operands(self, operands: List[Any]) -> bool:
        """
        Validate CALL instruction operands.
        
        Args:
            operands: Operands to validate
            
        Returns:
            True if operands are valid, False otherwise
        """
        if not operands:
            return False
        
        # Check operand type
        target = operands[0]
        if not isinstance(target, int):
            return False
        
        # Check if target is non-negative
        if target < 0:
            return False
        
        return True
    
    def validate_stack_size(self, size: int) -> bool:
        """
        Validate stack size.
        
        Args:
            size: Stack size to validate
            
        Returns:
            True if size is valid, False otherwise
        """
        return size <= self.max_stack_size
    
    def validate_memory_size(self, size: int) -> bool:
        """
        Validate memory size.
        
        Args:
            size: Memory size to validate
            
        Returns:
            True if size is valid, False otherwise
        """
        return size <= self.max_memory_size
    
    def validate_contract_size(self, size: int) -> bool:
        """
        Validate contract size.
        
        Args:
            size: Contract size to validate
            
        Returns:
            True if size is valid, False otherwise
        """
        return size <= self.max_contract_size
    
    def validate_gas_usage(self, gas_used: int) -> bool:
        """
        Validate gas usage.
        
        Args:
            gas_used: Gas used to validate
            
        Returns:
            True if gas usage is valid, False otherwise
        """
        return gas_used <= self.max_gas_per_instruction
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert security manager to dictionary format."""
        return {
            'max_stack_size': self.max_stack_size,
            'max_memory_size': self.max_memory_size,
            'max_contract_size': self.max_contract_size,
            'max_gas_per_instruction': self.max_gas_per_instruction,
            'blacklisted_instructions': [op.name for op in self.blacklisted_instructions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityManager':
        """Create security manager from dictionary format."""
        manager = cls()
        manager.max_stack_size = data['max_stack_size']
        manager.max_memory_size = data['max_memory_size']
        manager.max_contract_size = data['max_contract_size']
        manager.max_gas_per_instruction = data['max_gas_per_instruction']
        manager.blacklisted_instructions = [
            OpCode[op_name] for op_name in data['blacklisted_instructions']
        ]
        return manager 