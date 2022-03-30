import basisklassen
import time
import json
import numpy as np
import datenlogger
from curses.ascii import isdigit

angle_from_sensor = {
    0: 100,
    1: -40,
    3: -30,
    2: -20,
    7: -20,
    6: -10,
    4: 0,
    14: 0,
    12: 10,
    8: 20,
    28: 20,
    24: 30,
    16: 40,
    31: 100,
}
lookup = np.array([1, 2, 4, 8, 16])

STEERINGE_ANGLE_MAX = 45


def driveCar(car, speed, direction, angle, duration):
    i = 0
    while i < (10 * duration):
        car.steering_angle = angle
        car.drive(speed, direction)
        time.sleep(0.1)
        i += 1
    car.stop()


def fahrparcour(car, pos):
    if pos == 1:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        counter = 0
        state = 0
        while True:
            car.drive_data
            if state == 0:
                counter = 30
                car.drive(40, 1)
                car.steering_angle = 0
                state = 1
            elif state == 1:
                if counter > 0:
                    counter -= 1
                else:
                    print("eine Sekunde Pause")
                    counter = 10
                    car.drive(0, 0)
                    state = 2
            elif state == 2:
                if counter > 0:
                    counter -= 1
                else:
                    print("3 Sekunden gerade zurueck")
                    counter = 30
                    car.drive(40, -1)
                    car.steering_angle = 0
                    state = 3
            elif state == 3:
                if counter > 0:
                    counter -= 1
                else:
                    counter = 0
                    car.drive(0, 0)
                    break
            time.sleep(0.1)

    elif pos == 2:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        counter = 0
        state = 0
        while True:
            car.drive_data
            if state == 0:
                counter = 30
                car.drive(40, 1)
                car.steering_angle = 0
                state = 1
            elif state == 1:
                if counter > 0:
                    counter -= 1
                else:
                    print("eine Sekunde Pause")
                    counter = 10
                    car.drive(0, 0)
                    state = 2
            elif state == 2:
                if counter > 0:
                    counter -= 1
                else:
                    print("3 Sekunden gerade zurueck")
                    counter = 30
                    car.drive(40, -1)
                    car.steering_angle = 0
                    state = 3
            elif state == 3:
                if counter > 0:
                    counter -= 1
                else:
                    counter = 0
                    car.drive(0, 0)
                    break
            time.sleep(0.1)
        # print("Fahrparcours 2 gewaehlt:")
        # print("2 Sekunden gerade vor")
        # driveCar(car, 40, 1, 0, 2)
        # print("8 Sekunden vorwarts links herum")
        # driveCar(car, 45, 1, -45, 8)
        # print("1 Sekunde Pause")
        # driveCar(car, 0, 0, 0, 1)
        # print("8 Sekunden rueckwarts links herum")
        # driveCar(car, 45, -1, -45, 8)
        # print("2 Sekunden gerade zurueck")
        # driveCar(car, 40, -1, 0, 2)
        # car.stop()
        print()

    elif pos == 3:
        print("Fahrparcours 3 gewaehlt:")
        print("gerade vor bis Abstand < x")
        max_time = 200
        drive_time = 0
        distance = car.drive_data[3]
        while (distance > 20 or distance < 5) and drive_time < max_time:
            car.steering_angle = 0
            car.drive(40, 1)
            time.sleep(0.1)
            distance = car.drive_data[3]
            print("Abstand:", distance)
            drive_time += 1
        car.stop()

    elif pos == 4:
        print("Erkundungsfahrt:")
        max_time = 1000  # 100s
        drive_time = 0

        for i in range(10):
            print("Fahrt:", i + 1)
            distance = car.drive_data[3]
            while (distance > 25 or distance < 1) and drive_time < max_time:
                car.steering_angle = 0
                car.drive(40, 1)
                time.sleep(0.1)
                distance = car.drive_data[3]
                print("Abstand:", distance)
                drive_time += 1
            car.stop()
            print("zuruecksetzen")
            car.steering_angle = 45
            car.drive(40, -1)
            time.sleep(2)
            car.stop()
            car.steering_angle = 0
        car.stop()

    elif pos == 5:
        print("Line Follower")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        while counter_stop < (time_run / time_period):
            if ignore_stop > 0:
                ignore_stop -= 1
            car_data = car.drive_data
            ir_sens = car_data[4:9]
            st_angle = car.angle_from_ir()

            if st_angle != 100:
                car.steering_angle = st_angle
            else:
                print("STOP gefunden")
                if not ignore_stop:
                    break
            speed_limit = int(112 - (abs(st_angle) * 2.25))
            print("speed limit: ", speed_limit)
            speed_drive = speed_soll
            # if speed_drive > speed_limit:
            #     speed_drive = speed_limit
            car.drive(speed_drive, 1)
            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 7:
        print("Fahrparcours 7 gewaehlt:")
        print("gerade zuruecksetzen")
        driveCar(50, -1, 0, 2)
        car.stop()
        print()

    elif pos == 8:
        print("Datenaufzeichnung IR Sensoren")
        car.stop()
        input("Taste für start")
        i = 0
        while i < 100:
            a = car.drive_data
            print("IR-Sensors:", a[-5:])
            time.sleep(0.1)
            i += 1
        print()

    else:
        print("Fahrparcours", pos, "nicht bekannt!")


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
            self._log_file_path = data.get("log_file_path")
            if self._log_file_path == None:
                self._log_file_path = "Folder"
        self.fw = basisklassen.Front_Wheels(turning_offset=turning_offset)
        self.bw = basisklassen.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self._dl = datenlogger.Datenlogger(log_file_path=self._log_file_path)

    def logger_start(self):
        self._dl.start()

    def logger_log(self, data):
        self._dl.append(data)

    def logger_save(self):
        self._dl.save()

    def start_parcours(self, number):
        self.logger_start()
        fahrparcour(self, number)
        self.logger_save()

    def stop_parcours(self):
        print("Emergency STOP")

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
            self._steering_angle = STEERINGE_ANGLE_MAX
        elif value < (0 - STEERINGE_ANGLE_MAX):
            self._steering_angle = STEERINGE_ANGLE_MAX
        else:
            self._steering_angle = value
        self.fw.turn(90 + self._steering_angle)

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
        # self._ir_sensors = self.ir.read_analog()
        self._ir_sensors = self.ir.get_average(2)
        return self._ir_sensors

    def angle_from_ir(self):
        """berechnet den Soll-Lenkeinschlag damit das Fahrzeug der Linie folgen kann

        Returns:
            int: Soll-Lenkeinschlag (100 bedeutet STOP)
        """
        # Lookup-Table für mögliche Sensor-Werte
        ir_data = np.array(self.ir_sensor_analog)
        compValue = 0.6 * ir_data.max()
        sd = np.where(ir_data < compValue, 1, 0)
        lookupValue = (lookup * sd).sum()
        ir_result = angle_from_sensor.get(lookupValue)
        if ir_result != None:
            if ir_result < 100:
                self._steering_soll = self._steering_soll[1:]
                self._steering_soll.append(ir_result)
                ir_out = np.mean(self._steering_soll)
            else:
                ir_out = 100
            return ir_out
        else:
            return 100

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


def main():
    myCar = SensorCar(filter_deepth=4)
    myCar.stop()
    myCar.steering_angle = 0
    use_logger = False
    while True:
        print("Test des PiCar:")
        user_in = input("Sollen die Daten aufgezeichnet werden (j/n/q)?: ")
        if user_in.lower() == "j":
            use_logger = True
        else:
            use_logger = False
        if user_in.lower() == "q":
            break
        user_in = input(
            """Fahrparcours Auswahl: 
                1 = vor / zurueck
                2 = Kurvenfahrt
                3 = vor bis Hindernis
                4 = Erkundungsfahrt
                5 = LineFollower
                7 = gerade zuruecksetzen
                8 = Datenaufzeichnung IR Sensor
                "x" = abbrechen
                "q" = beenden 
                Bitte waehlen: """
        )
        if isdigit(user_in):
            if use_logger == True:
                myCar.logger_start()
            fahrparcour(myCar, int(user_in))
            myCar.logger_save()
            print("Parcours beendet")
        else:
            if user_in.lower() == "x":
                pass
            elif user_in.lower() == "q":
                print("Programm beendet")
                break
            else:
                print("Das habe ich nicht verstanden!")


if __name__ == "__main__":
    main()
