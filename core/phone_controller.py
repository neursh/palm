import asyncio
from core.toasts import Toasts
from aiohttp import web
import pyautogui, socketio, threading

class PhoneController:
    authorized_sid = ""

    warned_ips = []
    blacklisted_ips = []

    interface = "0.0.0.0"
    port = 45784

    allowed_inputs = ["left", "right", "shiftf5", "f5", "esc"]

    def __init__(self, interface: str, port: int):
        self.interface = interface
        self.port = port

    def startServer(self, threaded: bool = False):
        sio = socketio.AsyncServer(cors_allowed_origins="*")
        app = web.Application()
        sio.attach(app)

        @sio.event
        async def connect(sid, environ):
            # Disconnect blacklisted IPs.
            if environ["REMOTE_ADDR"] in self.blacklisted_ips:
                await sio.disconnect(sid)
                return

            # Ask for PIN using toast if no sid is authorized.
            if self.authorized_sid == "" and await Toasts.askForPin(title="Controller request",
                                                                    description="Please enter the PIN code provided on your phone's screen to confirm.",
                                                                    pin=environ["HTTP_PIN"]):
                if environ["REMOTE_ADDR"] in self.warned_ips:
                    self.warned_ips.remove(environ["REMOTE_ADDR"])
                
                self.authorized_sid = sid
                asyncio.create_task(Toasts.rawToast("Palm is connected to your phone", "Palm is ready to receive inputs from your phone."))
                await sio.emit("authorized", to=sid)

            # Warn if the PIN is wrong.
            elif environ["REMOTE_ADDR"] not in self.warned_ips:
                self.warned_ips.append(environ["REMOTE_ADDR"])
                return await sio.disconnect(sid)

            # If the warned IP requested and the PIN is still wrong, blacklist it.
            else:
                self.warned_ips.remove(environ["REMOTE_ADDR"])
                self.blacklisted_ips.append(environ["REMOTE_ADDR"])
                return await sio.disconnect(sid)
        
        @sio.event
        async def key(sid, data):
            # Receive input from app, if a unknown request is sent, remove it from the socket.
            if sid == self.authorized_sid and data in self.allowed_inputs:
                pyautogui.press(data) if data != "shiftf5" else pyautogui.hotkey("shift", "f5")
            else:
                await sio.disconnect(sid)

        @sio.event
        async def disconnect(sid):
            if sid == self.authorized_sid:
                asyncio.create_task(Toasts.rawToast("Palm is disconnected from your phone", "Palm is ready to receive new controller connection."))
                self.authorized_sid = ""
        
        if threaded:
            threading.Thread(target=web.run_app, args=(app, ), kwargs={"host": self.interface, "port": self.port}, daemon=True).start()
        else:
            web.run_app(app, host=self.interface, port=self.port)