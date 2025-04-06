import os
import logging
from dotenv import load_dotenv
from .database import Database
from .logger import setup_logger

logger = setup_logger(__name__)

class Initializer:
    """Handles project initialization and setup."""
    
    @staticmethod
    def initialize():
        """
        Initialize the blockchain project:
        1. Load environment variables
        2. Set up logging
        3. Initialize database and create tables
        """
        try:
            # Load environment variables
            load_dotenv()
            logger.info("Environment variables loaded successfully")
            
            # Initialize database and create tables
            Database.initialize()
            Database.create_tables()
            logger.info("Database initialized and tables created successfully")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize project: {e}")
            return False
    
    @staticmethod
    def check_environment():
        """
        Check if all required environment variables are set.
        Returns a list of missing variables.
        """
        required_vars = [
            'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
            'API_HOST', 'API_PORT', 'API_DEBUG',
            'INITIAL_DIFFICULTY', 'TARGET_BLOCK_TIME', 'MINING_REWARD',
            'DEFAULT_HOST', 'DEFAULT_PORT', 'MAX_PEERS',
            'KEY_SIZE', 'HASH_ALGORITHM', 'SIGNATURE_ALGORITHM',
            'LOG_LEVEL', 'LOG_FILE'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        return missing_vars 