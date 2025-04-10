from typing import Any, Dict, List, Optional, Callable
from .instruction import Instruction, OpCode
from .memory import Memory
from .stack import Stack

class VM:
    """
    Virtual Machine for executing smart contracts and blockchain operations.
    """
    
    def __init__(self):
        """Initialize VM components."""
        self.memory = Memory()
        self.stack = Stack()
        self.pc = 0  # Program counter
        self.running = False
        self.instructions: List[Instruction] = []
        self.gas_limit = 1000000
        self.gas_used = 0
        
        # Register instruction handlers
        self.handlers: Dict[OpCode, Callable] = {
            # Stack operations
            OpCode.PUSH: self._handle_push,
            OpCode.POP: self._handle_pop,
            OpCode.DUP: self._handle_dup,
            OpCode.SWAP: self._handle_swap,
            
            # Arithmetic operations
            OpCode.ADD: self._handle_add,
            OpCode.SUB: self._handle_sub,
            OpCode.MUL: self._handle_mul,
            OpCode.DIV: self._handle_div,
            OpCode.MOD: self._handle_mod,
            
            # Comparison operations
            OpCode.EQ: self._handle_eq,
            OpCode.LT: self._handle_lt,
            OpCode.GT: self._handle_gt,
            OpCode.LTE: self._handle_lte,
            OpCode.GTE: self._handle_gte,
            
            # Control flow
            OpCode.JUMP: self._handle_jump,
            OpCode.JUMPI: self._handle_jumpi,
            OpCode.CALL: self._handle_call,
            OpCode.RETURN: self._handle_return,
            
            # Memory operations
            OpCode.LOAD: self._handle_load,
            OpCode.STORE: self._handle_store,
            
            # Blockchain operations
            OpCode.BALANCE: self._handle_balance,
            OpCode.TRANSFER: self._handle_transfer,
            OpCode.CONTRACT: self._handle_contract,
            OpCode.CALL_CONTRACT: self._handle_call_contract,
            
            # System operations
            OpCode.HALT: self._handle_halt,
            OpCode.LOG: self._handle_log,
            OpCode.REVERT: self._handle_revert,
        }
    
    def load_program(self, instructions: List[Instruction]) -> None:
        """
        Load a program into the VM.
        
        Args:
            instructions: List of instructions to execute
        """
        self.instructions = instructions
        self.pc = 0
        self.running = False
        self.gas_used = 0
        self.stack.clear()
        self.memory.clear_temp()
    
    def run(self) -> bool:
        """
        Run the loaded program.
        
        Returns:
            True if execution completed successfully, False otherwise
        """
        if not self.instructions:
            return False
        
        self.running = True
        while self.running and self.pc < len(self.instructions):
            if self.gas_used >= self.gas_limit:
                self._handle_revert()
                return False
            
            instruction = self.instructions[self.pc]
            handler = self.handlers.get(instruction.opcode)
            
            if not handler:
                raise ValueError(f"Unknown opcode: {instruction.opcode}")
            
            try:
                handler(instruction.operands)
                self.pc += 1
            except Exception as e:
                print(f"Error executing instruction: {e}")
                self._handle_revert()
                return False
        
        return True
    
    # Instruction handlers
    def _handle_push(self, operands: List[Any]) -> None:
        """Handle PUSH instruction."""
        self.stack.push(operands[0])
        self.gas_used += 1
    
    def _handle_pop(self, operands: List[Any]) -> None:
        """Handle POP instruction."""
        self.stack.pop()
        self.gas_used += 1
    
    def _handle_dup(self, operands: List[Any]) -> None:
        """Handle DUP instruction."""
        self.stack.dup()
        self.gas_used += 1
    
    def _handle_swap(self, operands: List[Any]) -> None:
        """Handle SWAP instruction."""
        self.stack.swap()
        self.gas_used += 1
    
    def _handle_add(self, operands: List[Any]) -> None:
        """Handle ADD instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a + b)
        self.gas_used += 1
    
    def _handle_sub(self, operands: List[Any]) -> None:
        """Handle SUB instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a - b)
        self.gas_used += 1
    
    def _handle_mul(self, operands: List[Any]) -> None:
        """Handle MUL instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a * b)
        self.gas_used += 1
    
    def _handle_div(self, operands: List[Any]) -> None:
        """Handle DIV instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        if b == 0:
            raise ValueError("Division by zero")
        self.stack.push(a // b)
        self.gas_used += 1
    
    def _handle_mod(self, operands: List[Any]) -> None:
        """Handle MOD instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        if b == 0:
            raise ValueError("Modulo by zero")
        self.stack.push(a % b)
        self.gas_used += 1
    
    def _handle_eq(self, operands: List[Any]) -> None:
        """Handle EQ instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a == b)
        self.gas_used += 1
    
    def _handle_lt(self, operands: List[Any]) -> None:
        """Handle LT instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a < b)
        self.gas_used += 1
    
    def _handle_gt(self, operands: List[Any]) -> None:
        """Handle GT instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a > b)
        self.gas_used += 1
    
    def _handle_lte(self, operands: List[Any]) -> None:
        """Handle LTE instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a <= b)
        self.gas_used += 1
    
    def _handle_gte(self, operands: List[Any]) -> None:
        """Handle GTE instruction."""
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.push(a >= b)
        self.gas_used += 1
    
    def _handle_jump(self, operands: List[Any]) -> None:
        """Handle JUMP instruction."""
        self.pc = operands[0]
        self.gas_used += 1
    
    def _handle_jumpi(self, operands: List[Any]) -> None:
        """Handle JUMPI instruction."""
        condition = self.stack.pop()
        if condition:
            self.pc = operands[0]
        self.gas_used += 1
    
    def _handle_call(self, operands: List[Any]) -> None:
        """Handle CALL instruction."""
        # Save return address
        self.stack.push(self.pc + 1)
        # Jump to function
        self.pc = operands[0]
        self.gas_used += 1
    
    def _handle_return(self, operands: List[Any]) -> None:
        """Handle RETURN instruction."""
        self.pc = self.stack.pop()
        self.gas_used += 1
    
    def _handle_load(self, operands: List[Any]) -> None:
        """Handle LOAD instruction."""
        key = operands[0]
        value = self.memory.load(key)
        self.stack.push(value)
        self.gas_used += 1
    
    def _handle_store(self, operands: List[Any]) -> None:
        """Handle STORE instruction."""
        key = operands[0]
        value = self.stack.pop()
        self.memory.store(key, value)
        self.gas_used += 1
    
    def _handle_balance(self, operands: List[Any]) -> None:
        """Handle BALANCE instruction."""
        address = operands[0]
        # TODO: Implement balance check against blockchain
        self.stack.push(0)
        self.gas_used += 1
    
    def _handle_transfer(self, operands: List[Any]) -> None:
        """Handle TRANSFER instruction."""
        amount = self.stack.pop()
        to_address = operands[0]
        # TODO: Implement transfer against blockchain
        self.gas_used += 1
    
    def _handle_contract(self, operands: List[Any]) -> None:
        """Handle CONTRACT instruction."""
        # TODO: Implement contract deployment
        self.gas_used += 1
    
    def _handle_call_contract(self, operands: List[Any]) -> None:
        """Handle CALL_CONTRACT instruction."""
        # TODO: Implement contract method call
        self.gas_used += 1
    
    def _handle_halt(self, operands: List[Any]) -> None:
        """Handle HALT instruction."""
        self.running = False
        self.gas_used += 1
    
    def _handle_log(self, operands: List[Any]) -> None:
        """Handle LOG instruction."""
        message = operands[0]
        print(f"VM Log: {message}")
        self.gas_used += 1
    
    def _handle_revert(self, operands: List[Any] = None) -> None:
        """Handle REVERT instruction."""
        self.running = False
        self.stack.clear()
        self.memory.clear_temp()
        self.gas_used += 1 