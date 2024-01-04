import socket

SIZE = 1024
DEBUG = True
class Reciever:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(addr)
        self.seq_num = 0
        
    def recieve(self):
        packet, addr = self.socket.recvfrom(SIZE)
        num, data = self.extract_ack(packet)
        self.seq_num = num
        ack_pack = self.make_packet()
        self.socket.sendto(ack_pack, addr)
        if DEBUG:
            print(f"[+] recieved {packet} from {addr} and acked")
        return data
        
    def close(self):
        self.socket.close()     
                
    def make_packet(self, data =  b''):
        seq_bytes = self.seq_num.to_bytes(4, byteorder = 'little', signed = True)
        return seq_bytes + data 
        
    def extract_ack(self, packet):
        seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
        return seq_num, packet[4:]
    
    
    
def main(final_dest, recv_addr):
    reciever = Reciever(recv_addr)
    reciever_send_todest_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while(True):
        data = reciever.recieve()
        reciever_send_todest_socket.sendto(data, final_dest)
    
if __name__ == "__main__":
    # main (listen address server, destination)
    main(('localhost', 54321), ('localhost', 50001))