# Python Blockchain Implementation

A robust and efficient implementation of a blockchain system in Python, featuring proof-of-work consensus, transaction management, and network synchronization.

## Features

- **Proof of Work Consensus**: Implements a secure mining mechanism with dynamic difficulty adjustment
- **Transaction Management**: Handles transactions with digital signatures and fee system
- **Network Synchronization**: Supports multiple nodes with chain validation and conflict resolution
- **Database Persistence**: SQLite-based storage for blocks, transactions, and network state
- **Parallel Mining**: Optimized mining process using multiprocessing
- **RESTful API**: Flask-based API for blockchain interaction
- **Wallet Management**: Secure wallet creation and transaction signing
- **Transaction Confirmation**: Configurable confirmation blocks for transaction finality

## Requirements

- Python 3.8+
- SQLite3
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-blockchain.git
cd python-blockchain
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Blockchain Node

```bash
python -m blockchain.src.api
```

The API server will start on `http://localhost:5000`

### API Endpoints

- `GET /chain`: Get the full blockchain
- `POST /transactions/new`: Create a new transaction
- `GET /mine`: Mine a new block
- `POST /nodes/register`: Register a new node
- `GET /nodes/resolve`: Resolve conflicts between nodes
- `GET /wallet/address`: Get wallet address
- `GET /wallet/balance`: Get wallet balance
- `GET /difficulty`: Get current mining difficulty
- `GET /transaction/confirmations/<tx_hash>`: Get transaction confirmations

### Running Tests

```bash
./run_tests.sh
```

## Project Structure

```
python-blockchain/
├── blockchain/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── block.py
│   │   ├── blockchain.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── network.py
│   │   ├── transaction.py
│   │   └── wallet.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api.py
│       ├── test_block.py
│       ├── test_blockchain.py
│       ├── test_database.py
│       ├── test_network.py
│       ├── test_transaction.py
│       └── test_wallet.py
├── migrations/
├── requirements.txt
├── setup.py
├── run_tests.sh
├── README.md
└── LICENSE
```

## Configuration

The blockchain can be configured through environment variables or by modifying `config.py`:

- `BLOCK_REWARD`: Reward for mining a block
- `TRANSACTION_FEE`: Fee per transaction
- `MAX_BLOCK_SIZE`: Maximum transactions per block
- `DIFFICULTY_ADJUSTMENT_INTERVAL`: Blocks between difficulty adjustments
- `TARGET_BLOCK_TIME`: Target time between blocks in seconds
- `CONFIRMATION_BLOCKS`: Number of blocks needed for transaction confirmation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Bitcoin's blockchain implementation
- Built with Python and Flask
- Uses SQLite for data persistence
- Implements proof-of-work consensus mechanism 