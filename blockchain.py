import hashlib
import datetime
import json
import socket
import threading

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0  # Nonce for PoW
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(self.data).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8') +
                   str(self.nonce).encode('utf-8'))  # Include nonce in hash calculation
        return sha.hexdigest()

    def mine_block(self, difficulty):
        while self.hash[0:difficulty] != '0' * difficulty:  # Adjust difficulty by changing number of leading zeroes
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("Block mined: ", self.hash)

    def serialize(self):
        return {
            "index": self.index,
            "timestamp": str(self.timestamp),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2  # Difficulty for PoW

    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


class P2PServer:
    def __init__(self, blockchain, port):
        self.blockchain = blockchain
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"Listening for peers on port {self.port}")

    def handle_peer(self, client_socket):
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            if data == 'GET_CHAIN':
                chain_data = json.dumps([block.serialize() for block in self.blockchain.chain])
                client_socket.sendall(chain_data.encode('utf-8'))
        client_socket.close()

    def run(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_peer, args=(client_socket,))
            thread.start()


class P2PClient:
    def __init__(self, peer_ip, peer_port):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_chain_from_peer(self):
        try:
            self.client_socket.connect((self.peer_ip, self.peer_port))
            self.client_socket.sendall('GET_CHAIN'.encode('utf-8'))
            chain_data = b''
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                chain_data += data
            self.client_socket.close()
            return json.loads(chain_data.decode('utf-8'))
        except Exception as e:
            print("Error:", e)
            return None


# Example usage:

# Create a blockchain
my_blockchain = Blockchain()

# Start P2P server
p2p_server = P2PServer(my_blockchain, 5000)
thread = threading.Thread(target=p2p_server.run)
thread.start()

# Connect to peer and synchronize blockchain
p2p_client = P2PClient('127.0.0.1', 5000)
peer_chain = p2p_client.get_chain_from_peer()
if peer_chain:
    my_blockchain.chain = [Block(block['index'], datetime.datetime.strptime(block['timestamp'], "%Y-%m-%d %H:%M:%S.%f"), block['data'], block['previous_hash']) for block in peer_chain]

# Add some blocks
my_blockchain.add_block(Block(1, datetime.datetime.now(), "Block 1", ""))
my_blockchain.add_block(Block(2, datetime.datetime.now(), "Block 2", ""))
my_blockchain.add_block(Block(3, datetime.datetime.now(), "Block 3", ""))

# Check if the blockchain is valid
print("Is blockchain valid?", my_blockchain.is_chain_valid())

# Print the blocks
for block in my_blockchain.chain:
    print("Block Index:", block.index)
    print("Timestamp:", block.timestamp)
    print("Data:", block.data)
    print("Previous Hash:", block.previous_hash)
    print("Hash:", block.hash)
    print()

