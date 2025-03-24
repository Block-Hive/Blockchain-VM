import threading
import time
import requests
from typing import Set, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse

class NetworkManager:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.active_nodes: Set[str] = set()
        self.node_last_seen: Dict[str, datetime] = {}
        self.heartbeat_interval = 30  # seconds
        self.node_timeout = 90  # seconds
        self.discovery_interval = 300  # seconds
        
        # Start background threads
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.heartbeat_thread.start()
        self.discovery_thread.start()

    def _heartbeat_loop(self):
        """Send periodic heartbeats to all nodes."""
        while True:
            self._send_heartbeat()
            time.sleep(self.heartbeat_interval)

    def _discovery_loop(self):
        """Periodically discover new nodes from existing nodes."""
        while True:
            self._discover_nodes()
            time.sleep(self.discovery_interval)

    def _send_heartbeat(self):
        """Send heartbeat to all known nodes."""
        for node in self.blockchain.nodes:
            try:
                response = requests.post(
                    f'http://{node}/heartbeat',
                    json={'timestamp': time.time()},
                    timeout=5
                )
                if response.status_code == 200:
                    self.node_last_seen[node] = datetime.now()
                    self.active_nodes.add(node)
            except requests.RequestException:
                self._handle_node_failure(node)

    def _discover_nodes(self):
        """Discover new nodes from existing nodes."""
        for node in self.active_nodes:
            try:
                response = requests.get(f'http://{node}/nodes', timeout=5)
                if response.status_code == 200:
                    nodes = response.json().get('nodes', [])
                    for new_node in nodes:
                        if new_node not in self.blockchain.nodes:
                            self.blockchain.register_node(new_node)
            except requests.RequestException:
                self._handle_node_failure(node)

    def _handle_node_failure(self, node: str):
        """Handle node failure by removing it from active nodes."""
        self.active_nodes.discard(node)
        if node in self.node_last_seen:
            del self.node_last_seen[node]

    def get_active_nodes(self) -> Set[str]:
        """Get list of currently active nodes."""
        # Clean up inactive nodes
        now = datetime.now()
        inactive_nodes = {
            node for node, last_seen in self.node_last_seen.items()
            if now - last_seen > timedelta(seconds=self.node_timeout)
        }
        for node in inactive_nodes:
            self._handle_node_failure(node)
        
        return self.active_nodes

    def broadcast_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Broadcast a transaction to all active nodes.
        
        Args:
            transaction: Transaction to broadcast
            
        Returns:
            bool: True if at least one node accepted the transaction
        """
        success = False
        for node in self.active_nodes:
            try:
                response = requests.post(
                    f'http://{node}/transactions/new',
                    json=transaction,
                    timeout=5
                )
                if response.status_code == 201:
                    success = True
            except requests.RequestException:
                self._handle_node_failure(node)
        return success

    def broadcast_block(self, block: Dict[str, Any]) -> bool:
        """
        Broadcast a new block to all active nodes.
        
        Args:
            block: Block to broadcast
            
        Returns:
            bool: True if at least one node accepted the block
        """
        success = False
        for node in self.active_nodes:
            try:
                response = requests.post(
                    f'http://{node}/blocks/new',
                    json=block,
                    timeout=5
                )
                if response.status_code == 201:
                    success = True
            except requests.RequestException:
                self._handle_node_failure(node)
        return success 