import socket
import threading
import sys
import random
SERVER_ADDRESS = ('localhost', 9999)
connection_ip = None
connection_port = None
is_connected = False
def send_message(sock, command):
    sock.sendto(command.encode(), (connection_ip, connection_port))
def receive_messages(sock):
    try:
        while True:  
            data, addr = sock.recvfrom(4096)
            message = data.decode()
            if message.startswith("CONNECT"):
                global connection_ip, connection_port, is_connected
                _, dest_id, connection_ip, connection_port = message.split()
                connection_port = int(connection_port)
                is_connected = True
            else:
                print(message)
    except:
        return
def main():
    sock =  socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP   
    client_id = random.randint(0, 10**9)
    if len(sys.argv) == 4:
        SERVER_ADDRESS = (sys.argv[1], int(sys.argv[2]))
        client_id = sys.argv[3]
    elif len(sys.argv) == 2:    
        client_id = sys.argv[1]
        
    reg_message = f"REGISTER {client_id}"
    sock.sendto(reg_message.encode(), SERVER_ADDRESS)
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.start()
    try:
        while True:
            command = input()
            if command.startswith("end"):
                sock.close()
            elif not is_connected and command.startswith("CONNECT"):
                sock.sendto(command.encode(), SERVER_ADDRESS)
            else:
                if is_connected:
                    send_message(sock, command)
                else:
                    print("Please connect first: CONNECT [your_id] [dest_id]")
    except:
        sock.close()
    

if __name__ == "__main__":
    main()