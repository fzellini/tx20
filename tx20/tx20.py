from . import testing

if not testing:
    import pigpio
import time
from threading import Thread


class TX20():
    PLEN = 100000           # packet lenght
    BITLEN = 1220           # bit lenght in uSeconds

    def __init__(self, pi, port):
        self.pi = pi
        self.port = port
        self.evs = []
        self.lts = 0
        self.tframe = 0
        self.windspeed = None
        self.wind_direction = None
        self.last_observation_time = None
        if not testing:
            pi.set_mode(port, pigpio.INPUT)
            pi.set_pull_up_down(port, pigpio.PUD_UP)
            self.cb = pi.callback(port, pigpio.EITHER_EDGE, self.sm)

    def sm(self, gpio, bit, ts):
        if ts-self.lts > TX20.PLEN and not bit:
            self.tframe = ts
            # decode packet after timeout
            Thread(target=self._decode).start()

        self.evs.append((ts, bit))
        self.lts = ts

    def _decode(self):
        time.sleep(float(TX20.PLEN)/1000000.0)
        self.decode()
        self.evs = []

    def decode(self):
        pos = 1
        # start
        sa = 0
        for i in range(5):
            sa = sa << 1 | self.bitat(pos)
            pos += 1
        # print "sa %d" % sa
        elements = []
        for pkt in (4, 12, 4, 4 | 0x80, 12 | 0x80):
            xor = 0
            if pkt & 0x80:
                xor = 1
            pkt &= 0xF
            shift = pkt - 1
            acc = 0
            for i in range(pkt):
                acc = acc >> 1 | ((self.bitat(pos) ^ xor) << shift)
                pos += 1
            elements.append(acc)
        #  checksum
        chk = (elements[0] + (elements[1]&0xf) + ((elements[1] >> 4) & 0xf) + ((elements[1] >> 8) & 0xf))
        chk &= 0xf
        if sa == 4 and elements[0] == elements[3] and elements[1] == elements[4] and elements[2] == chk:
            # print "checksum ok"
            self.windspeed = float(elements[1])/10
            self.wind_direction = float(elements[0])*22.5
            self.last_observation_time = time.time()
        # print elements

    def data_available(self):
        return self.last_observation_time is not None

    def getdata(self):
        r = (None, None, None)
        if self.data_available():
            r = (self.windspeed, self.wind_direction, self.last_observation_time)
            self.last_observation_time = None
        return r

    def bitat(self, t):
        t = t*TX20.BITLEN-TX20.BITLEN/2
        t += self.tframe
        v = self.evs[-1][1]
        le = (0, 0)
        for e in self.evs:
            if e[0] > t:
                v = le[1]
                break
            le = e
    #    print "bitat %d is %d" % (td,v)
        return v

    def stop(self):
        self.cb.cancel()

    def test(self, evs):
        for ev in evs:
            self.sm(None, ev[1], ev[0])





