import socket
import struct
import os


hosts = None
with open('/etc/myhosts', 'r') as f:
        hosts = dict(line.strip().split() for line in f if line.strip() and not line.startswith('#'))


def respond(query_data):
    # Read the custom hosts file
    global hosts
    # Check if the queried domain is in the hosts file
    ip_address = hosts.get(query_data['qname'].rstrip('.'), None)

    # Pack the header
    id = query_data['id']
    flags = 0x8180  # Standard response, No error
    qdcount = query_data['qdcount']
    ancount = 1 if ip_address else 0  # Number of answers
    nscount = query_data['nscount']
    arcount = query_data['arcount']
    header = struct.pack('!HHHHHH', id, flags, qdcount, ancount, nscount, arcount)

    # Pack the question
    question = query_data['question']

    # Pack the answer
    answer = b''
    if ip_address:
        name = 0xC00C  # Pointer to the domain name in the question
        type = 1  # A record
        class_ = 1  # IN class
        ttl = 3600  # Time to live
        rdlength = 4  # Length of the RDATA field
        rdata = socket.inet_aton(ip_address)  # IP address
        answer = struct.pack('!HHHLH', name, type, class_, ttl, rdlength) + rdata

    return header + question + answer

def pars_dns_query(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """

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
        'question': dns_question  # Add the question field
    }
    
def dns_resolver(port):
    """_summary_

    Args:
        port (_type_): _description_
    """
    
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('127.0.0.1', port)
    sock.bind(server_address)

    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(4096)
        dns_query = pars_dns_query(data)
        response = respond(dns_query)
        sock.sendto(response, address)

# Call the function with a specific port
dns_resolver(5353)
