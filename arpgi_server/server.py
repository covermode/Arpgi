# Game server adaptation    @LatypovIlya
"""Contains instances for standard server and game calculating. Executable, runs server,
interface"""


import socket
from shared_lib.shared_models import EntityModel
from shared_lib.exts import Periodical, log
from shared_lib.network import Mailing
import random
import json
from threading import Thread


connected = {}


def player_state_changed(owner_name: str):
    """Sending to every connected to update their instance of target player
    :param owner_name: Name (in-system) of session, who owe target player"""
    for name, session in connected.items():
        if name == owner_name:
            continue
        session.send("update_model", json_data={
            'owner_name': owner_name,
            'model': connected[owner_name]["player"].get_model()
        })


class ArpgiServer:
    """Nest for Server core."""
    def __init__(self, host, port):
        """Following code is creation functions for routing handlers"""
        self.address = self.host, self.port = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.routed = {}
        self.socket.bind(self.address)
        self.socket.listen(5)

        @self.route("get_models", method="GET")
        def get_models(sender_name):
            return {name: session.data["player"].get_model()
                    for name, session in connected.items()}

        @self.route("get_model", method="GET")
        def get_model(sender_name):
            return connected[sender_name].data["player"].get_model()

        @self.route("set_player_moving_target", method="SET")
        def set_player_moving_target(sender_name, data):
            connected[sender_name].data["player"].set_moving_target(data["delta_pos"])
            for owner_name, ses in connected.items():
                if owner_name == sender_name:
                    continue
                ses.set("update_model", data={
                    'owner_name': sender_name,
                    'model': connected[sender_name].data["player"].get_model()
                })
            return 0

    def route(self, address: str, method: str):
        """Nest of main network class method 'route' for registering methods as
        allowed to call from client."""
        return Mailing.route(self.routed, address, method)

    def make_session(self, _connection: socket.socket, _name: str):
        """Creates session object and manually starts it.
        Session object is handling user requests, launch registered server methods
        and makes answers. (More detailed documentation for 'Mailing' are in 'network' module."""
        server = self

        class Session(Mailing):
            """Nest of main network communication module for server compatibility"""
            def __init__(self, connection: socket.socket, name: str):
                super(Session, self).__init__(connection, name)
                self.routed = server.routed
                self.data = {"player": EntityModel(
                    x=200, y=200, w=50, h=50, vel=5, delta_pos_x=0, delta_pos_y=0, alive=True
                )}
                self._mail.send(str.encode(json.dumps({
                    'name': self.name
                })))

        # this system uses dictionary of all connected users. keys are his in-system names,
        # values - 'Session' objects
        if _name in connected:
            raise NameError("This name already exists")
        session = Session(_connection, _name)
        log.info(f"{_name} connected :)")

        for owner_name, ses in connected.items():
            if owner_name == session.name:
                continue
            ses.set("update_model", data={
                'owner_name': session.name,
                'model': session.data["player"].get_model()
            })

        connected[session.name] = session
        try:
            session.start_receiving()   # launches 'Mailing' receiving loop
        except Exception as error:      # Any unhandled error will disconnect you. Even 'SystemExit'
            log.info(f"User {session.name} disconnected because following error:\n"
                     f"\t{str(error)}")

        for owner_name, ses in connected.items():
            if owner_name == session.name:
                continue
            ses.set("delete_model", data={
                'owner_name': session.name
            })

        log.info(f"{session.name} disconnected :(")
        connected.pop(session.name)
        print(connected)

    def main(self):

        def models_update():
            for name, ses in connected.items():
                ses.data["player"].update_pos()

        updater = Periodical(models_update, 1 / 60)     # use Periodical launcher,
        updater.start()

        log.info("Started serving")
        while True:
            connection, address = self.socket.accept()
            name = f"{address[0]}:{address[1]}_{random.randint(100000, 999999)}"
            ses = Thread(target=self.make_session, args=(connection, name))
            ses.start()


if __name__ == '__main__':
    _server_ = ArpgiServer("localhost", 5000)
    _server_.main()
