import os
import time
from datetime import datetime
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import basecar_tim as BCT
from basisklassen import Ultrasonic


class SonicCar(BCT.BaseCar):

    US_OFFSET = 10
    US_FREQ = 0.1
    LOG_FREQ = 0.1

    def __init__(self):
        super().__init__()
        self._us = Ultrasonic()
        self._distance = None
        self._timerThread = None
        self._dlThread = None
        self._usThread = None
        self._rangierThread = None
        self._active = False
        self._hindernis = False

    @property 
    def distance(self):
        dist = self._us.distance()
        self._distance = dist if dist >= 0 else 999
        return self._distance

    def getFahrdaten(self):
        return (str(self.speed), str(self.steering_angle), str(self.direction), str(self._distance))

    def zeitFunction(self, zeit):
        for i in range(zeit):
            time.sleep(1) 
        self._active = False

    def loggerFunction(self):
        self._dl.start()
        while self._active:
            self._dl.append(self.getFahrdaten())
            time.sleep(self.LOG_FREQ)
        self._dl.save()

    def usFunction(self):
        while self._active:
            if not (self.distance-self.US_OFFSET) > 0 and self._hindernis == False:
                self._hindernis = True
            else:
                time.sleep(self.US_FREQ)

    def erkundeWelt(self, v, zeit=999):
        self._active = True

        # Init Threads
        e = ThreadPoolExecutor(max_workers=4)
        self._timerThread = e.submit(self.zeitFunction, zeit)
        self._dlThread = e.submit(self.loggerFunction)
        self._usThread = e.submit(self.usFunction)
        self._rangierThread = e.submit(self.rangieren)
        e.shutdown(wait=False)

        # Start
        if self._active:
            self.drive(v, 1)

        while self._active:
            time.sleep(0.1)
            
        # Stop
        self.stop()   
        self._us.stop()

    def rangieren(self):
        while self._active:
            if self._hindernis:

                self.speed = 50
                self.steering_angle = 45
                self.direction = -1

                cntTime = time.perf_counter()
                while (time.perf_counter()-cntTime) < 2.55:
                    time.sleep(0.1)

                self.steering_angle = 90
                self.direction = 1

                self._hindernis = False

    



