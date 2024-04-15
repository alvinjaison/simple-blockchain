import hashlib
import json
import time
from collections import OrderedDict

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Adjust difficulty by changing number of leading zeroes

# Instantiate the blockchain
blockchain = Blockchain()

# Example usage:
blockchain.new_transaction('Alice', 'Bob', 1)
blockchain.new_transaction('Bob', 'Charlie', 2)
blockchain.new_transaction('Charlie', 'Alice', 3)

last_block = blockchain.last_block
last_proof = last_block['proof']
proof = blockchain.proof_of_work(last_proof)

# Mine a new block
blockchain.new_transaction(
    sender="0",  # "0" signifies a reward for mining
    recipient="Miner",
    amount=1,
)
previous_hash = blockchain.hash(last_block)
block = blockchain.create_block(proof, previous_hash)

print("Blockchain:", blockchain.chain)

