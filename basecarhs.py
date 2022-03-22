import basisklassen
import time

class BaseCar:
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 1
        self.fw = basisklassen.Front_Wheels()
        self.bw = basisklassen.Back_Wheels()
    
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, value):
        self._steering_angle = value
        self.fw.turn(self._steering_angle)
    
    def drive(self, geschwindigkeit, richtung):
        self.bw.speed = geschwindigkeit
        self._direction = richtung
        if richtung > 0:
            self.bw.forward()
        elif richtung < 0:
            self.bw.backward()
        else:
            self.stop()
        
    def stop(self):
        self.bw.stop()