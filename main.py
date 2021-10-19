import time
import signal
import urllib.parse
import requests

from uuid import uuid4
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from p2p.node import P2PNode
from p2p.events import P2PEvents

from blockchain.blockchain import Blockchain

# Instantiate the Node
app = Flask(__name__)
# Handle CORS
CORS(app)

# Generate an unique address for this node
node_identifier = str(uuid4()).replace('-', '')

p2pNode = p2pNode = P2PNode()

class ExitFromApp(Exception):
    pass

def handle_p2p_events(event, data):
    if event == P2PEvents.CONNECTED:
        print('Connected with: ', data)
    elif event == P2PEvents.MESSAGE_RECEIVED:
        print('Received message: ', data)
        if(data['event'] == 'register_node') and data['host'] and data['port']:
            p2pNode.connect(host=data['host'], port=data['port'])

def shutdown(signal, frame):
    raise ExitFromApp

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We need to run the consensus algorithm to get the proof for the block that needs to be mined
    last_block = blockchain.last_block
    proof = blockchain.generate_proof(last_block)

    # New block is added to the chain
    block = blockchain.create_new_block(proof)

    response = {
        'message': "New Block Added",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def create_new_transaction():
    values = request.get_json()

    if values is None:
        return None, 401

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction for the block
    index = blockchain.create_new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    if values is None:
        return None, 400

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        print(node)
        requests.post(node + '/nodes/broadcast', json={
            'host': p2pNode.host,
            'port': p2pNode.port
        })

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
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

    return jsonify(nodes_list), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(p2pNode.connection_urls), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Conflicts resolved and chain replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


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

    args = parser.parse_args()

    port = args.port
    socket_port = args.socket

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
