import asyncio
from core.local_ip import LocalIP
from core.multicast import UDPMulticastSocket
from core.phone_controller import PhoneController
from core.toasts import Toasts

if __name__ == '__main__':
    # Ask for default local IP interface.
    interface = LocalIP.get()

    # Start multicast server in thread.
    udpMulticast = UDPMulticastSocket(interface=interface, udp_ip="224.3.29.115", udp_port=45783)
    udpMulticast.start(threaded=True)

    # Start PhoneController server, providing a way to connect to the service.
    PhoneController(interface=interface, port=45784).startServer(threaded=True)

    asyncio.run(Toasts.showLaunched())

    input()