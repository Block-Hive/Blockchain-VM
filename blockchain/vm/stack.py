from typing import Any, List, Optional
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class StackError(Exception):
    """Base exception for stack operations."""
    pass

class StackOverflowError(StackError):
    """Raised when stack size exceeds maximum limit."""
    pass

class StackUnderflowError(StackError):
    """Raised when trying to pop from empty stack."""
    pass

class StackAccessError(StackError):
    """Raised when access control check fails."""
    pass

class StackItem(BaseModel):
    """Model for stack items with validation."""
    value: Any
    size: int = Field(default=32, ge=1, le=64)  # Size in bytes, max 64 bytes
    
    @validator('value')
    def validate_value(cls, v):
        if isinstance(v, (int, str)):
            if isinstance(v, int) and v.bit_length() > 256:
                raise ValueError("Integer value too large")
            if isinstance(v, str) and len(v.encode()) > 64:
                raise ValueError("String value too large")
        return v

class Stack:
    """
    Stack implementation for the VM with size limits and access control.
    Handles push, pop, and other stack operations.
    """
    
    MAX_STACK_SIZE = 1024  # Maximum number of items in stack
    
    def __init__(self):
        """Initialize empty stack."""
        self._items: List[StackItem] = []
        self._access_control = True  # Enable access control by default
    
    def _check_size(self) -> None:
        """Check if stack size is within limits."""
        if len(self._items) >= self.MAX_STACK_SIZE:
            logger.error("Stack overflow: maximum size reached")
            raise StackOverflowError(f"Stack size limit exceeded: {self.MAX_STACK_SIZE}")
    
    def _check_access(self) -> None:
        """Check if operation is allowed under current access control."""
        if not self._access_control:
            logger.warning("Access control disabled")
            raise StackAccessError("Operation not allowed under current access control")
    
    def push(self, value: Any) -> None:
        """
        Push a value onto the stack.
        
        Args:
            value: Value to push
            
        Raises:
            StackOverflowError: If stack size limit is reached
            StackAccessError: If access control check fails
            ValueError: If value validation fails
        """
        self._check_access()
        self._check_size()
        try:
            item = StackItem(value=value)
            self._items.append(item)
        except ValueError as e:
            logger.error(f"Invalid value pushed to stack: {e}")
            raise
    
    def pop(self) -> Any:
        """
        Pop a value from the stack.
        
        Returns:
            Popped value
            
        Raises:
            StackUnderflowError: If stack is empty
            StackAccessError: If access control check fails
        """
        self._check_access()
        if not self._items:
            logger.error("Stack underflow: attempted to pop from empty stack")
            raise StackUnderflowError("Stack is empty")
        return self._items.pop().value
    
    def peek(self) -> Optional[Any]:
        """
        Peek at the top value without removing it.
        
        Returns:
            Top value or None if stack is empty
            
        Raises:
            StackAccessError: If access control check fails
        """
        self._check_access()
        return self._items[-1].value if self._items else None
    
    def dup(self) -> None:
        """
        Duplicate the top value.
        
        Raises:
            StackUnderflowError: If stack is empty
            StackOverflowError: If stack size limit is reached
            StackAccessError: If access control check fails
        """
        self._check_access()
        if not self._items:
            logger.error("Stack underflow: attempted to duplicate from empty stack")
            raise StackUnderflowError("Stack is empty")
        self._check_size()
        self._items.append(self._items[-1])
    
    def swap(self) -> None:
        """
        Swap the top two values.
        
        Raises:
            StackUnderflowError: If stack has fewer than 2 items
            StackAccessError: If access control check fails
        """
        self._check_access()
        if len(self._items) < 2:
            logger.error("Stack underflow: attempted to swap with fewer than 2 items")
            raise StackUnderflowError("Stack has fewer than 2 items")
        self._items[-1], self._items[-2] = self._items[-2], self._items[-1]
    
    def clear(self) -> None:
        """
        Clear the stack.
        
        Raises:
            StackAccessError: If access control check fails
        """
        self._check_access()
        self._items.clear()
    
    def size(self) -> int:
        """
        Get the current size of the stack.
        
        Returns:
            Number of items in the stack
        """
        return len(self._items)
    
    def is_empty(self) -> bool:
        """
        Check if the stack is empty.
        
        Returns:
            True if stack is empty, False otherwise
        """
        return len(self._items) == 0
    
    def to_list(self) -> List[Any]:
        """
        Get a copy of the stack contents.
        
        Returns:
            List of stack items
            
        Raises:
            StackAccessError: If access control check fails
        """
        self._check_access()
        return [item.value for item in self._items.copy()]
    
    def __str__(self) -> str:
        """String representation of the stack."""
        return f"Stack({[item.value for item in self._items]})" 