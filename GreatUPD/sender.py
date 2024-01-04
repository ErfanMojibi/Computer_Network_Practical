import socket
import select
import threading
from queue import Queue

# Define constants
SIZE = 1024
TIMEOUT_INTERVAL = 1
DEBUG = True

class Sender:
    def __init__(self):
        self.seq_num = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        
    def send(self, destination, data = b'' ):
        while True:
            packet = self.make_packet(data)
            self.socket.sendto(packet, destination)
            if DEBUG:
                print(f"[+] packet sent to {destination} {packet}")
                            
            readable, _, _ = select.select([self.socket], [], [], TIMEOUT_INTERVAL)
        
            if readable:
                ack, addr = self.socket.recvfrom(SIZE)
                seq, data = self.extract_ack(ack)
                if seq == self.seq_num:
                    if DEBUG:
                        print(f"[+] ack recieved: {self.seq_num}")
                    self.seq_num = 1 if self.seq_num == 1 else 0
                    return True
                else:
                    if DEBUG:
                        print(f"[!] bad ack recieved: {ack} but expected {self.seq_num}")
                    continue
            else:
                if DEBUG:
                    print(f"[-] not acked: {data}, resend")
                continue
            
            
    def make_packet(self, data):
        seq_bytes = self.seq_num.to_bytes(4, byteorder = 'little', signed = True)
        return seq_bytes + data 
        
    def extract_ack(self, packet):
        seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
        return seq_num, packet[4:]
        


def receiver_thread(sock, packets_list):
    while True:
        packet, addr = sock.recvfrom(SIZE)
        packets_list.put(packet)
        if DEBUG:
            print(f"[+] received from {addr} {packet}")

def sender_thread(destination, packets_list):
    sender = Sender()
    while True:
        if packets_list:
            packet = packets_list.get()
            sender.send(destination, packet)

def main(data_rec_address, destination):
    sender_receive_from_source_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_receive_from_source_socket.bind(data_rec_address)

    packets = Queue()
    receiver_thread_instance = threading.Thread(
        target=receiver_thread,
        args=(sender_receive_from_source_socket, packets)
    )
    receiver_thread_instance.start()

    sender_thread_instance = threading.Thread(
        target=sender_thread,
        args=(destination, packets)
    )
    sender_thread_instance.start()

    receiver_thread_instance.join()
    sender_thread_instance.join()


    
if __name__ == "__main__":
    # main (source of data, lossy link)
    main(('localhost', 12345), ('localhost', 40000))