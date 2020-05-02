# Game server adaptation    @LatypovIlya
"""Contains instances for standard server and game calculating. Executable, runs server,
interface"""


from server import Server, connected
from entity import Entity
from shared_lib.exts import Periodical


def player_state_changed(owner_name: str):
    """Sending to every connected to update their instance of target player
    :param owner_name: Name (in-system) of session, who owe target player"""
    for name, session in connected.items():
        if name == owner_name:
            continue
        session.send("update_model", json_data={
            'owner_name': owner_name,
            'model': connected[owner_name].player.get_model()
        })


class ArpgiServer(Server):
    """Nest for Server core."""
    def __init__(self, host, port):
        """Following code is creation functions for routing handlers"""
        super(ArpgiServer, self).__init__(host, port)

        @self.route("get_models", method="GET")
        def get_models(sender_name):
            return {name: session.data.player.get_model()
                    for name, session in connected.items()}

        @self.route("get_model", method="GET")
        def get_model(sender_name):
            return connected[sender_name].data.player.get_model()

        @self.route("set_player_moving_target", method="SET")
        def set_player_moving_target(sender_name, data):
            connected[sender_name].data.player.set_moving_target(data["delta_pos"])
            for owner_name, ses in connected.items():
                if owner_name == sender_name:
                    continue
                ses.set("update_model", data={
                    'owner_name': sender_name,
                    'model': connected[sender_name].data.player.get_model()
                })
            return 0

    class SessionData:
        """Abstract class for storing data"""
        pass

    def _start_session(self, session):
        """Nest for session start. Puts 'SessionData' in, initialize it with first instances,
        also sends everyone that new player has arrived"""
        session.data = self.SessionData()
        session.data.player = Entity((200, 200, 100, 100), 5)   # common entity as player

        for owner_name, ses in connected.items():

            if owner_name == session.name:
                continue
            ses.set("update_model", data={
                'owner_name': session.name,
                'model': session.data.player.get_model()
            })
        super(ArpgiServer, self)._start_session(session)

    def _end_session(self, session):
        """Nest for session end. Sends everyone that someone was destroyed"""
        for owner_name, ses in connected.items():
            if owner_name == session.name:
                continue
            ses.set("delete_model", data={
                'owner_name': session.name
            })
        super(ArpgiServer, self)._end_session(session)
        print(connected)

    def main(self):
        """Nest for main server cycle. Makes all models updating their position"""
        def models_update():
            for name, ses in connected.items():
                ses.data.player.update_pos()

        updater = Periodical(models_update, 1 / 60)     # use Periodical launcher,
        updater.start()
        super(ArpgiServer, self).main()


if __name__ == '__main__':
    _server_ = ArpgiServer("localhost", 5000)
    _server_.main()
