import socket
import ssl
from concurrent.futures import ThreadPoolExecutor

# Proxy settings
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8000
MAX_THREADS = 10

def handle_client(client_socket):
    request = client_socket.recv(4096).decode('utf-8')
    first_line = request.split('\n')[0]
    if 'CONNECT' in first_line:
        handle_https(client_socket, first_line.split(' ')[1])
    else:
        handle_http(client_socket, request)

    client_socket.close()

def handle_http(client_socket, request):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    url = request.split(' ')[1]
    host = url.split('/')[2]
    remote_socket.connect((host, 80))
    remote_socket.send(request.encode())

    response = remote_socket.recv(4096)
    client_socket.send(response)
    remote_socket.close()

def handle_https(client_socket, url):
    parts = url.split(':')
    remote_host = parts[0]
    remote_port = int(parts[1])
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    client_socket.send("HTTP/1.1 200 Connection Established\r\n\r\n".encode())


    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(forward_data, client_socket, remote_socket)
        executor.submit(forward_data, remote_socket, client_socket)

def forward_data(source, destination):
    while True:
        data = source.recv(4096)
        if not data:
            break
        destination.send(data)

def main():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen()

    print(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            executor.submit(handle_client, client_socket)
if __name__ == "__main__":
    main()