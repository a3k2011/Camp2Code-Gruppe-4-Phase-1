import threading
import time
import os
from datetime import datetime
import basecar_tim as BCT
from basisklassen import Ultrasonic


class SonicCar(BCT.BaseCar):

    US_OFFSET = 10

    def __init__(self):
        super().__init__()
        self._us = Ultrasonic()
        self._distance = None
        self._logFilename = "CarLog-" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def rangieren(self):
        self.speed = 50
        self.steering_angle = 45 
        self.direction = -1

        cntTime = time.perf_counter()
        while (time.perf_counter() - cntTime) < 2.55:
            time.sleep(.1)

        self.steering_angle = 90
        self.direction = 1

    @property 
    def distance(self):
        dist = self._us.distance()
        self._distance = dist if dist >= 0 else 999
        return self._distance

    def getFahrdaten(self):
        return (str(self.speed), str(self.steering_angle), str(self.direction), str(self._distance))


class TimerThread(threading.Thread):

    def __init__(self, car, sec):
        super().__init__()
        self._car = car
        self._sec = sec

    def run(self):
        for i in range(self._sec):
            print("Time: ", i)
            time.sleep(1)

        self._car._us.stop()


class LoggerThread(threading.Thread):

    def __init__(self, car, sec):
        super().__init__()
        self._car = car
        self._sec = sec
        self._stop_event = threading.Event()

    def run(self):
        for i in range(self._sec):
            print("Logger:", i)
            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class USThread(threading.Thread):

    def __init__(self, car, freq):
        super().__init__()
        self._car = car
        self._freq = freq
        self._stop_event = threading.Event()

    def run(self):
        while (self._car.distance - self._car.US_OFFSET) > 0:
            print("Abstand: ", self._car._distance)
            time.sleep(self._freq)

        self._car.stop()   

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()            
    



