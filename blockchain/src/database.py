import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from .config import Config

class DatabaseManager:
    def __init__(self):
        """Initialize database manager."""
        self.config = Config.get_db_config()
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables if they don't exist."""
        # First connect to default postgres database to create our database if it doesn't exist
        conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            database='postgres',
            user=self.config['user'],
            password=self.config['password']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config['database']}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {self.config['database']}")
        
        cur.close()
        conn.close()
        
        # Now connect to our database and create tables
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create blocks table
                cur.execute('''CREATE TABLE IF NOT EXISTS blocks
                            (index INTEGER PRIMARY KEY,
                             timestamp REAL,
                             previous_hash TEXT,
                             proof INTEGER,
                             hash TEXT)''')
                
                # Create transactions table
                cur.execute('''CREATE TABLE IF NOT EXISTS transactions
                            (id SERIAL PRIMARY KEY,
                             block_index INTEGER,
                             sender TEXT,
                             recipient TEXT,
                             amount REAL,
                             signature TEXT,
                             FOREIGN KEY (block_index) REFERENCES blocks(index))''')
                
                # Create nodes table
                cur.execute('''CREATE TABLE IF NOT EXISTS nodes
                            (address TEXT PRIMARY KEY)''')
                
                # Create transaction confirmations table
                cur.execute('''CREATE TABLE IF NOT EXISTS transaction_confirmations
                            (transaction_hash TEXT PRIMARY KEY,
                             block_index INTEGER,
                             confirmations INTEGER,
                             FOREIGN KEY (block_index) REFERENCES blocks(index))''')
                
                # Create difficulty history table
                cur.execute('''CREATE TABLE IF NOT EXISTS difficulty_history
                            (block_index INTEGER PRIMARY KEY,
                             difficulty INTEGER,
                             actual_time REAL,
                             FOREIGN KEY (block_index) REFERENCES blocks(index))''')
                
                conn.commit()

    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        conn = psycopg2.connect(**self.config)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def execute_command(self, query: str, params: tuple = None) -> None:
        """
        Execute a command without returning results.
        
        Args:
            query: SQL command to execute
            params: Command parameters
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()

    def get_block(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a block by index.
        
        Args:
            index: Block index
            
        Returns:
            Optional[Dict[str, Any]]: Block data if found, None otherwise
        """
        results = self.execute_query(
            'SELECT * FROM blocks WHERE index = %s',
            (index,)
        )
        
        if not results:
            return None
            
        block_data = results[0]
        
        # Get transactions for this block
        transactions = self.execute_query(
            'SELECT sender, recipient, amount, signature FROM transactions WHERE block_index = %s',
            (index,)
        )
        
        # Convert transactions to the expected format
        formatted_transactions = [
            {
                'sender': tx['sender'],
                'recipient': tx['recipient'],
                'amount': tx['amount'],
                'signature': tx['signature']
            }
            for tx in transactions
        ]
        
        return {
            'index': block_data['index'],
            'timestamp': block_data['timestamp'],
            'previous_hash': block_data['previous_hash'],
            'proof': block_data['proof'],
            'hash': block_data['hash'],
            'transactions': formatted_transactions
        }

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        """
        Get all blocks.
        
        Returns:
            List[Dict[str, Any]]: List of blocks
        """
        blocks = self.execute_query('SELECT * FROM blocks ORDER BY index')
        return [self.get_block(block['index']) for block in blocks]

    def get_block_transactions(self, block_index: int) -> List[Dict[str, Any]]:
        """
        Get all transactions for a block.
        
        Args:
            block_index: Block index
            
        Returns:
            List[Dict[str, Any]]: List of transactions
        """
        return self.execute_query(
            'SELECT * FROM transactions WHERE block_index = %s',
            (block_index,)
        )

    def get_transaction_confirmations(self, transaction_hash: str) -> Optional[int]:
        """
        Get confirmations for a transaction.
        
        Args:
            transaction_hash: Transaction hash
            
        Returns:
            Optional[int]: Number of confirmations if found, None otherwise
        """
        results = self.execute_query(
            'SELECT confirmations FROM transaction_confirmations WHERE transaction_hash = %s',
            (transaction_hash,)
        )
        return results[0]['confirmations'] if results else None

    def get_active_nodes(self) -> List[str]:
        """
        Get all active nodes.
        
        Returns:
            List[str]: List of node addresses
        """
        results = self.execute_query('SELECT address FROM nodes')
        return [row['address'] for row in results]

    def save_block(self, block: Dict[str, Any]) -> None:
        """
        Save a block to the database.
        
        Args:
            block: Block data to save
        """
        self.execute_command(
            '''INSERT INTO blocks (index, timestamp, previous_hash, proof, hash)
               VALUES (%s, %s, %s, %s, %s)''',
            (block['index'], block['timestamp'], block['previous_hash'],
             block['proof'], block['hash'])
        )

    def save_transaction(self, transaction: Dict[str, Any], block_index: int) -> None:
        """
        Save a transaction to the database.
        
        Args:
            transaction: Transaction data to save
            block_index: Index of the block containing this transaction
        """
        self.execute_command(
            '''INSERT INTO transactions (block_index, sender, recipient, amount, signature)
               VALUES (%s, %s, %s, %s, %s)''',
            (block_index, transaction['sender'], transaction['recipient'],
             transaction['amount'], transaction['signature'])
        )

    def save_transaction_confirmation(self, transaction_hash: str, block_index: int,
                                   confirmations: int) -> None:
        """
        Save transaction confirmation data.
        
        Args:
            transaction_hash: Transaction hash
            block_index: Block index
            confirmations: Number of confirmations
        """
        self.execute_command(
            '''INSERT INTO transaction_confirmations (transaction_hash, block_index, confirmations)
               VALUES (%s, %s, %s)''',
            (transaction_hash, block_index, confirmations)
        )

    def save_difficulty(self, block_index: int, difficulty: int, actual_time: float) -> None:
        """
        Save difficulty data.
        
        Args:
            block_index: Block index
            difficulty: Current difficulty
            actual_time: Actual block time
        """
        self.execute_command(
            '''INSERT INTO difficulty_history (block_index, difficulty, actual_time)
               VALUES (%s, %s, %s)''',
            (block_index, difficulty, actual_time)
        )

    def save_node(self, address: str) -> None:
        """
        Save a node address.
        
        Args:
            address: Node address to save
        """
        self.execute_command(
            'INSERT INTO nodes (address) VALUES (%s) ON CONFLICT (address) DO NOTHING',
            (address,)
        )

    def clear_database(self) -> None:
        """Clear all data from the database."""
        tables = ['transaction_confirmations', 'difficulty_history', 'transactions', 'blocks', 'nodes']
        for table in tables:
            self.execute_command(f'TRUNCATE TABLE {table} CASCADE')

    def get_latest_difficulty(self) -> Optional[int]:
        """Get the latest difficulty value from the difficulty history."""
        try:
            self.execute_query('''
                SELECT difficulty 
                FROM difficulty_history 
                ORDER BY block_index DESC 
                LIMIT 1
            ''')
            result = self.fetch_one()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting latest difficulty: {e}")
            return None 