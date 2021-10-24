import hashlib
import typing
import time

from blockchain.block import Block
from blockchain.transaction import Transaction, UnspentTransactionOut
from blockchain.constants import BLOCK_GENERATION_INTERVAL, DIFFICULTY_ADJUSTMENT_ITNERVAL

from wallet.wallet import Wallet

class Blockchain:
    def __init__(self):
        """
        Once our blockchain is instantiated
         - Transactions List is created which is used to store all the transactions before adding the block to the chain
         - Chain is empty list which is used to store all the blocks after mining
         - Set is empty set which is made such that there won't be any duplicate node entries to the network
         - Genesis Block is created which acts the first block in the chain with previous_hash = 1 and proof = 100
        """
        self.transaction_pool: typing.List[Transaction] = []
        self.chain: typing.List[Block] = [Block.genesis()]

        unspent_transaction_outs = Transaction.process_transactions(self.chain[0].transactions, [], self.chain[0].index)

        if unspent_transaction_outs is not None:
            self.unspent_transaction_outs: typing.List[UnspentTransactionOut] = unspent_transaction_outs
        else:
            self.unspent_transaction_outs: typing.List[UnspentTransactionOut] = []

        self.block_mining = False

    def create_new_block(self, wallet: Wallet):
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

        coinbase_transaction = Transaction.generation_coinbase_transaction(wallet.public_key.toString(), self.last_block.index + 1)

        new_block = self.create_new_block_raw(wallet, [coinbase_transaction] + self.transaction_pool)
        if new_block is not None:
            # TODO: Update the Transactions Processing
            for i in range(len(self.chain)):
                self.unspent_transaction_outs = Transaction.process_transactions(self.chain[i].transactions, self.unspent_transaction_outs, self.chain[i].index)

            if self.unspent_transaction_outs is not None:
                self.unspent_transaction_outs: typing.List[UnspentTransactionOut] = self.unspent_transaction_outs
            else:
                self.unspent_transaction_outs: typing.List[UnspentTransactionOut] = []
            # Unverified Transactions list is reset back after mining
            self.transaction_pool = []
            return self.last_block
        else:
            return None

    def create_new_block_raw(self, wallet: Wallet, transactions: typing.List[Transaction]) -> typing.Union[Block, None]:
        difficulty = self.get_difficulty()
        new_block = self.find_block(self.last_block.index + 1, self.last_block.hash(), transactions, difficulty, wallet)

        if new_block is not None:
            self.chain.append(new_block)

        return new_block

    def find_block(self, index: int, previous_hash: str, transactions: typing.List[Transaction], difficulty: int, wallet: Wallet) -> typing.Union[Block, None]:
        past_timestamp = 0

        while not self.block_mining:
            current_timestamp = self.get_usable_timestamp()
            if not current_timestamp == past_timestamp:
                if self.validate_stake(previous_hash, wallet.public_key.toString(), current_timestamp, wallet.get_account_balance(self.unspent_transaction_outs), difficulty):
                    return Block(index, previous_hash, difficulty, wallet.get_account_balance(self.unspent_transaction_outs), wallet.public_key.toString(), transactions)
                past_timestamp = current_timestamp

        return None

    def get_usable_timestamp(self) -> int:
        return round(time.time() / 1000)

    def create_new_transaction(self, wallet: Wallet, recipient: str, amount: float):
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
        new_transaction = wallet.create_transaction(recipient, amount, self.unspent_transaction_outs, self.transaction_pool)
        if new_transaction is not None:
            self.transaction_pool.append(new_transaction)
            return self.last_block.index + 1
        else:
            return -1

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

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def replace_chain(self, chain_data: typing.List[dict]):
        new_chain: typing.List[Block] = []

        for block in chain_data:
            new_chain.append(Block.from_dict(block))

        if self.valid_chain(new_chain):
            self.chain = new_chain
            return True

        return False


    def replace_pool(self, new_pool: typing.List[dict]):
        self.transaction_pool = []

        for transaction in new_pool:
            self.transaction_pool.append(Transaction.from_dict(transaction))

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
        while self.validate_proof(previous_block_proof, proof, previous_block_hash) is False and not self.block_mining:
            proof += 1

        if self.block_mining == True:
            return None

        return proof

    def get_difficulty(self) -> int:
        if self.last_block.index % DIFFICULTY_ADJUSTMENT_ITNERVAL == 0:
            return self.get_adjusted_difficulty()
        else:
            return self.last_block.difficulty

    def get_adjusted_difficulty(self) -> int:
        prev_adjusted_block = self.chain[len(self.chain) - DIFFICULTY_ADJUSTMENT_ITNERVAL]

        time_expected = BLOCK_GENERATION_INTERVAL * DIFFICULTY_ADJUSTMENT_ITNERVAL
        time_taken = self.last_block.timestamp - prev_adjusted_block.timestamp

        if time_taken < time_expected / 2:
            return prev_adjusted_block.difficulty + 1
        elif time_taken > time_expected / 2:
            return prev_adjusted_block.difficulty - 1
        else:
            return prev_adjusted_block.difficulty

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

    @staticmethod
    def validate_stake(previous_hash: str, address: str, timestamp: int, balance: float, difficulty: int) -> bool:
        difficulty = difficulty + 1

        balance_over_diff = 2 ** 256 * balance / difficulty
        staking_hash = int(hashlib.sha256((previous_hash + address + str(timestamp)).encode()).hexdigest(), 16)

        return balance_over_diff - staking_hash >= 0