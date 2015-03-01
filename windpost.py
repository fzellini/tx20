# run pigpiod with "sudo pigpiod -b 500"
# sudo apt-get install python-requests if not available

from tx20 import tx20
import time
import requests
import math


if __name__ == "__main__":

    BUFSIZE = 8
    dataBuf = []
    for i in range(0, BUFSIZE):
        dataBuf.append((0, 0, 0))
    bufIndex = 0
    bufCount = 0


    pi = None
    try:
        import pigpio
        pi = pigpio.pi()
        tx20 = tx20.TX20(pi, 11)
        while True:
            if tx20.data_available():
                dataBuf[bufIndex] = tx20.getdata()
                print dataBuf[bufIndex]
                tstamp = dataBuf[bufIndex][2]
                bufIndex += 1
                bufIndex %= BUFSIZE
                if bufCount < BUFSIZE:
                    bufCount += 1
                else:
                    # do average stuffs, emit record
                    avg = vee = vnn = 0
                    for wind_ms, wind_degrees, tstamp2 in dataBuf:
                        avg += wind_ms
                        vee += wind_ms*math.sin(2*math.pi*((90-wind_degrees)/360))
                        vnn += wind_ms*math.cos(2*math.pi*((90-wind_degrees)/360))
                    vee /= BUFSIZE
                    vnn /= BUFSIZE
                    average_speed = math.sqrt(vee*vee+vnn*vnn)
                    # at = math.atan2(vnn,vee)
                    at = math.degrees(math.atan2(vee, vnn))
                    at = 90-at
                    if at < 0:
                        at += 360
                    if at == 360:
                        at = 0
                    wspeed = average_speed
                    wdir = at
                    print "Averaged speed: %f, dir: %f, ts: %d" % (wspeed, wdir, tstamp)
                    requests.get ("http://mediaserver.home.lan/meteo/update",params={"ts":tstamp,"speed":wspeed,"dir":wdir}, timeout=1)
            time.sleep(.1)
        
    except ImportError:
        tx20 = tx20.TX20(pi, 9)
        tx20.test([(995236582, 0), (995239025, 1), (995240245, 0), (995243907, 1), (995245126, 0), (995263436, 1), (995264655, 0), (995267098, 1), (995268319, 0), (995269537, 1)])
        while True:
            if tx20.data_available():
                wspeed, wdir, tstamp = tx20.getdata()
                print "speed: %f, dir: %f, ts: %d" % (wspeed, wdir, tstamp)
                break
            time.sleep(.1)

    

