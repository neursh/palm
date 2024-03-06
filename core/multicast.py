import socket, threading, platform

class UDPMulticastSocket:
    UDP_IP = "224.3.29.115"
    UDP_PORT = 45783
    INTERFACE = "0.0.0.0"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def __init__(self, udp_ip: str, udp_port: int, interface: str):
        self.UDP_IP = udp_ip
        self.UDP_PORT = udp_port
        self.INTERFACE = interface

    def start(self, threaded: bool = False):
        self.sock.bind((self.INTERFACE, self.UDP_PORT))

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.INTERFACE))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.UDP_IP) + socket.inet_aton(self.INTERFACE))

        if threaded:
            threading.Thread(target=self.listenForClient, daemon=True).start()
        else:
            self.listenForClient()

    def listenForClient(self):
        pc_name = platform.node()
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                info = data.decode()
                if addr[0] != self.INTERFACE and info.startswith("palm::client"):
                    self.sock.sendto(f"palm::server::{pc_name}".encode(), (self.UDP_IP, self.UDP_PORT))
            except:
                break

    def stop(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()