import socket
SERVER_ADDRESS = ('0.0.0.0', 9999)
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDRESS)
    clients = {}
    while True:
        data, addr = sock.recvfrom(4096)
        message = data.decode()
        if message.startswith("REGISTER"):
            _, client_id = message.split()
            address = addr
            clients[client_id] = address
            sock.sendto(f"REGISTERED {address[0]}".encode(), addr)
            print(f"REGISTERED {address[0]}: {client_id}")
        elif message.startswith("CONNECT"):
            _, src_id, dest_id = message.split()
            dest_addr = clients[dest_id]
            src_addr = clients[src_id]
            sock.sendto(f"CONNECT {dest_id} {dest_addr[0]} {dest_addr[1]}".encode(), src_addr)
            sock.sendto(f"CONNECT {src_id} {src_addr[0]} {src_addr[1]}".encode(), dest_addr)
            print(f"CONNECTED {src_id} {dest_id}")


if __name__ == "__main__":
    main()