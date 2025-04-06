import os
import json
import logging
from typing import Dict, Any, List, Optional
from .database import Database
from ..config import DATA_DIR, BLOCKCHAIN_FILE, WALLET_FILE, PEERS_FILE

logger = logging.getLogger(__name__)

class Storage:
    """
    Storage utility for managing blockchain data persistence.
    Uses PostgreSQL database for storage.
    """
    
    @staticmethod
    def initialize():
        """Initialize storage and create necessary database tables."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Initialize database and create tables
            Database.initialize()
            Database.create_tables()
            
            logger.info("Storage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            raise
    
    @staticmethod
    def save_blockchain(blockchain_data: Dict[str, Any]) -> bool:
        """
        Save blockchain data to the database.
        
        Args:
            blockchain_data: Blockchain data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Save each block to the database
            for block in blockchain_data.get('chain', []):
                if not Database.save_block(block):
                    return False
            
            logger.info("Blockchain saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save blockchain: {e}")
            return False
    
    @staticmethod
    def load_blockchain() -> Optional[Dict[str, Any]]:
        """
        Load blockchain data from the database.
        
        Returns:
            Optional[Dict[str, Any]]: Blockchain data if found, None otherwise
        """
        try:
            blocks = Database.get_blocks()
            if not blocks:
                return None
            
            return {'chain': blocks}
        except Exception as e:
            logger.error(f"Failed to load blockchain: {e}")
            return None
    
    @staticmethod
    def save_wallet(wallet_data: Dict[str, Any]) -> bool:
        """
        Save wallet data to the database.
        
        Args:
            wallet_data: Wallet data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return Database.save_wallet(wallet_data)
        except Exception as e:
            logger.error(f"Failed to save wallet: {e}")
            return False
    
    @staticmethod
    def load_wallet(address: str) -> Optional[Dict[str, Any]]:
        """
        Load wallet data from the database.
        
        Args:
            address: Wallet address to load
            
        Returns:
            Optional[Dict[str, Any]]: Wallet data if found, None otherwise
        """
        try:
            return Database.get_wallet(address)
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            return None
    
    @staticmethod
    def save_peers(peers_data: List[Dict[str, Any]]) -> bool:
        """
        Save peers data to the database.
        
        Args:
            peers_data: List of peer data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for peer in peers_data:
                if not Database.save_peer(peer):
                    return False
            
            logger.info("Peers saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save peers: {e}")
            return False
    
    @staticmethod
    def load_peers() -> List[Dict[str, Any]]:
        """
        Load peers data from the database.
        
        Returns:
            List[Dict[str, Any]]: List of peer data
        """
        try:
            return Database.get_peers()
        except Exception as e:
            logger.error(f"Failed to load peers: {e}")
            return []
    
    @staticmethod
    def clear_data() -> bool:
        """
        Clear all stored data from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return Database.clear_data()
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")
            return False 