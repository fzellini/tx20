# run pigpiod with "sudo pigpiod -b 500"

from tx20 import tx20
import time


if __name__ == "__main__":

    pi = None
    try:
        import pigpio
        pi = pigpio.pi()
        tx20 = tx20.TX20(pi, 9)
        while True:
            if tx20.data_available():
                wspeed, wdir, tstamp = tx20.getdata()
                print "speed: %f, dir: %f, ts: %d" % (wspeed, wdir, tstamp)
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

    

