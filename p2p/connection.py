import socket
import time
import threading
import json
import typing

from p2p.constants import MESSAGE_ENCODING, END_OF_MESSAGE, BUFFER_SIZE
from p2p.events import P2PEvents

class P2PConnection(threading.Thread):
    def __init__(self, sock: socket.socket, host: str, port: int, callback: typing.Callable[[P2PEvents, typing.Any], None] = None, original_host: str = None, original_port: int = None) -> None:
        super(P2PConnection, self).__init__()

        self.host = host
        self.port = port

        self.original_host = original_host
        self.original_port = original_port

        self.sock = sock

        self.terminate_flag = threading.Event()

        self.callback = callback

        self.sock.settimeout(10.0)

    def send(self, data):
        if isinstance(data, str):
            try:
                self.sock.sendall(data.encode(MESSAGE_ENCODING) + END_OF_MESSAGE)
            except Exception as e:
                print(e)
                self.stop()
        
        elif isinstance(data, dict):
            try:
                json_data = json.dumps(data)
                json_data = json_data.encode(MESSAGE_ENCODING) + END_OF_MESSAGE
                self.sock.sendall(json_data)
                
            except TypeError as type_error:
                print('Error:', type_error)
            
            except Exception as e:
                self.stop()
        
        elif isinstance(data, bytes):
            self.sock.sendall(data + END_OF_MESSAGE)
        
        else:
            print('not valid')

    
    def stop(self):
        self.terminate_flag.set()

    def parse_packet(self, packet):
        try:
            decoded = packet.decode(MESSAGE_ENCODING)

            try:
                return json.loads(decoded)
            
            except json.decoder.JSONDecodeError:
                return decoded

        except UnicodeDecodeError:
            return packet
    
    def run(self):
        buffer = b''

        while not self.terminate_flag.is_set():
            chunk = b''

            try:
                chunk = self.sock.recv(BUFFER_SIZE)
            
            except socket.timeout:
                pass
            
            except Exception as e:
                self.terminate_flag.set()

            if chunk != b'':
                buffer += chunk
                message_end = buffer.find(END_OF_MESSAGE)

                while message_end > 0:
                    packet  = buffer[:message_end]
                    buffer = buffer[message_end + 1:]

                    if self.callback is not None:
                        self.callback(P2PEvents.MESSAGE_RECEIVED, self.parse_packet(packet))

                    message_end = buffer.find(END_OF_MESSAGE)
                
            time.sleep(0.01)

        self.sock.settimeout(None)
        self.sock.close()   