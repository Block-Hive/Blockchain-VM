import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'blockchain')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Blockchain configuration
    DIFFICULTY = int(os.getenv('DIFFICULTY', '4'))
    BLOCK_REWARD = float(os.getenv('BLOCK_REWARD', '10.0'))
    TRANSACTION_FEE = float(os.getenv('TRANSACTION_FEE', '0.1'))
    MAX_BLOCK_SIZE = int(os.getenv('MAX_BLOCK_SIZE', '1000'))
    CONFIRMATION_BLOCKS = int(os.getenv('CONFIRMATION_BLOCKS', '6'))
    TARGET_BLOCK_TIME = int(os.getenv('TARGET_BLOCK_TIME', '10'))
    DIFFICULTY_ADJUSTMENT_INTERVAL = int(os.getenv('DIFFICULTY_ADJUSTMENT_INTERVAL', '2016'))
    
    # Network configuration
    HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', '30'))
    NODE_TIMEOUT = int(os.getenv('NODE_TIMEOUT', '90'))
    DISCOVERY_INTERVAL = int(os.getenv('DISCOVERY_INTERVAL', '300'))
    
    # API configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', '100'))
    
    # Wallet configuration
    WALLET_FILE = os.getenv('WALLET_FILE', 'wallet.json')
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }
    
    @classmethod
    def get_blockchain_config(cls) -> Dict[str, Any]:
        """Get blockchain configuration."""
        return {
            'difficulty': cls.DIFFICULTY,
            'block_reward': cls.BLOCK_REWARD,
            'transaction_fee': cls.TRANSACTION_FEE,
            'max_block_size': cls.MAX_BLOCK_SIZE,
            'confirmation_blocks': cls.CONFIRMATION_BLOCKS,
            'target_block_time': cls.TARGET_BLOCK_TIME,
            'difficulty_adjustment_interval': cls.DIFFICULTY_ADJUSTMENT_INTERVAL
        }
    
    @classmethod
    def get_network_config(cls) -> Dict[str, Any]:
        """Get network configuration."""
        return {
            'heartbeat_interval': cls.HEARTBEAT_INTERVAL,
            'node_timeout': cls.NODE_TIMEOUT,
            'discovery_interval': cls.DISCOVERY_INTERVAL
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            'host': cls.API_HOST,
            'port': cls.API_PORT,
            'rate_limit_window': cls.RATE_LIMIT_WINDOW,
            'rate_limit_max_requests': cls.RATE_LIMIT_MAX_REQUESTS
        } 