from typing import List
from ..instruction import Instruction, OpCode

def create_simple_token_contract(owner_address: str) -> List[Instruction]:
    """
    Create a simple token contract.
    
    This contract implements basic token functionality:
    - Total supply: 1,000,000 tokens
    - Transfer tokens between addresses
    - Check balances
    
    Args:
        owner_address: Address of the contract owner
        
    Returns:
        List of instructions representing the contract
    """
    instructions = [
        # Initialize total supply
        Instruction(OpCode.PUSH, [1000000]),
        Instruction(OpCode.STORE, ["total_supply"]),
        
        # Initialize owner balance
        Instruction(OpCode.PUSH, [owner_address]),
        Instruction(OpCode.PUSH, [1000000]),
        Instruction(OpCode.STORE, ["balance"]),
        
        # Transfer function
        Instruction(OpCode.PUSH, ["transfer"]),
        Instruction(OpCode.PUSH, [2]),  # Number of parameters
        Instruction(OpCode.STORE, ["function"]),
        
        # Check sender balance
        Instruction(OpCode.LOAD, ["balance"]),
        Instruction(OpCode.PUSH, [0]),  # Amount to transfer
        Instruction(OpCode.LT),
        Instruction(OpCode.JUMPI, [20]),  # Jump to end if insufficient balance
        
        # Update balances
        Instruction(OpCode.LOAD, ["balance"]),
        Instruction(OpCode.PUSH, [0]),  # Amount to transfer
        Instruction(OpCode.SUB),
        Instruction(OpCode.STORE, ["balance"]),
        
        Instruction(OpCode.PUSH, [1]),  # Recipient address
        Instruction(OpCode.LOAD, ["balance"]),
        Instruction(OpCode.PUSH, [0]),  # Amount to transfer
        Instruction(OpCode.ADD),
        Instruction(OpCode.STORE, ["balance"]),
        
        # Return success
        Instruction(OpCode.PUSH, [True]),
        Instruction(OpCode.RETURN),
        
        # Return failure
        Instruction(OpCode.PUSH, [False]),
        Instruction(OpCode.RETURN),
        
        # Balance function
        Instruction(OpCode.PUSH, ["balance"]),
        Instruction(OpCode.PUSH, [1]),  # Number of parameters
        Instruction(OpCode.STORE, ["function"]),
        
        Instruction(OpCode.PUSH, [0]),  # Address to check
        Instruction(OpCode.LOAD, ["balance"]),
        Instruction(OpCode.RETURN),
    ]
    
    return instructions

def main():
    """Example usage of the simple token contract."""
    from ..vm import VM
    from ..contract import ContractManager
    
    # Create VM and contract manager
    vm = VM()
    contract_manager = ContractManager()
    
    # Create contract
    owner_address = "0x1234"
    contract_code = create_simple_token_contract(owner_address)
    contract = contract_manager.deploy_contract(
        address="0x5678",
        code=contract_code,
        owner=owner_address
    )
    
    # Load contract into VM
    vm.load_program(contract.code)
    
    # Run contract
    success = vm.run()
    if success:
        print("Contract executed successfully")
    else:
        print("Contract execution failed")
    
    # Print contract state
    print("Contract state:", contract.state)

if __name__ == "__main__":
    main() 