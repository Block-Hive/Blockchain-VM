import json
import time
from typing import Dict, Any, List, Optional, Set
from ..core.block import Block
from ..core.transaction import Transaction

class DHTNode:
    """
    Distributed Hash Table node for blockchain networking.
    Handles peer discovery, block/transaction propagation, and chain synchronization.
    """
    
    def __init__(self, node_id: str, host: str, port: int):
        """
        Initialize a new DHT node.
        
        Args:
            node_id: Unique identifier for this node
            host: Host address to bind to
            port: Port to listen on
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Set[str] = set()  # Set of peer node IDs
        self.blockchain = None  # Will be set by the blockchain instance
        self.transaction_pool = None  # Will be set by the transaction pool instance
    
    def register_blockchain(self, blockchain: Any) -> None:
        """
        Register the blockchain instance with this node.
        
        Args:
            blockchain: The blockchain instance
        """
        self.blockchain = blockchain
    
    def register_transaction_pool(self, transaction_pool: Any) -> None:
        """
        Register the transaction pool instance with this node.
        
        Args:
            transaction_pool: The transaction pool instance
        """
        self.transaction_pool = transaction_pool
    
    def add_peer(self, peer_id: str) -> None:
        """
        Add a new peer to the network.
        
        Args:
            peer_id: ID of the peer to add
        """
        self.peers.add(peer_id)
    
    def remove_peer(self, peer_id: str) -> None:
        """
        Remove a peer from the network.
        
        Args:
            peer_id: ID of the peer to remove
        """
        self.peers.discard(peer_id)
    
    def broadcast_block(self, block: Block) -> None:
        """
        Broadcast a new block to all peers.
        
        Args:
            block: The block to broadcast
        """
        message = {
            'type': 'new_block',
            'data': block.to_dict()
        }
        self._broadcast_message(message)
    
    def broadcast_transaction(self, transaction: Transaction) -> None:
        """
        Broadcast a new transaction to all peers.
        
        Args:
            transaction: The transaction to broadcast
        """
        message = {
            'type': 'new_transaction',
            'data': {
                'transaction': transaction.to_dict(),
                'signature': transaction.signature
            }
        }
        self._broadcast_message(message)
    
    def request_chain(self, peer_id: str) -> None:
        """
        Request the blockchain from a specific peer.
        
        Args:
            peer_id: ID of the peer to request from
        """
        message = {
            'type': 'request_chain',
            'data': {
                'node_id': self.node_id
            }
        }
        self._send_message(peer_id, message)
    
    def handle_message(self, message: Dict[str, Any], sender_id: str) -> None:
        """
        Handle incoming messages from peers.
        
        Args:
            message: The received message
            sender_id: ID of the sending peer
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type == 'new_block':
            self._handle_new_block(data)
        elif message_type == 'new_transaction':
            self._handle_new_transaction(data)
        elif message_type == 'request_chain':
            self._handle_chain_request(data, sender_id)
        elif message_type == 'chain_response':
            self._handle_chain_response(data)
    
    def _handle_new_block(self, data: Dict[str, Any]) -> None:
        """
        Handle a new block received from a peer.
        
        Args:
            data: Block data
        """
        if not self.blockchain:
            return
        
        block = Block.from_dict(data)
        
        # Validate and add the block
        if self.blockchain.add_block(block):
            # Remove transactions from pool
            if self.transaction_pool:
                self.transaction_pool.remove_transactions(block.transactions)
    
    def _handle_new_transaction(self, data: Dict[str, Any]) -> None:
        """
        Handle a new transaction received from a peer.
        
        Args:
            data: Transaction data
        """
        if not self.transaction_pool:
            return
        
        transaction = Transaction.from_dict(
            data['transaction'],
            signature=data['signature']
        )
        
        # Add transaction to pool
        self.transaction_pool.add_transaction(transaction)
    
    def _handle_chain_request(self, data: Dict[str, Any], sender_id: str) -> None:
        """
        Handle a request for the blockchain.
        
        Args:
            data: Request data
            sender_id: ID of the requesting peer
        """
        if not self.blockchain:
            return
        
        response = {
            'type': 'chain_response',
            'data': {
                'chain': self.blockchain.to_dict(),
                'node_id': data['node_id']
            }
        }
        self._send_message(sender_id, response)
    
    def _handle_chain_response(self, data: Dict[str, Any]) -> None:
        """
        Handle a blockchain response from a peer.
        
        Args:
            data: Response data
        """
        if not self.blockchain:
            return
        
        # Verify the response is for this node
        if data['node_id'] != self.node_id:
            return
        
        # Try to replace the current chain
        self.blockchain.replace_chain(data['chain'])
    
    def _broadcast_message(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all peers.
        
        Args:
            message: Message to broadcast
        """
        for peer_id in self.peers:
            self._send_message(peer_id, message)
    
    def _send_message(self, peer_id: str, message: Dict[str, Any]) -> None:
        """
        Send a message to a specific peer.
        
        Args:
            peer_id: ID of the peer to send to
            message: Message to send
        """
        # TODO: Implement actual message sending logic
        # This would typically use a networking library like asyncio or twisted
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the node
        """
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'peers': list(self.peers)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DHTNode':
        """
        Create a DHTNode instance from a dictionary.
        
        Args:
            data: Dictionary containing node data
            
        Returns:
            DHTNode: New DHTNode instance
        """
        node = cls(
            node_id=data['node_id'],
            host=data['host'],
            port=data['port']
        )
        node.peers = set(data['peers'])
        return node 