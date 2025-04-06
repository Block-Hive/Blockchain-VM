# Blockchain Implementation in Python

A complete blockchain system implemented in Python, featuring core blockchain functionality, secure transactions, peer-to-peer networking, and a RESTful API.

## Features

- Core blockchain functionality (blocks, chain, mining)
- Secure transaction system with digital signatures
- Peer-to-peer networking using DHT
- RESTful API for blockchain operations
- PostgreSQL database for persistent storage
- Wallet management with encrypted private keys
- Configurable mining difficulty
- Transaction pool management
- Comprehensive logging system
- Automatic database initialization
- Environment-based configuration

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Flask
- cryptography
- pycryptodome
- requests
- python-dotenv
- pytest
- psycopg2-binary

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/blockchain.git
cd blockchain
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
```bash
# Install PostgreSQL if not already installed
sudo apt-get install postgresql postgresql-contrib

# Create a database
sudo -u postgres psql
postgres=# CREATE DATABASE blockchain;
postgres=# CREATE USER blockchain_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE blockchain TO blockchain_user;
postgres=# \q
```

5. Configure environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

The `.env` file contains all necessary configuration:
- Database settings (host, port, credentials)
- API settings (host, port, debug mode)
- Blockchain parameters (difficulty, block time, mining reward)
- Network settings (host, port, peer limits)
- Security settings (key size, algorithms)
- Logging settings (level, file)

## Project Structure

```
blockchain/
├── api/
│   └── app.py              # Flask API implementation
├── core/
│   ├── block.py            # Block class implementation
│   ├── blockchain.py       # Blockchain class implementation
│   ├── transaction.py      # Transaction class implementation
│   └── transaction_pool.py # Transaction pool management
├── crypto/
│   └── wallet.py           # Wallet and cryptographic operations
├── network/
│   └── dht_node.py         # DHT node for networking
├── utils/
│   ├── database.py         # PostgreSQL database operations
│   ├── initializer.py      # Project initialization
│   ├── logger.py           # Logging configuration
│   └── storage.py          # Storage management
├── config.py               # Configuration settings
└── __init__.py
```

## Usage

1. Start the node:
```bash
python -m blockchain.api.app
```

The application will automatically:
- Load environment variables
- Initialize the database and create tables
- Set up logging
- Start the API server

2. API Endpoints:

### Blockchain Operations
- `GET /chain` - Get the full blockchain
- `POST /mine` - Mine a new block
- `POST /transactions/new` - Create a new transaction
- `GET /transactions/pending` - Get pending transactions

### Network Operations
- `POST /nodes/register` - Register a new node
- `GET /nodes/resolve` - Resolve conflicts between nodes

### Wallet Operations
- `POST /wallet/new` - Create a new wallet
- `GET /wallet/balance` - Get wallet balance

## Testing

1. Run all tests:
```bash
python -m pytest
```

2. Run specific test file:
```bash
python -m pytest tests/test_blockchain.py
```

3. Run tests with coverage:
```bash
python -m pytest --cov=blockchain tests/
```

4. Example test patterns:
- See `tests/example_test.py` for common test patterns
- Use fixtures for setup and teardown
- Test both success and error cases
- Use meaningful test names and docstrings

## Development

1. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes:
- Follow PEP 8 style guide
- Add docstrings to new functions/classes
- Update tests as needed
- Update documentation

3. Run tests before committing:
```bash
python -m pytest
```

4. Commit your changes:
```bash
git add .
git commit -m "Description of your changes"
```

5. Push to your branch:
```bash
git push origin feature/your-feature-name
```

6. Create a Pull Request

## Security Features

- RSA key pairs for wallets
- Digital signatures for transactions
- Encrypted storage for private keys
- Proof of work for mining
- Input validation
- Rate limiting
- Environment-based configuration
- Secure database connections

## Troubleshooting

1. Database Connection Issues:
- Check PostgreSQL service status
- Verify database credentials in .env
- Ensure database and user exist
- Check network connectivity

2. API Issues:
- Verify API settings in .env
- Check if port is available
- Review logs for errors

3. Mining Issues:
- Check difficulty settings
- Verify wallet balance
- Review transaction pool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Cryptography library for cryptographic operations
- Flask for the REST API
- PostgreSQL for persistent storage
- Python-dotenv for environment management 