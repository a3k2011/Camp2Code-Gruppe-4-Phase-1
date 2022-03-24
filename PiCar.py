import basisklassen
import time
import json

STEERINGE_ANGLE_MAX = 45

class BaseCar:
    def __init__(self):
        self._steering_angle = 0
        self._speed = 0
        self._direction = 1
        with open("config.json", "r") as f:
            data = json.load(f)
            turning_offset = data["turning_offset"]
            forward_A = data["forward_A"]
            forward_B = data["forward_B"]
        self.fw = basisklassen.Front_Wheels(turning_offset=turning_offset)
        self.bw = basisklassen.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
    
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
        """Hier wird auf ein anderes Winkelsystem normiert. 
        0 Grad = geradeaus, 
        -45 Grad ist max links, 
        +45 Grad ist max rechts"""
        if value > STEERINGE_ANGLE_MAX:
            self._steering_angle = 90+ STEERINGE_ANGLE_MAX
        elif value < (0-STEERINGE_ANGLE_MAX):
            self._steering_angle = 90-STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = 90+value
        self.fw.turn(self._steering_angle)
    
    def drive(self, geschwindigkeit, richtung):
        self.speed = geschwindigkeit
        self.bw.speed = self.speed
        self.direction = richtung
        if richtung > 0:
            self.bw.forward()
        elif richtung < 0:
            self.bw.backward()
        else:
            self.stop()
        
    def stop(self):
        self.bw.stop()