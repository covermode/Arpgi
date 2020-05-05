# Game server adaptation    @LatypovIlya
"""Contains instances for standard server and game calculating. Executable, runs server,
interface"""


import socket
from shared_lib.exts import Periodical, log
from shared_lib.network import Mailing
from room import Room
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
        self.rooms = {}
        self.socket.bind(self.address)
        self.socket.listen(5)

        @self.route("get_player", method="GET")
        def get_player(sender_name):
            return self.where_player(sender_name).player(sender_name).get_model()

        @self.route("get_room_info", method="GET")
        def get_room_info(sender_name):
            return {
                'room_size': self.where_player(sender_name).map_size,
            }

        @self.route("get_entities", method="GET")
        def get_entities(sender_name):
            return self.where_player(sender_name).get_entity_models()

        @self.route("get_statics", method="GET")
        def get_statics(sender_name):
            return self.where_player(sender_name).get_static_models()

        @self.route("set_player_moving_target", method="SET")
        def set_player_moving_target(sender_name, data):
            player = self.where_player(sender_name).player(sender_name)
            map_size = self.where_player(sender_name).map_size
            if 0 <= player.x < map_size[0] and 0 <= player.y < map_size[1]:
                player.set_moving_target(data["delta_pos"])
                for owner_name, ses in connected.items():
                    if owner_name == sender_name:
                        continue
                    ses.set("update_entity", data={
                        'owner_name': sender_name,
                        'model': player.get_model()
                    })
                return 0
            else:
                raise ValueError("Can't move out the world")

    def route(self, address: str, method: str):
        """Nest of main network class method 'route' for registering methods as
        allowed to call from client."""
        return Mailing.route(self.routed, address, method)

    def where_player(self, owner_name):
        return self.rooms[connected[owner_name].room_name]

    def add_to_room(self, user_name, room_name):
        log.info(f"User {user_name} is being added to room {room_name}")

        spawn_point = self.rooms[room_name].spawn_point
        connected[user_name].room_name = room_name
        self.rooms[room_name].add_player(user_name, {
            'name': user_name,
            'x': spawn_point[0], 'y': spawn_point[1], 'w': 50, 'h': 50,
            'vel': 100, 'delta_pos_x': 0, 'delta_pos_y': 0, 'motion_start_x': spawn_point[0],
            'motion_start_y': spawn_point[1], 'motion_start_time': 0, 'alive': True
        })
        for owner_name in self.rooms[room_name].players:
            if owner_name == user_name:
                continue
            connected[owner_name].set("update_entity", data={
                'owner_name': user_name,
                'model': self.rooms[room_name].player(user_name).get_model()
            })

    def pop_from_room(self, user_name, room_name):
        log.info(f"User {user_name} is being removed from room {room_name}")

        for owner_name in self.rooms[room_name].players:
            if owner_name == user_name:
                continue
            connected[owner_name].set("delete_entity", data={
                'owner_name': user_name
            })

        connected[user_name].room_name = None
        self.rooms[room_name].pop_player(user_name)

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
                self.room_name = None
                # spawn_point = server.game.spawn_point
                # self.data = {"player": server.game.add_player(self.name, {
                #     'x': spawn_point[0], 'y': spawn_point[1], 'w': 50, 'h': 50,
                #     'vel': 100, 'delta_pos_x': 0, 'delta_pos_y': 0, 'alive': True
                # })}
                self._mail.send(str.encode(json.dumps({
                    'name': self.name,
                })))

        # this system uses dictionary of all connected users. keys are his in-system names,
        # values - 'Session' objects
        if _name in connected:
            raise NameError("This name already exists")
        session = Session(_connection, _name)
        connected[session.name] = session
        log.info(f"{_name} connected :)")

        self.add_to_room(session.name, "main")

        try:
            session.start_receiving()   # launches 'Mailing' receiving loop
        except Exception as error:      # Any unhandled error will disconnect you. Even 'SystemExit'
            log.info(f"User {session.name} disconnected because following error:\n"
                     f"\t{str(error)}")

        self.pop_from_room(session.name, session.room_name)

        log.info(f"{session.name} disconnected :(")
        connected.pop(session.name)
        print(connected)

    def main(self):
        def game_update():
            for room in self.rooms:
                self.rooms[room].update()

        def models_merge():
            log.debug("Merging")
            for room_name, room in self.rooms.items():
                for owner_name, player in room.players.items():
                    connected[owner_name].set("update_entities", data=room.get_entity_models())

        self.rooms["main"] = Room((1000, 1000))
        # self.game = Room((1000, 1000))
        updater = Periodical(game_update, 1 / 60)     # use Periodical launcher,
        updater.start()

        merger = Periodical(models_merge, 10)
        merger.start()

        log.info("Started serving")
        while True:
            connection, address = self.socket.accept()
            name = f"{address[0]}:{address[1]}_{random.randint(100000, 999999)}"
            ses = Thread(target=self.make_session, args=(connection, name))
            ses.start()


if __name__ == '__main__':
    _server_ = ArpgiServer("localhost", 5000)
    _server_.main()
