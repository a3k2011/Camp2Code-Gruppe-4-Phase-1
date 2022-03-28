import basisklassen as bk
import datenlogger_tim  as dl
import json
from pandas import read_json
import time


class BaseCar(object):

    MAXSA = [50, 130]

    def __init__(self):
        self._json = self.readJSON()
        self._fw = bk.Front_Wheels(turning_offset=self._json["turning_offset"])
        self._bw = bk.Back_Wheels(forward_A=self._json["forward_A"], forward_B=self._json["forward_B"])
        self._dl = dl.Datenlogger("Logger")
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

    def fp1(self, v):
        # Vorwaerts 3sec
        self.drive(v, 1)
        time.sleep(3)

        # Stillstand 1sec
        self.stop()
        time.sleep(1)

        # Rueckwaerts 3sec
        self.drive(v, -1)
        time.sleep(3)

        #Ende
        self.stop()

    def fp2(self, v):
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
            self.stop()