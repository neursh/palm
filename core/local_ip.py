import socket

class LocalIP:
    @staticmethod
    def get():
        tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmp.connect(("1.1.1.1", 80))

        return tmp.getsockname()[0]