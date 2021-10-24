import time
import signal
import urllib.parse
import requests

from uuid import uuid4
from flask import Flask, json, jsonify, request, send_from_directory
from flask_cors import CORS

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
        print('Received message: ', data)
        if data['event'] == 'register_node' and data['host'] and data['port']:
            p2pNode.connect(host=data['host'], port=data['port'])
        elif data['event'] == 'new_transaction':
            transaction = wallet.create_transaction(data['recipient'], data['amount'], blockchain.unspent_transaction_outs, blockchain.transaction_pool)
            if transaction: blockchain.transaction_pool.append(transaction)
        elif data['event'] == 'init_chain':
            blockchain.replace_chain(data['chain'])
        elif data['event'] == 'init_pool':
            blockchain.replace_pool(data['pool'])
        elif data['event'] == 'block_created':
            blockchain.block_mining = True

            new_chain = blockchain.chain
            # new_chain.append(Block(len(new_chain) + 1, data['proof'], new_chain[-1].hash(), blockchain.transaction_pool))

            if blockchain.valid_chain(new_chain):
                blockchain.create_new_block(data['proof'])

            blockchain.block_mining = False


def shutdown(signal, frame):
    raise ExitFromApp


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/mint', methods=['GET'])
def mine():
    if not wallet.can_account_validate(blockchain.all_transactions):
        return 'You need to be a validator to mint blocks', 200
    
    if wallet.get_account_stake(blockchain.all_transactions) == 0:
        return 'You need to stake some coins in order to mint blocks', 200

    # We need to run the consensus algorithm to get the proof for the block that needs to be mined
    new_block = blockchain.create_new_block(wallet)
    if new_block is None:
        return jsonify('Another node completed mining before this node'), 200
    return jsonify('Minting Completed!'), 200


@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    return jsonify(wallet.get_account_balance(blockchain.unspent_transaction_outs)), 200

@app.route('/wallet/stake', methods=['GET'])
def get_stake():
    return jsonify(wallet.get_account_stake(blockchain.all_transactions)), 200

@app.route('/wallet/address', methods=['GET'])
def get_address():
    return wallet.public_key.toString(), 200

@app.route('/wallet/validator', methods=['GET'])
def is_validator():
    return wallet.can_account_validate(blockchain.all_transactions)


@app.route('/transactions/new', methods=['POST'])
def create_new_transaction():
    values = request.get_json()

    if values is None:
        return None, 401

    required = ['recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction for the block
    transaction = wallet.create_transaction(values['recipient'], float(values['amount']), blockchain.unspent_transaction_outs, blockchain.transaction_pool)

    if transaction is not None:
        blockchain.transaction_pool.append(transaction)
        return 'Added your transaction to pool', 200
    else:
        return 'Could not add your transaction', 401


@app.route('/transactions/validator', methods=['POST'])
def become_a_validator():
    if wallet.can_account_validate(blockchain.all_transactions):
        return 'you are already a validator', 200

    transaction = wallet.validator_transaction(CHAIN_ADDRESS, VALIDATOR_AMOUNT, blockchain.unspent_transaction_outs, blockchain.transaction_pool)
    if transaction is not None:
        blockchain.transaction_pool.append(transaction)
        return 'Added your transaction to pool', 200

    else:
        return 'Could not add your transaction', 401


# TODO: Complete the Stake Coins Function
@app.route('/transactions/stake', methods=['POST'])
def stake_coins():
    values = request.get_json()

    if values is None:
        return None, 401

    required = ['amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction = wallet.create_transaction(CHAIN_ADDRESS, float(values['amount']), blockchain.unspent_transaction_outs, blockchain.transaction_pool)

    if transaction is not None:
        blockchain.transaction_pool.append(transaction)
        return 'Added your transaction to pool', 200
    else:
        return 'Could not add your transaction', 401

    return 'Your Coins has been staked', 200


@app.route('/transactions/pool', methods=['GET'])
def unverified_transactions():
    return jsonify(blockchain.transaction_pool), 200


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

    args = parser.parse_args()

    port = args.port
    socket_port = args.socket

    if args.owner:
        wallet.load_keys_from_file('wallet/wallet.key')

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