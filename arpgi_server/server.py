# Server base module. @LatypovIlya
"""Network server to get information from users by sockets, answer, and send them messages"""

import socket
import random
from threading import Thread
from shared_lib.network import Mailing
from shared_lib.exts import log

# that var is using for making sure that only
# one server is launched at the same time
_routed = {}    # used for storing instances for 'route' function
connected = {}  # dict of connected users. key=name, value=<Session> object


class Server:
    """Main game server class. Has function to call from client side"""

    def __init__(self, host, port):
        """Using socket for creating connection. It binds socket to (host, port) and
        start listening for connections. Any connected user will receive firstly his
        in-system name and then starts his session, and receiving loop in it.
        More detailed documentation look in 'network' module"""
        self.address = self.host, self.port = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.routed = {}
        self.socket.bind(self.address)
        self.socket.listen(5)

    def route(self, address: str, method: str):
        """Nest of main network class method 'route' for registering methods as
        allowed to call from client."""
        return Mailing.route(self.routed, address, method)

    def make_session(self, _connection: socket.socket, _name: str):
        """Creates session object and manually starts it.
        Session object is handling user requests, launch registered server methods
        and makes answers. (More detailed documentation for 'Mailing' are in 'network' module.
        Splitting all whole cycle of session live was did for nesting"""
        server = self

        class Session(Mailing):
            """Nest of main network communication module for server compatibility"""
            def __init__(self, connection: socket.socket, name: str):
                super(Session, self).__init__(connection, name)
                self.routed = server.routed
                self._mail.send(str.encode(self.name))

        # this system uses dictionary of all connected users. keys are his in-system names,
        # values - 'Session' objects
        if _name in connected:
            raise NameError("This name already exists")
        session = Session(_connection, _name)
        log.info(f"{_name} connected :)")
        self._start_session(session)

    def _start_session(self, session):
        """Starts created session. In cause that 'session' objects can't be created outer
        'make_session' function, this function can't be called from any other place but
        'make_session'. When user disconnects, ends session"""
        try:
            connected[session.name] = session
            session.start_receiving()   # launches 'Mailing' receiving loop
        except Exception as error:      # Any unhandled error will disconnect you. Even 'SystemExit'
            log.info(f"User {session.name} disconnected because following error:\n"
                     f"\t{str(error)}")
        self._end_session(session)

    def _end_session(self, session):
        log.info(f"{session.name} disconnected :(")
        connected.pop(session.name)

    def main(self):
        """Starts server infinite listening for new connections loop"""
        log.info("Started serving")
        while True:
            connection, address = self.socket.accept()
            name = f"{address[0]}:{address[1]}_{random.randint(100000, 999999)}"
            ses = Thread(target=self.make_session, args=(connection, name))
            ses.start()
