import basisklassen as bk
import datenlogger_tim  as dl
import json
from pandas import read_json
import time
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor


class BaseCar(object):

    MAXSA = [50, 130]
    LOG_FREQ = 0.1

    def __init__(self):
        self._json = self.readJSON()
        self._fw = bk.Front_Wheels(turning_offset=self._json["turning_offset"])
        self._bw = bk.Back_Wheels(forward_A=self._json["forward_A"], forward_B=self._json["forward_B"])
        self._worker = ThreadPoolExecutor(max_workers=4)
        self._dl = dl.Datenlogger("Logger")
        self._active = False
        # self.speed = 0
        self.steering_angle = 90
        self.direction = 1

    @staticmethod 
    def readJSON():
        with open("config.json", "r") as f:
            data = json.load(f)
        return data

    def drive(self, v, dir):
        self.speed = v
        self.direction = dir

    def stop(self):
        self._bw.stop()

    @property
    def speed(self):
        return self._bw.speed

    @speed.setter
    def speed(self, v):
        self._bw.speed = v

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = self._fw.turn(angle)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, dir):
        self._direction = -1 if dir==-1 else 0 if dir==0 else 1
        self.stop() if dir==0 else self._bw.backward() if dir==-1 else self._bw.forward()

    def getFahrdaten(self):
        return {'v': self.speed, 'sa': self.steering_angle, 'dir': self.direction}

    def loggerFunction(self):
        self._dl.start()
        while self._active:
            self._dl.append(self.getFahrdaten())
            time.sleep(self.LOG_FREQ)
        self._dl.save()

    def fp1(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.shutdown(wait=False)

        # Vorwaerts 3sec
        self.drive(v, 1)
        time.sleep(3)

        # Stillstand 1sec
        self.stop()
        time.sleep(1)

        # Rueckwaerts 3sec
        self.drive(v, -1)
        time.sleep(3)

        # Ende
        self._active = False
        self.stop()

    def fp2(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.shutdown(wait=False)

        for sa in self.MAXSA:
            # Vorwaerts 1sec gerade
            self.steering_angle = 90
            self.drive(v, 1)
            time.sleep(1)

            # Vorwaerts 8sec Max Lenkwinkel 
            self.steering_angle = sa
            time.sleep(8)

            # Stoppen
            self.stop()

            # Rueckwaerts 8sec Max Lenkwinkel
            self.drive(v, -1)
            time.sleep(8)

            # Rueckwaerts 1sec gerade
            self.steering_angle = 90
            time.sleep(1)

        # Ende
        self._active = False
        self.stop()