import socket
import logging
import threading
import datetime

# Set up logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)


class HoneypotServer:
    def __init__(self, host='0.0.0.0', port=2222):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Honeypot server starting on {self.host}:{self.port} (simulating SSH service)")

    def handle_client(self, client_socket, addr):
        try:
            logging.info(f"Connection attempt from {addr[0]}:{addr[1]}")

            # Send fake SSH banner to mimic a real SSH server
            banner = b"SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7\r\n"
            client_socket.send(banner)
            logging.info(f"Sent fake SSH banner to {addr[0]}:{addr[1]}")

            # Receive data (e.g., client version, login attempts)
            data = client_socket.recv(1024)
            if data:
                logging.info(f"Received data from {addr[0]}:{addr[1]}: {data.decode('utf-8', errors='ignore').strip()}")
            else:
                logging.info(f"No data received from {addr[0]}:{addr[1]}")

            # Simulate a login prompt to lure more interaction
            prompt = b"username: "
            client_socket.send(prompt)
            username = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()
            if username:
                logging.info(f"Attempted username from {addr[0]}:{addr[1]}: {username}")

            password_prompt = b"password: "
            client_socket.send(password_prompt)
            password = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()
            if password:
                logging.info(f"Attempted password from {addr[0]}:{addr[1]}: {password}")

            # Send fake denial to close interaction
            denial = b"Access denied\r\n"
            client_socket.send(denial)

        except Exception as e:
            logging.error(f"Error handling client {addr[0]}:{addr[1]}: {str(e)}")

        finally:
            client_socket.close()
            logging.info(f"Connection closed for {addr[0]}:{addr[1]}")

    def run(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                # Handle each connection in a separate thread for concurrency
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.start()
            except KeyboardInterrupt:
                logging.info("Shutting down honeypot server")
                break
            except Exception as e:
                logging.error(f"Server error: {str(e)}")


if __name__ == "__main__":
    honeypot = HoneypotServer()
    honeypot.run()