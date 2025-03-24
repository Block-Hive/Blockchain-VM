from typing import List, Dict, Any, Set, Optional
import json
from time import time
import hashlib
from urllib.parse import urlparse
import sqlite3
import os
import multiprocessing
from multiprocessing import Pool, cpu_count
from functools import partial

from .block import Block
from .transaction import Transaction
from .database import DatabaseManager
from .config import Config


class Blockchain:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.nodes: Set[str] = set()
        self.difficulty = 4  # Number of leading zeros required in hash
        self.block_reward = 10.0  # Reward for mining a block
        self.transaction_fee = 0.1  # Fee per transaction
        self.max_block_size = 1000  # Maximum number of transactions per block
        self.confirmation_blocks = 6  # Number of blocks needed for confirmation
        self.target_block_time = 10  # Target time between blocks in seconds
        self.difficulty_adjustment_interval = 2016  # Number of blocks between difficulty adjustments
        
        self.current_transactions = []
        
        # Initialize database
        self.db = db_manager if db_manager else DatabaseManager()
        self._init_db()
        
        # Create genesis block if chain is empty
        if not self.chain:
            self.create_genesis_block()

    def _init_db(self):
        """Initialize the database."""
        self.db._init_db()
        
        # Load existing data
        self._load_from_db()

    def _load_from_db(self):
        """Load blockchain data from database."""
        # Load blocks
        blocks = self.db.get_all_blocks()
        
        for block_data in blocks:
            block = Block.from_dict(block_data)
            self.chain.append(block)
        
        # Load nodes
        self.nodes = set(self.db.get_active_nodes())
        
        # Load latest difficulty
        latest_difficulty = self.db.get_latest_difficulty()
        if latest_difficulty:
            self.difficulty = latest_difficulty

    def _save_to_db(self):
        """Save blockchain data to database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Clear existing data
        c.execute('DELETE FROM blocks')
        c.execute('DELETE FROM transactions')
        c.execute('DELETE FROM nodes')
        c.execute('DELETE FROM transaction_confirmations')
        c.execute('DELETE FROM difficulty_history')
        
        # Save blocks and transactions
        for block in self.chain:
            c.execute('''INSERT INTO blocks (block_index, timestamp, previous_hash, proof, hash)
                        VALUES (?, ?, ?, ?, ?)''',
                     (block.index, block.timestamp, block.previous_hash, block.proof, block.hash))
            
            for tx in block.transactions:
                c.execute('''INSERT INTO transactions (block_index, sender, recipient, amount, signature)
                            VALUES (?, ?, ?, ?, ?)''',
                         (block.index, tx['sender'], tx['recipient'], tx['amount'], tx['signature']))
                
                # Save transaction confirmation
                tx_hash = hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
                confirmations = max(0, len(self.chain) - block.index)
                c.execute('''INSERT INTO transaction_confirmations (transaction_hash, block_index, confirmations)
                            VALUES (?, ?, ?)''',
                         (tx_hash, block.index, confirmations))
            
            # Save difficulty history
            c.execute('''INSERT INTO difficulty_history (block_index, difficulty, actual_time)
                        VALUES (?, ?, ?)''',
                     (block.index, self.difficulty, block.timestamp))
        
        # Save nodes
        for node in self.nodes:
            c.execute('INSERT INTO nodes (address) VALUES (?)', (node,))
        
        conn.commit()
        conn.close()

    def create_genesis_block(self) -> None:
        """Create the first block in the chain."""
        # Check if genesis block already exists
        existing_block = self.db.get_block(0)
        if existing_block:
            # If genesis block exists, load it
            genesis_block = Block.from_dict(existing_block)
            self.chain.append(genesis_block)
            return

        # Create new genesis block if it doesn't exist
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time(),
            previous_hash="0" * 64
        )
        genesis_block.proof = self.proof_of_work(genesis_block)
        genesis_block.hash = genesis_block.calculate_hash()  # Calculate hash before saving
        self.chain.append(genesis_block)
        self.db.save_block(genesis_block.to_dict())

    def get_last_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]

    def get_balance(self, address: str) -> float:
        """
        Calculate the balance of an address.
        
        Args:
            address: The address to check balance for
            
        Returns:
            float: The current balance
        """
        balance = 0.0
        
        # Add received transactions
        for block in self.chain:
            for tx in block.transactions:
                if tx['recipient'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
        
        # Add pending transactions
        for tx in self.pending_transactions:
            if tx.recipient == address:
                balance += tx.amount
            if tx.sender == address:
                balance -= tx.amount
        
        return balance

    def validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validate a transaction before adding it to pending transactions.
        
        Args:
            transaction: The transaction to validate
            
        Returns:
            bool: True if transaction is valid, False otherwise
        """
        # Check if sender has sufficient balance (including transaction fee)
        sender_balance = self.get_balance(transaction.sender)
        if sender_balance < (transaction.amount + self.transaction_fee):
            return False
        
        # Verify transaction signature
        if not transaction.signature:
            return False
            
        # TODO: Add proper signature verification once we have the public key
        # For now, we'll just check if the signature exists
        
        return True

    def add_transaction(self, transaction: Transaction) -> int:
        """
        Add a new transaction to the list of pending transactions.
        
        Args:
            transaction: Transaction to add
            
        Returns:
            int: Index of the block that will contain this transaction
        """
        if not self.validate_transaction(transaction):
            raise ValueError("Invalid transaction")
            
        self.pending_transactions.append(transaction)
        return self.get_last_block().index + 1

    def proof_of_work(self, block: Block) -> int:
        """
        Calculate the proof of work for a block.
        
        Args:
            block: Block to mine
            
        Returns:
            int: The proof value that satisfies the difficulty requirement
        """
        proof = 0
        while not self.is_valid_proof(block, proof):
            proof += 1
        return proof

    def is_valid_proof(self, block: Block, proof: int) -> bool:
        """
        Check if a proof is valid.
        
        Args:
            block: Block to check
            proof: Proof value to verify
            
        Returns:
            bool: True if the proof is valid, False otherwise
        """
        block.proof = proof
        block_hash = block.calculate_hash()
        return block_hash.startswith('0' * self.difficulty)

    def get_transaction_confirmations(self, transaction_hash: str) -> int:
        """
        Get the number of confirmations for a transaction.
        
        Args:
            transaction_hash: Hash of the transaction to check
            
        Returns:
            int: Number of confirmations (0 if transaction not found)
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT confirmations FROM transaction_confirmations WHERE transaction_hash = ?',
                 (transaction_hash,))
        result = c.fetchone()
        
        conn.close()
        return result[0] if result else 0

    def is_transaction_confirmed(self, transaction_hash: str) -> bool:
        """
        Check if a transaction is confirmed.
        
        Args:
            transaction_hash: Hash of the transaction to check
            
        Returns:
            bool: True if transaction is confirmed, False otherwise
        """
        return self.get_transaction_confirmations(transaction_hash) >= self.confirmation_blocks

    def adjust_difficulty(self) -> None:
        """Adjust difficulty based on actual block time."""
        if len(self.chain) < self.difficulty_adjustment_interval:
            return
            
        # Get the last adjustment block
        last_adjustment = self.chain[-self.difficulty_adjustment_interval]
        current_block = self.chain[-1]
        
        # Calculate actual time taken
        actual_time = current_block.timestamp - last_adjustment.timestamp
        
        # Calculate target time
        target_time = self.target_block_time * self.difficulty_adjustment_interval
        
        # Adjust difficulty
        if actual_time < target_time / 4:  # Too fast
            self.difficulty += 1
        elif actual_time > target_time * 4:  # Too slow
            self.difficulty = max(1, self.difficulty - 1)

    def _calculate_proof_parallel(self, start_proof: int, end_proof: int, previous_hash: str) -> Optional[int]:
        """
        Calculate proof of work in parallel for a range of values.
        
        Args:
            start_proof: Starting proof value
            end_proof: Ending proof value
            previous_hash: Hash of the previous block
            
        Returns:
            Optional[int]: Valid proof if found, None otherwise
        """
        for proof in range(start_proof, end_proof):
            if self._verify_proof(proof, previous_hash):
                return proof
        return None

    def mine_block(self, miner_address: str) -> Optional[Block]:
        """
        Mine a new block.
        
        Args:
            miner_address: Address of the miner
            
        Returns:
            Optional[Block]: New block if mined successfully, None otherwise
        """
        if not self.pending_transactions:
            return None

        # Create new block
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            timestamp=self.get_current_timestamp(),
            previous_hash=previous_block.hash,
            proof=0
        )

        # Calculate proof of work in parallel
        num_processes = cpu_count()
        chunk_size = 10000  # Adjust based on your needs
        start_proof = 0
        found_proof = None

        with Pool(processes=num_processes) as pool:
            while found_proof is None:
                # Create ranges for parallel processing
                ranges = [
                    (i, min(i + chunk_size, i + chunk_size * 2))
                    for i in range(start_proof, start_proof + chunk_size * num_processes, chunk_size)
                ]
                
                # Map the ranges to worker processes
                results = pool.starmap(
                    self._calculate_proof_parallel,
                    [(start, end, new_block.previous_hash) for start, end in ranges]
                )
                
                # Check results
                for result in results:
                    if result is not None:
                        found_proof = result
                        break
                
                start_proof += chunk_size * num_processes

        if found_proof is None:
            return None

        # Set the proof and calculate hash
        new_block.proof = found_proof
        new_block.hash = new_block.calculate_hash()

        # Add mining reward transaction
        reward_transaction = {
            'sender': '0',  # System address
            'recipient': miner_address,
            'amount': self.mining_reward,
            'timestamp': self.get_current_timestamp(),
            'signature': ''  # No signature needed for mining reward
        }
        new_block.transactions.append(reward_transaction)

        # Add block to chain
        self.chain.append(new_block)
        self.db.save_block(new_block.to_dict())

        # Save transactions
        for transaction in new_block.transactions:
            self.db.save_transaction(transaction, new_block.index)

        # Clear pending transactions
        self.pending_transactions = []

        # Update difficulty
        self._update_difficulty(new_block)

        return new_block

    def is_valid_chain(self, chain: List[Block]) -> bool:
        """
        Check if a blockchain is valid.
        
        Args:
            chain: Blockchain to validate
            
        Returns:
            bool: True if the chain is valid, False otherwise
        """
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            # Check if the current block points to the previous block
            if current_block.previous_hash != previous_block.hash:
                return False

            # Verify the proof of work
            if not self.is_valid_proof(current_block, current_block.proof):
                return False

        return True

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes.
        
        Args:
            address: Address of the node to add
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        self._save_to_db()

    def resolve_conflicts(self, get_chain_from_node) -> bool:
        """
        Consensus algorithm. Resolves conflicts by replacing our chain with
        the longest one in the network.
        
        Args:
            get_chain_from_node: Function to get chain from a node
            
        Returns:
            bool: True if our chain was replaced, False otherwise
        """
        new_chain = None
        max_length = len(self.chain)

        # Get and verify the chains from all the nodes in our network
        for node in self.nodes:
            chain_data = get_chain_from_node(node)
            if chain_data is None:
                continue

            chain = [Block.from_dict(block) for block in chain_data]
            length = len(chain)

            # Check if the length is longer and the chain is valid
            if length > max_length and self.is_valid_chain(chain):
                max_length = length
                new_chain = chain

        # Replace our chain if we discovered a new, valid, longer chain
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the blockchain to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the blockchain
        """
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'nodes': list(self.nodes)
        }

    def get_block(self, index: int) -> Optional[Block]:
        """Get a block by index."""
        block_data = self.db.get_block(index)
        if block_data:
            return Block.from_dict(block_data)
        return None

    def get_all_blocks(self) -> List[Block]:
        """Get all blocks in the chain."""
        blocks_data = self.db.get_all_blocks()
        return [Block.from_dict(block_data) for block_data in blocks_data]

    def get_block_transactions(self, block_index: int) -> List[Transaction]:
        """Get all transactions in a block."""
        transactions_data = self.db.get_block_transactions(block_index)
        return [Transaction.from_dict(tx_data) for tx_data in transactions_data]

    def get_transaction_confirmations(self, transaction_hash: str) -> Optional[int]:
        """Get the number of confirmations for a transaction."""
        return self.db.get_transaction_confirmations(transaction_hash)

    def is_transaction_confirmed(self, transaction_hash: str) -> bool:
        """Check if a transaction is confirmed."""
        confirmations = self.get_transaction_confirmations(transaction_hash)
        return confirmations is not None and confirmations >= self.confirmation_blocks

    def add_transaction(self, transaction: Transaction) -> int:
        """Add a new transaction to the current transactions."""
        self.current_transactions.append(transaction)
        return len(self.chain) + 1

    def mine_block(self) -> Block:
        """Mine a new block."""
        # Get the last block
        last_block = self.chain[-1]
        
        # Calculate proof of work
        proof = self.proof_of_work(last_block)
        
        # Create new block
        block = Block(
            index=len(self.chain),
            timestamp=time(),
            transactions=self.current_transactions[:self.max_block_size],
            proof=proof,
            previous_hash=last_block.hash
        )
        
        # Add block to chain
        self.chain.append(block)
        self.db.save_block(block.to_dict())
        
        # Save transactions
        for transaction in block.transactions:
            self.db.save_transaction(transaction.to_dict(), block.index)
        
        # Clear current transactions
        self.current_transactions = []
        
        # Update transaction confirmations
        self._update_transaction_confirmations()
        
        # Adjust difficulty
        self.adjust_difficulty()
        
        return block

    def proof_of_work(self, last_block: Block) -> int:
        """Calculate proof of work."""
        proof = 0
        while not self.verify_proof(proof, last_block.hash):
            proof += 1
        return proof

    def verify_proof(self, proof: int, previous_hash: str) -> bool:
        """Verify proof of work."""
        guess = f'{proof}{previous_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == '0' * self.difficulty

    def verify_chain(self) -> bool:
        """Verify the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
            if not self.verify_proof(current_block.proof, current_block.previous_hash):
                return False
        
        return True

    def get_balance(self, address: str) -> float:
        """Get balance for an address."""
        balance = 0.0
        
        # Add block rewards
        for block in self.chain:
            if block.transactions and block.transactions[0].recipient == address:
                balance += self.block_reward
        
        # Add transaction amounts
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount + self.transaction_fee
                if transaction.recipient == address:
                    balance += transaction.amount
        
        return balance

    def adjust_difficulty(self):
        """Adjust mining difficulty based on block time."""
        if len(self.chain) % self.difficulty_adjustment_interval != 0:
            return
        
        # Get the time taken for the last difficulty_adjustment_interval blocks
        last_adjustment_block = self.chain[-self.difficulty_adjustment_interval]
        time_taken = self.chain[-1].timestamp - last_adjustment_block.timestamp
        
        # Save difficulty history
        self.db.save_difficulty(
            self.chain[-1].index,
            self.difficulty,
            time_taken
        )
        
        # Adjust difficulty
        if time_taken < self.target_block_time * self.difficulty_adjustment_interval * 0.9:
            self.difficulty += 1
        elif time_taken > self.target_block_time * self.difficulty_adjustment_interval * 1.1:
            self.difficulty = max(1, self.difficulty - 1)

    def _update_transaction_confirmations(self):
        """Update confirmation counts for all transactions."""
        for block in self.chain:
            for transaction in block.transactions:
                transaction_hash = transaction.hash
                confirmations = len(self.chain) - block.index
                self.db.save_transaction_confirmation(
                    transaction_hash,
                    block.index,
                    confirmations
                )

    def clear_chain(self):
        """Clear the blockchain."""
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.db.clear_database()
        self.create_genesis_block() 