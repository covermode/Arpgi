# Useful stuff for coding   @LatypovIlya


from threading import Timer
import logging
import time

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


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed
