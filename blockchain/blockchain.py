import hashlib
import json
import requests
import typing

from time import time
from urllib.parse import urlparse

from blockchain.block import Block
from blockchain.transaction import Transaction

class Blockchain:
    def __init__(self):
        """
        Once our blockchain is instantiated
         - Transactions List is created which is used to store all the transactions before adding the block to the chain
         - Chain is empty list which is used to store all the blocks after mining
         - Set is empty set which is made such that there won't be any duplicate node entries to the network
         - Genesis Block is created which acts the first block in the chain with previous_hash = 1 and proof = 100
        """
        self.unverified_transactions: typing.List[Transaction] = []
        self.chain: typing.List[Block] = [Block.genesis()]
        self.nodes = set()

    def create_new_block(self, proof: int):
        """
        Create a new Block in the Blockchain
        <model> Block
         - index : Index of Block in the chain
         - timestamp : Time of transaction
         - transactions : List of Transactions tracked before mining the block
         - proof : Random number which can be used only once, and generated based on the consensus algorithm
         - previous_hash : Hash value of the previous block in the chain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: Block Object which is generated
        """

        self.chain.append(Block(len(self.chain) + 1, proof, self.chain[-1].hash(), self.unverified_transactions))

        # Unverified Transactions list is reset back after mining
        self.unverified_transactions = []

        return self.chain[-1]

    def create_new_transaction(self, sender: str, recipient: str, amount: int):
        """
        Creates a new transaction to go into the next mined Block
        <model> Transaction
         - Sender : Address of Sender
         - Recipient : Address of Recipient
         - Amount : Transaction Amoount

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Transaction Amount
        :return: We return the index of the block that contains the transaction
        """
        self.unverified_transactions.append(Transaction(sender, recipient, amount))

        return self.last_block.index + 1

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node added
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid Node URL')


    def valid_chain(self, chain):
        """
        Determine if a given blockchain as input is valid
        :param chain: given blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the block is correct
            last_block_hash = last_block.hash()
            if block.previous_hash != last_block_hash:
                return False

            # Check that the Proof is correct based on our Consensus Algorithm
            if not self.validate_proof(last_block.proof_of_work, block.proof_of_work, last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None
        chain_max_length = len(self.chain)

        # Verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > chain_max_length and self.valid_chain(chain):
                    chain_max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    @property
    def last_block(self):
        return self.chain[-1]

    def generate_proof(self, last_block):
        """
         - Let p be the proof of previous block
         - Let h be the hash of previous block
         - Let n be the proof of the current block which is to be computed
        Consensus Algorithm:
         - Compute the value n such that hash(pnh) ends in 4 zeroes

        :param last_block: last Block in blockchain
        :return: Valid Proof
        """

        previous_block_proof = last_block.proof_of_work #p
        previous_block_hash = last_block.hash() #h

        proof = 0 #n
        while self.validate_proof(previous_block_proof, proof, previous_block_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def validate_proof(previous_block_proof, proof, previous_block_hash):
        """
        Verifies the Proof ( Nonce )
        :param previous_block_proof: Proof of the previous block
        :param proof: Given Proof for verification
        :param previous_block_hash: Hash of the Previous Block
        :return: True if the proof is valid, False if not.
        """

        """
        Verification Process of the Proof
        Based on the consensus algorithm assumed for this blockchain
        We are finding the value of hash(pnh) and verify if it ends in 4 zeroes
        """

        number = f'{previous_block_proof}{proof}{previous_block_hash}'.encode()
        number_hashed = hashlib.sha256(number).hexdigest()
        return number_hashed[-4:] == "0000"