import os
import time
from datetime import datetime
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import basecar_tim as BCT
from basisklassen import Ultrasonic


class SonicCar(BCT.BaseCar):

    US_OFFSET = 15
    US_FREQ = 0.1
    LOG_FREQ = 0.1
    TIME_FREQ = 0.1

    def __init__(self):
        super().__init__()
        self._us = Ultrasonic()
        self._distance = None
        self._timerThread = None
        self._dlThread = None
        self._usThread = None
        self._rangierThread = None
        self._inpThread = None
        self._active = False
        self._hindernis = False
        self._tmpspeed = None

    @property 
    def distance(self):
        dist = self._us.distance()
        self._distance = dist if dist >= 0 else self.US_OFFSET+1
        return self._distance

    def getFahrdaten(self):
        return {'v': self.speed, 'sa': self.steering_angle, 'dir': self.direction, 'dist': self._distance}

    def zeitFunction(self, zeit):
        cntTime = time.perf_counter()
        while self._active and ((time.perf_counter()-cntTime) < zeit):
            time.sleep(self.TIME_FREQ)
        self._active = False

    def loggerFunction(self):
        self._dl.start()
        while self._active:
            self._dl.append(self.getFahrdaten())
            time.sleep(self.LOG_FREQ)
        self._dl.save()

    def usFunction(self):
        while self._active:
            if self._hindernis == False and not (self.distance-self.US_OFFSET) > 0:
                self._hindernis = True
            else:
                time.sleep(self.US_FREQ)

    def inputFunction(self):
        while self._active:
            inpUser = input("Fahrbefehl eingeben!")
            dictBefehle = {'f': 'self.direction = 1', 'b': 'self.direction = -1', 'l': 'self.steering_angle = 50', 'r': 'self.steering_angle = 130', 'e': 'self._active = False'}
            try:
                if inpUser in dictBefehle:
                    exec(dictBefehle[inpUser])
                elif type(int(inpUser)) and int(inpUser) >=0 and int(inpUser) <= 100:
                    self.speed = int(inpUser)
                    self._tmpspeed = int(inpUser)
                else:
                    raise Exception
            except Exception:
                print("Kein gültiger Befehl oder gültige Geschwindigkeit!")
                continue

    def erkundeWelt(self, v, zeit=None):
        self._active = True
        self._tmpspeed = v

        # Initialisiere Threads
        e = ThreadPoolExecutor(max_workers=4)
        if zeit == None:
            self._inpThread = e.submit(self.inputFunction)
        else:
            self._timerThread = e.submit(self.zeitFunction, zeit)
        self._dlThread = e.submit(self.loggerFunction)
        self._usThread = e.submit(self.usFunction)
        self._rangierThread = e.submit(self.rangieren)
        
        # Starte die Fahrt
        if self._active:
            self.drive(v, 1)
            
        # Wartet auf Fertigstellung aller Threads
        e.shutdown(wait=True)

        # Stopt die Fahrt
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
                self.speed = self._tmpspeed

                self._hindernis = False