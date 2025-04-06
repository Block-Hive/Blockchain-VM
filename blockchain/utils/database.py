import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import pool
import json
from typing import Dict, Any, List, Optional
import logging
from ..config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class Database:
    """
    Database utility class for PostgreSQL operations.
    Handles connection pooling, queries, and data persistence.
    """
    
    _connection_pool = None
    
    @classmethod
    def initialize(cls):
        """Initialize the database connection pool."""
        try:
            cls._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password']
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        if cls._connection_pool is None:
            cls.initialize()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool."""
        if cls._connection_pool is not None and conn is not None:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    def create_tables(cls):
        """Create necessary database tables if they don't exist."""
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                # Create blocks table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS blocks (
                        id SERIAL PRIMARY KEY,
                        index INTEGER NOT NULL,
                        timestamp DOUBLE PRECISION NOT NULL,
                        previous_hash VARCHAR(64) NOT NULL,
                        hash VARCHAR(64) NOT NULL UNIQUE,
                        nonce INTEGER NOT NULL,
                        data JSONB NOT NULL
                    )
                """)
                
                # Create transactions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        block_id INTEGER REFERENCES blocks(id),
                        sender VARCHAR(255) NOT NULL,
                        recipient VARCHAR(255) NOT NULL,
                        amount DOUBLE PRECISION NOT NULL,
                        timestamp DOUBLE PRECISION NOT NULL,
                        signature TEXT,
                        is_pending BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create wallets table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS wallets (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255) NOT NULL UNIQUE,
                        public_key TEXT NOT NULL,
                        encrypted_private_key TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create peers table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS peers (
                        id SERIAL PRIMARY KEY,
                        node_id VARCHAR(255) NOT NULL UNIQUE,
                        host VARCHAR(255) NOT NULL,
                        port INTEGER NOT NULL,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to create database tables: {e}")
            raise
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def save_block(cls, block_data: Dict[str, Any]) -> bool:
        """
        Save a block to the database.
        
        Args:
            block_data: Block data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO blocks (index, timestamp, previous_hash, hash, nonce, data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    block_data['index'],
                    block_data['timestamp'],
                    block_data['previous_hash'],
                    block_data['hash'],
                    block_data['nonce'],
                    json.dumps(block_data)
                ))
                block_id = cur.fetchone()[0]
                
                # Save transactions
                for tx in block_data.get('transactions', []):
                    cur.execute("""
                        INSERT INTO transactions 
                        (block_id, sender, recipient, amount, timestamp, signature, is_pending)
                        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                    """, (
                        block_id,
                        tx['sender'],
                        tx['recipient'],
                        tx['amount'],
                        tx['timestamp'],
                        tx.get('signature')
                    ))
                
                conn.commit()
                logger.info(f"Block {block_data['index']} saved successfully")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to save block: {e}")
            return False
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def get_blocks(cls) -> List[Dict[str, Any]]:
        """
        Get all blocks from the database.
        
        Returns:
            List[Dict[str, Any]]: List of blocks
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT data FROM blocks ORDER BY index")
                blocks = [row['data'] for row in cur.fetchall()]
                return blocks
        except Exception as e:
            logger.error(f"Failed to get blocks: {e}")
            return []
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def save_transaction(cls, transaction: Dict[str, Any]) -> bool:
        """
        Save a pending transaction to the database.
        
        Args:
            transaction: Transaction data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO transactions 
                    (sender, recipient, amount, timestamp, signature, is_pending)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (
                    transaction['sender'],
                    transaction['recipient'],
                    transaction['amount'],
                    transaction['timestamp'],
                    transaction.get('signature')
                ))
                conn.commit()
                logger.info("Transaction saved successfully")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to save transaction: {e}")
            return False
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def get_pending_transactions(cls) -> List[Dict[str, Any]]:
        """
        Get all pending transactions from the database.
        
        Returns:
            List[Dict[str, Any]]: List of pending transactions
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT sender, recipient, amount, timestamp, signature
                    FROM transactions
                    WHERE is_pending = TRUE
                """)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get pending transactions: {e}")
            return []
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def save_wallet(cls, wallet_data: Dict[str, Any]) -> bool:
        """
        Save a wallet to the database.
        
        Args:
            wallet_data: Wallet data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO wallets (address, public_key, encrypted_private_key)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (address) DO UPDATE
                    SET public_key = EXCLUDED.public_key,
                        encrypted_private_key = EXCLUDED.encrypted_private_key
                """, (
                    wallet_data['address'],
                    wallet_data['public_key'],
                    wallet_data.get('encrypted_private_key')
                ))
                conn.commit()
                logger.info(f"Wallet {wallet_data['address']} saved successfully")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to save wallet: {e}")
            return False
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def get_wallet(cls, address: str) -> Optional[Dict[str, Any]]:
        """
        Get a wallet from the database by address.
        
        Args:
            address: Wallet address to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Wallet data if found, None otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT address, public_key, encrypted_private_key
                    FROM wallets
                    WHERE address = %s
                """, (address,))
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get wallet: {e}")
            return None
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def save_peer(cls, peer_data: Dict[str, Any]) -> bool:
        """
        Save a peer to the database.
        
        Args:
            peer_data: Peer data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO peers (node_id, host, port)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (node_id) DO UPDATE
                    SET host = EXCLUDED.host,
                        port = EXCLUDED.port,
                        last_seen = CURRENT_TIMESTAMP
                """, (
                    peer_data['node_id'],
                    peer_data['host'],
                    peer_data['port']
                ))
                conn.commit()
                logger.info(f"Peer {peer_data['node_id']} saved successfully")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to save peer: {e}")
            return False
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def get_peers(cls) -> List[Dict[str, Any]]:
        """
        Get all peers from the database.
        
        Returns:
            List[Dict[str, Any]]: List of peers
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT node_id, host, port
                    FROM peers
                    WHERE last_seen > CURRENT_TIMESTAMP - INTERVAL '1 hour'
                """)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get peers: {e}")
            return []
        finally:
            if conn:
                cls.return_connection(conn)
    
    @classmethod
    def clear_data(cls) -> bool:
        """
        Clear all data from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = cls.get_connection()
            with conn.cursor() as cur:
                cur.execute("TRUNCATE blocks, transactions, wallets, peers CASCADE")
                conn.commit()
                logger.info("Database cleared successfully")
                return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to clear database: {e}")
            return False
        finally:
            if conn:
                cls.return_connection(conn) 