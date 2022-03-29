import basisklassen
import time
import json
import numpy as np

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
            self._steering_angle = 90 + STEERINGE_ANGLE_MAX
        elif value < (0 - STEERINGE_ANGLE_MAX):
            self._steering_angle = 90 - STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = 90 + value
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


class Sonic(BaseCar):
    def __init__(self):
        super().__init__()
        self.us = basisklassen.Ultrasonic()

    @property
    def distance(self):
        return self.us.distance()

    @property
    def drive_data(self):
        return [self.speed, self.direction, self.steering_angle, self.distance]

    def usstop(self):
        self.us.stop()


class SensorCar(Sonic):
    """Die Klasse SensorCar fuegt die Funtkion des IR-Sensors zur SonicCar-Klasse hinzu

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
    """

    def __init__(self, filter_deepth: int = 5):
        super().__init__()
        self.ir = basisklassen.Infrared()
        self._ir_sensor_analog = self.ir.read_analog()
        self._steering_soll = [0] * filter_deepth

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        self._ir_sensors = self.ir.read_analog()
        return self._ir_sensors

    def angle_from_ir(self):
        """berechnet den Soll-Lenkeinschlag damit das Fahrzeug der Linie folgen kann

        Returns:
            int: Soll-Lenkeinschlag (100 bedeutet STOP)
        """
        ir_data = self.ir_sensor_analog
        sd = [0, 0, 0, 0, 0]
        ir_result = 0
        for i in range(5):
            if ir_data[i] < (0.6 * np.max(ir_data)):
                sd[i] = 1
            else:
                sd[i] = 0
        if np.mean(ir_data) < 15:  # alles dunkel,
            ir_result = 100  # stopp-Bedingung
        else:
            if np.sum(sd) == 5:  # alle low -> nicht möglich
                ir_result = 100
            elif np.sum(sd) == 0:
                ir_result = 100
            else:
                if sd[4]:  # stark nach links
                    ir_result = -40
                if sd[4] and sd[3]:  # viel nach links
                    ir_result = -30
                if sd[3]:  # etwas nach links
                    ir_result = -20
                if sd[3] and sd[2]:  # etwas nach links
                    ir_result = -10
                if sd[0]:  # stark nach rechts
                    ir_result = 40
                if sd[0] and sd[1]:  #
                    ir_result = 30
                if sd[1]:  # etwas nach links
                    ir_result = 20
                if sd[1] and sd[2]:  # etwas nach links
                    ir_result = 10

        if ir_result < 100:
            self._steering_soll = self._steering_soll[1:]
            self._steering_soll.append(ir_result)
            ir_out = np.mean(self._steering_soll)
        else:
            ir_out = 100
        return ir_out

    @property
    def drive_data(self):
        """Ausgabe der Fahrdaten

        Returns:
            list: speed, direction, steering_angle, distance, ir_sensors
        """
        data = [
            self._speed,
            self._direction,
            self._steering_angle,
            self.distance,
        ] + self.ir_sensor_analog

        self.logger_log(data)
        return data

