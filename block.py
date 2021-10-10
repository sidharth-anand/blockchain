import hashlib
from time import time
import json

class Block(dict):
    def __init__(self, index, proof_of_work, previous_hash, transactions = []) -> None:
        self.index = index
        self.timestamp = time()
        self.proof_of_work = proof_of_work
        self.previous_hash = previous_hash
        self.transactions = transactions

        dict.__init__(self, index=self.index, timestamp=self.timestamp, proof_of_work=self.proof_of_work, previous_hash=self.previous_hash, transactions=self.transactions)

    def hash(self):
        return hashlib.sha256(json.dumps(self, sort_keys=True).encode())
