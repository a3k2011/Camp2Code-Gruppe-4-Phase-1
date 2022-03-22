"""
Grundfunktionen des PiCar

"""

import basisklassen
import time
import json

STEERINGE_ANGLE_MAX = 45 
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = -1
SPEED_MAX = 100
SPEED_MIN = 0

class BaseCar():
    """ 
    PiCar class BaseCar
    stellt die Grundfunktion fuer das Fahren zur Verfuegung    
    """
    
    def __init__(self) -> None:
        self.backwheels = basisklassen.Back_Wheels()
        self.steering = basisklassen.Front_Wheels()
        self._steering_angle = None
        self._speed = None
        self._direction = None
        self._steering_offset = 0
        self.init()
    
    def init(self):
        self._steering_angle = 0
        self._speed = 0
        self._direction = 0
        try:
            with open("config.json", "r") as f:
                self._steering_offset = json.load(f).get("turning_offset")
            print("turning offset: ", self._steering_offset)
        except:
            print("config.json FEHLER!!!")


    def drive(self, speed, direction):
        self.speed = speed
        self.direction = direction
        self.backwheels.speed = self.speed
        if self.direction == DIRECTION_FORWARD:
            self.backwheels.forward()
        elif self.direction == DIRECTION_BACKWARD:
            self.backwheels.backward()
    
    def stop(self):
        self.direction = 0
        self.speed = 0
        self.backwheels.stop()
        print("car stopped!!!", "Car dirves with", self._speed, "speed in direction", self._direction)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value == DIRECTION_FORWARD:
            self._direction = DIRECTION_FORWARD
        elif value == DIRECTION_BACKWARD:
            self._direction = DIRECTION_BACKWARD
        else:
            self._direction = 0


    @property
    def steering_angle(self):
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, value):
        """
        steering angel is physically limitet between 45 and 135 grad
        
        """
        if value > STEERINGE_ANGLE_MAX:
            self._steering_angle = 90+ STEERINGE_ANGLE_MAX
        elif value < (0-STEERINGE_ANGLE_MAX):
            self._steering_angle = 90-STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = 90+value
        self._steering_angle = self._steering_angle
        angle = self.steering_angle + self._steering_offset
        print("Sollwinkel", angle)
        self.steering.turn(angle)
        print("new steering angle: ", self._steering_angle)


    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        if value > SPEED_MAX:
            self._speed = SPEED_MAX
        elif value < SPEED_MIN:
            self._speed = SPEED_MIN
        else:
            self._speed = value

class SonicCar(BaseCar):
    def __init__(self) -> None:
        super().__init__()
        self.us = basisklassen.Ultrasonic()

    @property
    def distance(self):
        return self.us.distance()
    
    



        
        

def main():
    myCar = BaseCar()
   
if __name__ == "__main__":
    main()