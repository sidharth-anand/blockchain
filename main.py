from uuid import uuid4
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from blockchain import Blockchain


# Instantiate the Node
app = Flask(__name__)

# Handle CORS
CORS(app)

# Generate an unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We need to run the consensus algorithm to get the proof for the block that needs to be mined
    last_block = blockchain.last_block
    proof = blockchain.generate_proof(last_block)

    # Since we are computing the proof reward has to be assigned to us
    blockchain.create_new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # New block is added to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_new_block(proof, previous_hash)

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

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify(list(blockchain.nodes)), 200


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
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)