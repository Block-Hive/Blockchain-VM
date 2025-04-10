from typing import Any, List, Optional

class Stack:
    """
    Stack implementation for the VM.
    Handles push, pop, and other stack operations.
    """
    
    def __init__(self):
        """Initialize empty stack."""
        self._items: List[Any] = []
    
    def push(self, value: Any) -> None:
        """
        Push a value onto the stack.
        
        Args:
            value: Value to push
        """
        self._items.append(value)
    
    def pop(self) -> Any:
        """
        Pop a value from the stack.
        
        Returns:
            Popped value
            
        Raises:
            IndexError: If stack is empty
        """
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> Optional[Any]:
        """
        Peek at the top value without removing it.
        
        Returns:
            Top value or None if stack is empty
        """
        return self._items[-1] if self._items else None
    
    def dup(self) -> None:
        """
        Duplicate the top value.
        
        Raises:
            IndexError: If stack is empty
        """
        if not self._items:
            raise IndexError("Stack is empty")
        self._items.append(self._items[-1])
    
    def swap(self) -> None:
        """
        Swap the top two values.
        
        Raises:
            IndexError: If stack has fewer than 2 items
        """
        if len(self._items) < 2:
            raise IndexError("Stack has fewer than 2 items")
        self._items[-1], self._items[-2] = self._items[-2], self._items[-1]
    
    def clear(self) -> None:
        """Clear the stack."""
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
        """
        return self._items.copy()
    
    def __str__(self) -> str:
        """String representation of the stack."""
        return f"Stack({self._items})" 