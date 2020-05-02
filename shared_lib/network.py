import socket
from time import sleep
from threading import Thread
import logging
import json
import hashlib
from datetime import datetime

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="> %(asctime)-15s %(levelname)-8s || %(message)s")


def _hash(string):
    return hashlib.sha256(string).hexdigest()


class Mailing:
    def __init__(self, mailman: socket.socket, name):
        self._mail = mailman
        self.receive_status = {}
        self.name = name
        self.routed = {}
        self.alive = True

    class LetterStatus:
        _state = None

        @property
        def state(self):
            return self._state

        @state.setter
        def state(self, val):
            if val is None:
                raise ValueError("Can't set None Status state")
            else:
                self._state = val

        def wait_for_change(self):
            while self._state is None:
                sleep(0.01)
            return self._state

    class NetworkError(Exception):
        pass

    class AskingError(NetworkError):
        pass

    class WrongServerActions(NetworkError):
        pass

    class AddressNotFoundError(WrongServerActions):
        pass

    class ReceivingError(NetworkError):
        pass

    @staticmethod
    def route(routing_dict, address: str, method: str):
        method = method.upper()
        if method not in ["GET", "SET"]:
            raise KeyError(f"This method {method} is not allowed. Only allowed ['GET', 'SET']")
        if (address, method) in routing_dict:
            raise KeyError("This address with this method already exists")

        def decorator(func):
            routing_dict[(address, method)] = func
            return func

        return decorator

    def start_receiving(self):
        while self.alive:
            try:
                data = self._mail.recv(4096)
                # - "type" can be one of this values ["GET" to get info from client
                #                                     "SET" to set info on a client side
                #                                     "ANS" if getting answer on some request
                # - ["ANS"] "key" sha256 for checking in receiving_status
                # - ["ANS"] "success" True if success else error happened
                # - ["ANS"] "error" (if not success) contains python error info
                # - ["ANS", "SET"] (if success) "data" received or sent data
                # - ["GET", "SET"] "address" of asked function
                # - ["GET", "SET"] "time" of sending request

                if not data:
                    raise Mailing.ReceivingError("Empty data received")
                response = json.loads(data)

                log.info("Received: " + data.decode())

                try:
                    if response["type"] == "ANS":
                        if not response["success"]:
                            raise Mailing.AskingError(f"Unsuccess response\n"
                                                      f"\tError: {response['error']}")
                        self.receive_status[response["key"]].state = response["data"]

                    elif response["type"] == "GET":
                        if (response["address"], "GET") not in self.routed:
                            raise Mailing.AddressNotFoundError(
                                f"No {response['address']} address with method 'GET' exists"
                                f"Maybe you forgot to initialize 'routed' property?")
                        data = {
                            'type': "ANS",
                            'key': _hash(data)
                        }
                        try:
                            value = self.routed[(response["address"], "GET")](
                                sender_name=self.name)
                        except Exception as error:
                            data["success"] = False
                            data["error"] = str(error)
                        else:
                            data["success"] = True
                            data["data"] = value
                        finally:
                            self._send(data)

                    elif response["type"] == "SET":
                        if (response["address"], "SET") not in self.routed:
                            raise Mailing.AddressNotFoundError(
                                f"No {response['address']} address with method 'SET' exists."
                                f"Maybe you forgot to initialize 'routed' property?")
                        data = {
                            'type': "ANS",
                            'key': _hash(data)
                        }
                        response_data = response["data"]
                        try:
                            value = self.routed[(response["address"], "SET")](
                                sender_name=self.name,
                                data=response_data)
                        except Exception as error:
                            data["success"] = False
                            data["error"] = str(error)
                        else:
                            data["success"] = True
                            data["data"] = value
                        finally:
                            self._send(data)

                    else:
                        raise Mailing.ReceivingError(f"Invalid type {response['type']}. Only"
                                                     f" ['GET', 'SET', 'ANS'] could be")
                except KeyError:
                    raise Mailing.WrongServerActions("Required request fields are empty")
            except Mailing.AskingError as error:
                log.error(f"Asking Error.\n"
                          f"\t{str(error)}")
            except Mailing.WrongServerActions as error:
                log.fatal(f"Wrong server action. He's kinda crazy\n"
                          f"\t{str(error)}")
                raise error
            except Mailing.ReceivingError:
                log.error("Empty data received.")

        log.info("Lost connection")
        self._mail.close()

    def _send(self, data):
        _ = json.dumps(data)
        log.info("Sendng: " + _)
        self._mail.send(str.encode(_))

    def _ask(self, data):

        key = _hash(str.encode(json.dumps(data)))
        # key used for getting answer

        self._send(data)

        status = Mailing.LetterStatus()               # creating status of request
        self.receive_status[key] = status       # to put here answer when received

        answer = status.wait_for_change()       # waiting until answer received
        return answer

    def get(self, address):
        data = {
            'type': "GET",
            'address': address,
            'time': str(datetime.now())
        }
        return self._ask(data)

    def set_and_go(self, address, data):
        setter = Thread(target=self.set, args=(address, data))
        setter.start()

    def set(self, address, data):
        data = {
            'type': "SET",
            'address': address,
            'time': str(datetime.now()),
            'data': data
        }
        return self._ask(data)

    def kill(self):
        self.alive = False
        self._mail.close()


# actual
class NetClient(Mailing):
    def __init__(self, host, port):
        self.address = self.host, self.port = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        name = self.connect()
        super(NetClient, self).__init__(self.socket, name)
        self.receiver = Thread(target=self.start_receiving)
        self.receiver.start()

        self.routed = {}
        log.info("Successfully started receiving in background :)")

    def route(self, address, method):
        return super(NetClient, self).route(self.routed, address, method)

    def connect(self):
        self.socket.connect(self.address)
        return self.socket.recv(4096).decode()
