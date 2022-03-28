import os
import time
from datetime import datetime
import basecar_tim as BCT
from basisklassen import Ultrasonic


class SonicCar(BCT.BaseCar):

    US_OFFSET = 20
    US_FREQ = 0.1

    def __init__(self):
        super().__init__()
        self._us = Ultrasonic()
        self._distance = None
        self._hindernis = False
        self._tmpspeed = None

    @property 
    def distance(self):
        dist = self._us.distance()
        self._distance = dist if dist >= 0 else (self.US_OFFSET+1)
        return self._distance

    def getFahrdaten(self):
        return {'v': self.speed, 'sa': self.steering_angle, 'dir': self.direction, 'dist': self._distance}

    def usFunction(self):
        while self._active:
            if self._hindernis == False and not (self.distance-self.US_OFFSET) > 0:
                self._hindernis = True
            else:
                time.sleep(self.US_FREQ)

    def inputFunction(self):
        while self._active:
            inpUser = input("Fahrbefehl eingeben: ")
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

    def fp3(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.submit(self.usFunction)
        self._worker.shutdown(wait=False)

        # Starte die Fahrt
        if self._active:
            self.drive(v, 1)

        while not self._hindernis:
            time.sleep(0.1)
        
        # Ende
        self._active = False
        self.stop()
        self._us.stop()

    def fp4(self, v):
        # Initialisiere Threads
        self._active = True
        self._tmpspeed = v
        self._worker.submit(self.loggerFunction)
        self._worker.submit(self.usFunction)
        #self._worker.submit(self.inputFunction)
        self._worker.submit(self.rangieren)
        
        # Starte die Fahrt
        if self._active:
            self.drive(v, 1)
            
        # Wartet auf Fertigstellung aller Threads
        self._worker.shutdown(wait=True)

        # Stopt die Fahrt
        self.stop()
        self._us.stop()

    def rangieren(self):
        while self._active:
            if self._hindernis:

                self.direction = -1
                self.speed = 50
                self.steering_angle = 45

                cntTime = time.perf_counter()
                while (time.perf_counter()-cntTime) < 2.55:
                    time.sleep(0.1)

                self.steering_angle = 90
                self.direction = 1
                self.speed = self._tmpspeed

                self._hindernis = False