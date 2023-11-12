import concurrent.futures
import socket
import struct



def parse_hosts_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    hosts = {}
    for line in lines:
        if line.startswith('#'):
            continue
        parts = line.split()
        ip_address = parts[0]
        hostnames = parts[1:]
        for hostname in hostnames:
            hosts[hostname] = ip_address
    return hosts

hosts = parse_hosts_file('/etc/myhosts')

def respond(query_data):
    global hosts
    # Check if the queried domain is in the hosts file
    ip_address = hosts.get(query_data['qname'].rstrip('.'), None)

    # Pack the header
    id = query_data['id']
    flags = 0x8080  # Standard response, No error
    qdcount = query_data['qdcount']
    ancount = 1 if ip_address else 0  # Number of answers
    nscount = 0
    arcount = 0

    # Pack the question
    question = query_data['question']

    # Pack the answer
    answer = b''
    if ip_address:
        name = 0xC00C  # Pointer to the domain name in the question
        type = 1  # A record
        class_ = 1  # IN class
        ttl = 0  # Time to live
        rdlength = 4  # Length of the RDATA field
        rdata = socket.inet_aton(ip_address)  # IP address
        answer = struct.pack('!HHHLH', name, type, class_, ttl, rdlength) + rdata
    else:
        flags = 0x8083
    
    header = struct.pack('!HHHHHH', id, flags, qdcount, ancount, nscount, arcount)
    return header + question + answer

def parse_dns_query(data):
    dns_header = data[:12]
    dns_question = data[12:]

    # Unpack the header
    (id, flags, qdcount, ancount, nscount, arcount) = struct.unpack('!HHHHHH', dns_header)

    # Unpack the question
    qname, qtype, qclass = '', '', ''
    i = 0
    while True:
        length = dns_question[i]
        if length == 0:
            break
        qname += dns_question[i+1:i+1+length].decode() + '.'
        i += length + 1
    qtype, qclass = struct.unpack('!HH', dns_question[i+1:i+5])
    dns_question = dns_question[: i+5]
    return {
        'id': id,
        'flags': flags,
        'qdcount': qdcount,
        'ancount': ancount,
        'nscount': nscount,
        'arcount': arcount,
        'qname': qname,
        'qtype': qtype,
        'qclass': qclass,
        'question': dns_question
    }
    
def handle_query(data, address, sock):
        dns_query = parse_dns_query(data)
        response = respond(dns_query)
        return response, address, sock
    
    
def handle_query_result(future):
    response, address, sock = future.result()
    sock.sendto(response, address)
    
def dns_resolver(port, pool_size=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', port)
    sock.bind(server_address)
    with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
        while True:
            print('\nwaiting to receive message')
            data, address = sock.recvfrom(4096)
            future = executor.submit(handle_query, data, address, sock)
            future.add_done_callback(handle_query_result)


if __name__ == "__main__":
    dns_resolver(5353)