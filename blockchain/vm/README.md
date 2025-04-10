# Shield Coin Virtual Machine

A virtual machine implementation for the Shield Coin blockchain that enables smart contract execution.

## Features

- Register-based VM architecture
- Smart contract execution environment
- Secure sandbox for contract execution
- State management for blockchain data
- Gas metering system
- Security features and access controls
- Debugging and monitoring tools

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shield-coin.git
cd shield-coin
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install development dependencies (optional):
```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

```python
from blockchain.vm import VM
from blockchain.vm.instruction import Instruction, OpCode

# Create VM instance
vm = VM()

# Create some instructions
instructions = [
    Instruction(OpCode.PUSH, [42]),
    Instruction(OpCode.PUSH, [58]),
    Instruction(OpCode.ADD),
    Instruction(OpCode.HALT)
]

# Load and run program
vm.load_program(instructions)
success = vm.run()

# Check result
if success:
    result = vm.stack.pop()
    print(f"Result: {result}")  # Should print 100
```

### Smart Contracts

```python
from blockchain.vm import VM
from blockchain.vm.contract import ContractManager
from blockchain.vm.examples.simple_token import create_simple_token_contract

# Create VM and contract manager
vm = VM()
contract_manager = ContractManager()

# Create and deploy contract
owner_address = "0x1234"
contract_code = create_simple_token_contract(owner_address)
contract = contract_manager.deploy_contract(
    address="0x5678",
    code=contract_code,
    owner=owner_address
)

# Execute contract
vm.load_program(contract.code)
success = vm.run()
```

## Architecture

The VM consists of several components:

1. **Instruction Set**: Defines the operations that can be performed
2. **Memory Management**: Handles storage and retrieval of variables
3. **Stack**: Manages the execution stack
4. **Contract Manager**: Handles smart contract deployment and execution
5. **Security Manager**: Implements security features and access controls

## Security Features

- Stack size limits
- Memory size limits
- Contract size limits
- Gas usage limits
- Instruction blacklisting
- Operand validation
- Secure sandbox execution

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

The project follows PEP 8 style guidelines. Use `black` for formatting:

```bash
black blockchain/
```

### Type Checking

Use `mypy` for type checking:

```bash
mypy blockchain/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 