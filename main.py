import time
import signal
import urllib.parse
import requests

from uuid import uuid4
from flask import Flask, json, jsonify, request, send_from_directory
from flask_cors import CORS
from blockchain.transaction import Transaction, TransactionTypes

from p2p.node import P2PNode
from p2p.events import P2PEvents

from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.constants import VALIDATOR_AMOUNT, CHAIN_ADDRESS

from wallet.wallet import Wallet

# Instantiate the Node
app = Flask(__name__)

# Handle CORS
CORS(app)

# Generate an unique address for this node
node_identifier = str(uuid4()).replace('-', '')

p2pNode = p2pNode = P2PNode()

# Instantiate the Wallet
wallet = Wallet()

# Instantiate the Blockchain
blockchain = Blockchain()

class ExitFromApp(Exception):
    pass

def handle_p2p_events(event, data):
    if event == P2PEvents.CONNECTED:
        print('Connected with: ', data)
    elif event == P2PEvents.MESSAGE_RECEIVED:
        if data['event'] == 'register_node' and data['host'] and data['port']:
            p2pNode.connect(host=data['host'], port=data['port'])
        elif data['event'] == 'new_transaction':
            blockchain.transaction_pool.append(Transaction.from_dict(data['transaction']))
        elif data['event'] == 'init_chain':
            blockchain.replace_chain(data['chain'])
        elif data['event'] == 'init_pool':
            blockchain.replace_pool(data['pool'])
        elif data['event'] == 'block_created':
            blockchain.block_mining = True

            if blockchain.replace_chain(data['chain']):
                blockchain.transaction_pool = []

            blockchain.block_mining = False


def shutdown(signal, frame):
    raise ExitFromApp


"""
    Chain
    - This endpoint returns the whole full blockchain
    - All the blocks with transactions and the length of blockchain is returned as json
"""
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


"""
    Mint
    - The requirements a node has to fulfil to mint nodes is:
        - It must be a validator
        - It must stake some coints before minting
    - If any of the requirements fail to occur, the minting process is not taken forward
    - Once the requirements are fulfiled, consensus algorithms is run, block is created and appended to the chain
"""
@app.route('/mint', methods=['GET'])
def mine():
    # Checking whether the node is a validator or not
    if not wallet.can_account_validate(blockchain.all_transactions):
        return 'You need to be a validator to mint blocks', 200

    # Checking whether any coins are staked by the node or not
    if wallet.get_account_stake(blockchain.all_transactions) == 0:
        return 'You need to stake some coins in order to mint blocks', 200

    # Creating and minting the block
    new_block = blockchain.create_new_block(wallet)

    # If another minting node finishes the minting process None is returned from the earlier function
    if new_block is None:
        return jsonify('Another node completed mining before this node'), 200

    p2pNode.broadcast({
        'event': 'block_created',
        'chain': blockchain.chain
    })

    return jsonify('Minting Completed!'), 200


"""
    Get Balance
    - This endpoint returns the balance amount of coins present in the wallet
"""
@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    return jsonify(wallet.get_account_balance(blockchain.unspent_transaction_outs)), 200


"""
    Get Stake
    - This endpoint returns the amount of coins that are put on stake by the node
"""
@app.route('/wallet/stake', methods=['GET'])
def get_stake():
    return jsonify(wallet.get_account_stake(blockchain.all_transactions)), 200


"""
    Get Addresss
    - This endpoint returns the public key of the node's wallet
"""
@app.route('/wallet/address', methods=['GET'])
def get_address():
    return wallet.public_key.toString(), 200


"""
    Is Validator
    - This endpoint returns true if the given node is a validator
"""
@app.route('/wallet/validator', methods=['GET'])
def is_validator():
    return jsonify(wallet.can_account_validate(blockchain.all_transactions)), 200


"""
    Shows all the content of a wallet
    - Wallet Address
    - Account Balance
    - Is validator
    - Staked coins
"""
@app.route('/wallet', methods=["GET"])
def wallet_details():
    balance = wallet.get_account_balance(blockchain.unspent_transaction_outs)
    stake = wallet.get_account_stake(blockchain.all_transactions)
    address = wallet.public_key.toString(), 200
    is_validator = wallet.can_account_validate(blockchain.all_transactions)

    data = {
        'balance': balance,
        'stake': stake,
        'address': address,
        'is_validator': is_validator
    }

    return jsonify(data), 200


