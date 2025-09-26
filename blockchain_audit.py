import hashlib
import json
from datetime import datetime

class BlockchainAudit:
    def __init__(self, audit_chain_file: str = "audit_chain.db"):
        self.chain_file = audit_chain_file
        self.chain = self.load_chain()
        
    def create_genesis_block(self):
        """Create the first block in the audit chain"""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now().isoformat(),
            'data': 'GENESIS_BLOCK',
            'previous_hash': '0',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        return genesis_block
    
    def add_audit_entry(self, operation: str, table: str, user: str, old_data: dict, new_data: dict):
        """Add an immutable audit entry"""
        audit_data = {
            'operation': operation,
            'table': table,
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'old_data': old_data,
            'new_data': new_data,
            'checksum': self.calculate_data_checksum(new_data)
        }
        
        previous_block = self.chain[-1]
        new_block = {
            'index': previous_block['index'] + 1,
            'timestamp': datetime.now().isoformat(),
            'data': audit_data,
            'previous_hash': previous_block['hash'],
            'nonce': 0
        }
        
        # Proof of work (simple version)
        new_block['nonce'] = self.proof_of_work(new_block)
        new_block['hash'] = self.calculate_hash(new_block)
        
        self.chain.append(new_block)
        self.save_chain()
        
        return new_block['hash']  # Return transaction ID
    
    def verify_chain_integrity(self) -> bool:
        """Verify that the audit trail hasn't been tampered with"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check hash linkage
            if current_block['previous_hash'] != previous_block['hash']:
                return False
                
            # Check proof of work
            if not self.valid_proof(current_block):
                return False
                
        return True
    
    def proof_of_work(self, block, difficulty=4):
        """Simple proof of work algorithm"""
        block['nonce'] = 0
        computed_hash = self.calculate_hash(block)
        
        while not computed_hash.startswith('0' * difficulty):
            block['nonce'] += 1
            computed_hash = self.calculate_hash(block)
            
        return block['nonce']
    
    def calculate_hash(self, block):
        """Calculate SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
