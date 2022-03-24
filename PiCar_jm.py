"""
Grundfunktionen des PiCar
"""

import basisklassen as bk
import time
from datetime import datetime
import json
import os

STEERINGE_ANGLE_MAX = 45
DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = -1
SPEED_MAX = 100
SPEED_MIN = 0
LOGGER_START = "start"
LOGGER_APPEND = "append"
LOGGER_SAVE = "save"
LOG_SPEED = "speed"
LOG_DIR = "dir"
LOG_ANGLE = "angle"
LOG_US = "us"
LOG_IR = "ir"


class BaseCar:
    """Basis-Implementierung der Fahrzeug-Klasse fuer das Sunfounder PiCar"""

    def __repr__(self) -> str:
        return "Klasse BaseCar"

    def __init__(self):
        """Erzeugen der Klasse, laden der Config-Werte aus config.json"""
        self._log_file = {}
        self._log_data = []
        self._logger_running = False
        self._log_file_path = ""

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
        self._steering_angle = 0
        self._speed = 0
        self._direction = 0

    def Datenlogger(self, modus, *args):
        """Datenlogger fuer alle Fahraktionen
            Die Daten werden mit Timestamps gesichert und bei STOP des Loggers als json in ein Logfile gespeicher.
            Der Speicherort für das Logfile wird aus der config.json gelesen. Ist dort ncihts definiert wird das root-Verzeichnis genommen.

        Args:
            modus (str): Steuerung des Loggers (LOGGER_START, LOGGER_APPEND, LOGGER_STOP)
            *args (dict(s)):Hinzufuegen von Log-Daten als Dictionarys
        """
        if (modus == "start") and not self._logger_running:
            self._logger_running = True
            self._log_file["start"] = str(datetime.now()).partition(".")[0]
        elif modus == "append":
            app_time = str(datetime.now()).partition(".")[0]
            for arg in args:
                self._log_data.append({app_time: arg})
        elif (modus == "save") and self._logger_running:
            self._logger_running = False
            self._log_file["data"] = self._log_data
            self._log_file["ende"] = str(datetime.now()).partition(".")[0]
            filename = self._log_file.get("start").partition(".")[0]
            filename = (
                filename.replace("-", "_").replace(" ", "_").replace(":", "_")
                + "_drive.log"
            )
            if self._log_file_path != None:
                logfile = os.path.join(self._log_file_path, filename)
                if not os.path.isdir(self._log_file_path):
                    os.mkdir(self._log_file_path)
            else:
                logfile = filename
            with open(logfile, "w") as f:
                json.dump(self._log_file, f)
            self._log_file.clear()
            self._log_data.clear()
            print("Log-File saved to:", logfile)

    def drive(self, speed, direction):
        """Methode drive
        args:   speed (Geschwindigkeit in % von 0 bis 100)
                direction (Fahrtrichtung: 1=vor, 0=stop, -1=zurück)
        """
        self.Datenlogger(LOGGER_APPEND, {LOG_SPEED: speed}, {LOG_DIR: direction})
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
        self.Datenlogger(LOGGER_APPEND, {LOG_SPEED: 0}, {LOG_DIR: 0})
        self.direction = 0
        self.speed = 0
        self.bw.stop()
        print(
            "car stopped!!!",
            "Car dirves with",
            self._speed,
            "speed in direction",
            self._direction,
        )

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        """_summary_

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
        self.Datenlogger(LOGGER_APPEND, {LOG_ANGLE: self._steering_angle})

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


class SonicCar(BaseCar):
    """Die Klasse Sonic-Car fuegt die Funktion des Ultraschallsensors zu BaseCare hinzu

    Args:
        BaseCar (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.us = bk.Ultrasonic()

    @property
    def distance(self):
        """Methode distance() von SonicCar

        Returns:
            int: return des Abstands in cm
        """
        distance = self.us.distance()
        self.Datenlogger(LOGGER_APPEND, {LOG_US: distance})
        return distance

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten

        Returns:
            tuple: speed, direction, steering_angle, distance
        """
        return (self._speed, self._direction, self._steering_angle, self.distance)


class SensorCar(SonicCar):
    """Die Klasse SensorCar fuegt die Funtkion des IR-Sensors zur SonicCar-Klasse hinzu

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
    """

    def __init__(self):
        super().__init__()
        self.ir = bk.Infrared()

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        ir_sensors = self.ir.read_analog()
        self.Datenlogger(LOGGER_APPEND, {LOG_IR: ir_sensors})
        return ir_sensors


def main():
    myCar = SonicCar()
    myCar.Datenlogger(LOGGER_START)
    time.sleep(0.2)
    myCar.Datenlogger(LOGGER_APPEND, {LOG_ANGLE: 20})
    time.sleep(2)
    myCar.Datenlogger(LOGGER_APPEND, {LOG_SPEED: 40})
    time.sleep(1.2)
    myCar.Datenlogger(LOGGER_APPEND, {LOG_DIR: 1}, {"speed": 35})
    time.sleep(0.3)
    myCar.Datenlogger(LOGGER_APPEND, {LOG_US: 34})
    time.sleep(0.6)
    myCar.Datenlogger(LOGGER_APPEND, {LOG_IR: [23,21,34,67,76]})
    time.sleep(1.4)
    myCar.Datenlogger(LOGGER_SAVE)


if __name__ == "__main__":
    main()
