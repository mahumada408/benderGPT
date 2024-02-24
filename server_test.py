import socket
import time

class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.setup_server()
        self.clients = []

    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Server started. Waiting for connection...")

    def handle_client(self, client_socket):
        try:
            while True:
                # Send current time to client
                message = f"Server Time: {time.ctime()}\n"
                for client_socket in self.clients:
                    client_socket.send(message.encode('utf-8'))
                time.sleep(0.01)  # Wait for 2 seconds before sending next message
        except ConnectionResetError:
            print("Client disconnected")
        finally:
            client_socket.close()

    def run(self):
        while len(self.clients) < 2:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            print(f"Connection established with {addr}")
        self.handle_client(client_socket)

    def close_server(self):
        self.server_socket.close()
        print("Server shut down successfully.")

if __name__ == "__main__":
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    finally:
        server.close_server()
