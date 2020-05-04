# Useful stuff for coding   @LatypovIlya


from threading import Timer
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="> %(asctime)-15s %(levelname)-8s || %(message)s")


class Periodical:
    def __init__(self, func, secs: float):
        self.func = func
        self.secs = secs
        self._started = False

    def start(self):
        def wrap():
            if self._started:
                timer = Timer(self.secs, wrap)
                timer.start()
                self.func()

        self._started = True
        wrap()

    def stop(self):
        self._started = False
