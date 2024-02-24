import socket

class Client:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            print("Connected to server.")
            while True:
                data = sock.recv(1024)  # Buffer size of 1024 bytes
                if not data:
                    print("Connection closed by server.")
                    break
                print("Received:", data.decode('utf-8'))

if __name__ == "__main__":
    client = Client()
    client.start()
