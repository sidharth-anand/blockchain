import socket
import time
import threading
import typing

from .connection import P2PConnection
from .constants import MESSAGE_ENCODING, BUFFER_SIZE
from .events import P2PEvents

class P2PNode(threading.Thread):
    def __init__(self) -> None:
        threading.Thread.__init__(self)

        self.host = '0.0.0.0'
        self.port = 0

        self.terminate_flag = threading.Event()
        
        self.connections: typing.List[P2PConnection] = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.messages_sent = 0
        self.messages_recv = 0
        self.messages_rerr = 0

        self.event_handler = self.handler

    def init(self, host: str, port: int, callback: typing.Callable[[P2PEvents, typing.Any], None] = None) -> None:
        self.host = host
        self.port = port

        self.init_server()

        self.event_handler = callback if callback is not None else self.handler

    def init_server(self):
        print("Initialisation of the Node on port: " + str(self.port))

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen(1)

    def broadcast(self, data):
        self.messages_sent += 1

        for connection in self.connections:
            self.send_to_node(connection, data)
    
    def send_to_node(self, node, data):
        node.send(data)
    
    def handler(self, event, data):
        print(event, data)

    def connect(self, host: str, port: int) -> bool:
        if host == '0.0.0.0':
            host = 'localhost'

        if host == self.host and port == self.port:
            return False
        
        for connection in self.connections:
            if (host == connection.host and port == connection.port) or (host == connection.original_host and port == connection.original_port):
                return True
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(None)
            sock.connect((host, port))

            sock.send(P2PNode.to_url(self.host, self.port).encode(MESSAGE_ENCODING))
            (connection_host, connection_port) = P2PNode.from_url(sock.recv(BUFFER_SIZE).decode(MESSAGE_ENCODING))
            
            for connection in self.connections:
                if (connection_host == connection.host and connection_port == connection.port) or (connection_host == connection.original_host and connection_port == connection.original_port):
                    return True

            thread_client = self.create_new_connection(sock, host, port, connection_host, connection_port)
            thread_client.start()

            self.connections.append(thread_client)
            self.event_handler(P2PEvents.CONNECTED, (host, port))

            return True
        
        except Exception as e:
            print('could not connect', e)
            return False
    
    def disconnect(self, host, port):
        for connection in self.connections:
            if connection.host == host and connection.port == port:
                connection.stop()
                self.event_handler(P2PEvents.DISCONNECTED, (connection.host, connection.port))

    def stop(self):
        self.terminate_flag.set()
    
    def create_new_connection(self, sock, host, port, original_host = None, original_port = None):
        return P2PConnection(sock, host, port, self.event_handler, original_host, original_port)
    
    def run(self):
        self.event_handler(P2PEvents.STARTED, None)

        while not self.terminate_flag.is_set():
            try:
                try:
                    connection, client_addr = self.sock.accept()

                    (connection_host, connection_port) = P2PNode.from_url(connection.recv(BUFFER_SIZE).decode(MESSAGE_ENCODING))
                    connection.send(P2PNode.to_url(self.host, self.port).encode(MESSAGE_ENCODING))

                    thread_client = self.create_new_connection(connection, client_addr[0], client_addr[1], connection_host, connection_port)
                    thread_client.start()

                    self.connections.append(thread_client)

                    self.event_handler(P2PEvents.CONNECTED, (connection_host, connection_port))
                
                except socket.timeout:
                    continue

                except Exception as e:
                    raise e

            except KeyboardInterrupt:
                    self.stop()
            
            
        time.sleep(0.01)

        for connection in self.connections:
            connection.stop()
        
        time.sleep(1)

        for connection in self.connections:
            connection.join()
        
        self.sock.settimeout(None)
        self.sock.close()

        self.event_handler(P2PEvents.SHUTDOWN, None)

    @property
    def connection_urls(self):
        return list(map(lambda x: P2PNode.to_url(x.original_host, x.original_port), self.connections))

    @staticmethod
    def to_url(host: str, port: int) -> str:
        return host + ':' + str(port)

    @staticmethod
    def from_url(url: str):
        split = url.split(':')
        return split[0], int(split[1])