"""
    Create a new transaction
    - This is a POST Endpoint to create a new transaction between a sender and recipient
    - The request body contains two paramenters
        - Recipient - address of the wallet of recipient
        - Amount - number of coins that are need to be transferred

"""
@app.route('/transactions/new', methods=['POST'])
def create_new_transaction():
    values = request.get_json()

    # Validating the values from request body
    if values is None:
        return None, 401

    # Validating the required parameters of the request body
    required = ['recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    transaction = wallet.create_transaction(values['recipient'], float(values['amount']), blockchain.unspent_transaction_outs, blockchain.transaction_pool)

    # If transaction creation is successful, the transaction would be appended to the pool
    if transaction is not None:
        blockchain.transaction_pool.append(transaction)

        p2pNode.broadcast({
            'event': 'new_transaction',
            'transaction': transaction
        })

        return jsonify({'message': 'Added your transaction to pool'}), 200
    else:
        return jsonify({'message': 'Could not add your transaction'}), 401


"""
    Create a new validator transaction
    - This transaction makes the user a Validator
    - VALIDATOR_AMOUNT is burnt
        - VALIDATOR_AMOUNT burnt is non-refundable
        - The amount is transferred to CHAIN_ADDRESS (128 bits of '0')
"""
@app.route('/transactions/validator', methods=['POST'])
def become_a_validator():
    # Verify if the user is already a validator
    if wallet.can_account_validate(blockchain.all_transactions):
        return 'you are already a validator', 200

    transaction = wallet.create_transaction(CHAIN_ADDRESS, VALIDATOR_AMOUNT, blockchain.unspent_transaction_outs, blockchain.transaction_pool, TransactionTypes.VALIDATOR)
    if transaction is not None:
        blockchain.transaction_pool.append(transaction)

        p2pNode.broadcast({
            'event': 'new_transaction',
            'transaction': transaction
        })

        return 'Added your transaction to pool', 200

    else:
        return 'Could not add your transaction', 401


"""
    Create a new stake transaction
    - This is a POST Endpoint to create a new transaction to stake coins enabling the user to mint blocks
    - The request body contains two paramenters
        - Amount - number of coins that are need to be staked

"""
@app.route('/transactions/stake', methods=['POST'])
def stake_coins():
    values = request.get_json()

    # Validating the values from request body
    if values is None:
        return None, 401

    # Validating the required parameters(amount) of the request body
    required = ['amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction = wallet.create_transaction(CHAIN_ADDRESS, float(values['amount']), blockchain.unspent_transaction_outs, blockchain.transaction_pool, TransactionTypes.STAKE)

    # If transaction creation is successful, the transaction would be appended to the pool
    if transaction is not None:
        blockchain.transaction_pool.append(transaction)

        p2pNode.broadcast({
            'event': 'new_transaction',
            'transaction': transaction
        })

        return 'Added your transaction to pool', 200
    else:
        return 'Could not add your transaction', 401

    return 'Your Coins has been staked', 200


"""
    Get Transactions Pool
    - This endpoint returns all the transactions currently in the pool
    - Once the block is minted, the transaction pool is emptied and this endpoint then returns an empty array
"""
@app.route('/transactions/pool', methods=['GET'])
def unverified_transactions():
    return jsonify(blockchain.transaction_pool), 200


"""
    Get Nodes
    - This endpoint returns all the nodes connected to the blockchain
"""
@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(p2pNode.connection_urls), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    if values is None:
        return None, 400

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        requests.post(node + '/nodes/broadcast', json={
            'host': p2pNode.host,
            'port': p2pNode.port
        })

    response = {
        'message': 'New nodes have been added',
    }

    return jsonify(response), 201


@app.route('/nodes/broadcast', methods=['POST'])
def broadcast_node():
    values = request.get_json()

    print(values)

    if not values:
        return 'Could not find values', 401

    if not values['host'] or not values['port']:
        return 'Specify the node to broadcast', 401

    host = values['host']
    port = values['port']

    p2pNode.broadcast({
        'event': 'register_node',
        'host': host,
        'port': port
    })

    nodes_list = p2pNode.connection_urls

    p2pNode.connect(host, port)

    connected_node = p2pNode.get_connection(host, port)

    p2pNode.send_to_node(connected_node, {
        'event': 'init_chain',
        'chain': blockchain.chain
    })
    p2pNode.send_to_node(connected_node, {
        'event': 'init_pool',
        'pool': blockchain.transaction_pool
    })

    return jsonify(nodes_list), 200


@app.route('/', methods=['GET'])
def base():
	return send_from_directory('web/public', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('web/public', path)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('-p', '--port', default=4000, type=int, help='port to listen on')
    parser.add_argument('-s', '--socket', default=4001, type=int, help='p2p socket port to listen on')
    parser.add_argument('-o', '--owner', default=False, action='store_true')
    parser.add_argument('-k', '--wallet-key', help='Initialize the wallet with your private key')

    args = parser.parse_args()

    port = args.port
    socket_port = args.socket

    if args.owner:
        wallet.load_keys_from_file('wallet/wallet.key')

    if args.wallet_key:
        wallet.set_private_key(args.wallet_key)

    signal.signal(signal.SIGINT, shutdown)

    try:
        p2pNode.init(host='0.0.0.0', port=socket_port, callback=handle_p2p_events)
        p2pNode.start()

        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

        while True:
            continue

    except ExitFromApp:
        if p2pNode is not None:
            p2pNode.terminate_flag.set()
            p2pNode.join()