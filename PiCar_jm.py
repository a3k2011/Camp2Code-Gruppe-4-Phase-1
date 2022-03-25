"""
Grundfunktionen des PiCar
"""

from curses.ascii import isdigit
from pydoc import isdata
import basisklassen as bk
import time
from datetime import datetime
import json
import os
import datenlogger

STEERINGE_ANGLE_MAX = 45
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = -1
SPEED_MAX = 100
SPEED_MIN = 0


class BaseCar:
    """Basis-Implementierung der Fahrzeug-Klasse fuer das Sunfounder PiCar"""

    def __repr__(self) -> str:
        return "Klasse BaseCar"

    def __init__(self):
        """Erzeugen der Klasse, laden der Config-Werte aus config.json"""
        with open("config.json", "r") as f:
            data = json.load(f)
            turning_offset = data["turning_offset"]
            forward_A = data["forward_A"]
            forward_B = data["forward_B"]
            self._log_file_path = data.get("log_file_path")
            print("Turning Offset: ", turning_offset)
            print("Forward A: ", forward_A)
            print("Forward B: ", forward_B)

        self.fw = bk.Front_Wheels(turning_offset=turning_offset)
        self.bw = bk.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self._dl = datenlogger.Datenlogger(log_file_path=self._log_file_path)
        self._steering_angle = 0
        self._speed = 0
        self._direction = 0

    def logger_start(self):
        self._dl.start()

    def logger_log(self):
        self._dl.append(self.drive_data)

    def logger_save(self):
        self._dl.save()

    def drive(self, speed, direction):
        """Methode drive
        args:   speed (Geschwindigkeit in % von 0 bis 100)
                direction (Fahrtrichtung: 1=vor, 0=stop, -1=zurück)
        """
        self.speed = speed
        self.direction = direction
        self.bw.speed = self.speed
        if self.direction == DIRECTION_FORWARD:
            self.bw.forward()
        elif self.direction == DIRECTION_BACKWARD:
            self.bw.backward()
        else:
            self.bw.stop()

    def stop(self):
        """sofortiges anhalten des PiCar"""
        self.direction = 0
        self.speed = 0
        self.bw.stop()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        """gesetzte Fahrrichtung sichern

        Args:
            value (int): setzen der Fahrtrichtung (-1=rueckwaerts, 0=stehen, 1=vorwaerts)
        """
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
        """setzen des Lenkwinkels
            in der Basisklasse ist dieser zw. 45 und 135 Grad mit Geradeauslauf bei 90 Grad definiert
            Hier wird er angepasst auf Werte zwischen -45 und 45 Grad, 0 Grad ist gerade

        Args:
            value (int): Soll-Winkel der Lenkung (-45 ... 45 Grad)
        """
        if value > STEERINGE_ANGLE_MAX:
            self._steering_angle = 90 + STEERINGE_ANGLE_MAX
        elif value < (0 - STEERINGE_ANGLE_MAX):
            self._steering_angle = 90 - STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = 90 + value
        self._steering_angle = self._steering_angle
        self.fw.turn(self._steering_angle)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        """setzen der Sollgeschwindigkeit mit Limit 0 ... 100

        Args:
            value (int): Sollgeschwindigkeit in %
        """
        if value > SPEED_MAX:
            self._speed = SPEED_MAX
        elif value < SPEED_MIN:
            self._speed = SPEED_MIN
        else:
            self._speed = value

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten

        Returns:
            tuple: speed, direction, steering_angle
        """
        return [self._speed, self._direction, self._steering_angle]


class SonicCar(BaseCar):
    """Die Klasse Sonic-Car fuegt die Funktion des Ultraschallsensors zu BaseCare hinzu

    Args:
        BaseCar (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.us = bk.Ultrasonic(timeout=0.05)
        self._distance = 300

    @property
    def distance(self):
        """Methode distance() von SonicCar

        Returns:
            int: return des Abstands in cm
        """
        self._distance = self.us.distance()
        return self._distance

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten

        Returns:
            tuple: speed, direction, steering_angle, distance
        """
        return [self._speed, self._direction, self._steering_angle, self.distance]


class SensorCar(SonicCar):
    """Die Klasse SensorCar fuegt die Funtkion des IR-Sensors zur SonicCar-Klasse hinzu

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
    """

    def __init__(self):
        super().__init__()
        self.ir = bk.Infrared()
        self._ir_sensor_analog = self.ir.read_analog()

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        self._ir_sensors = self.ir.read_analog()
        return self._ir_sensors

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten

        Returns:
            tuple: speed, direction, steering_angle, distance, ir_sensors
        """
        return [
            self._speed,
            self._direction,
            self._steering_angle,
            self.distance,
            self.ir_sensor_analog,
        ]


def main():
    print("PiCar als main ausgefuehrt")


if __name__ == "__main__":
    main()
