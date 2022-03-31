import basisklassen
import numpy as np
from curses.ascii import isdigit


from datetime import datetime
import os, json, time


angle_from_sensor = {
    0: 100,
    1: -40,
    3: -32,
    2: -23,
    7: -23,
    6: -10,
    4: 0,
    14: 0,
    12: 10,
    8: 23,
    28: 23,
    24: 32,
    16: 40,
    31: 100,
}
lookup = np.array([1, 2, 4, 8, 16])
fp_allowed = False

STEERINGE_ANGLE_MAX = 45
IR_MARK = 0.7


class Datenlogger:
    """Datenlogger Klasse
    speichert übergebene Tupels oder Listen mit Angabe des Zeitdeltas seid Start der Aufzeichnung in ein json-File
    """

    def __init__(self, log_file_path=None):
        """Zielverzeichnis fuer Logfiles kann beim Init mit uebergeben werden
            Wenn der Ordner nicht existiert wird er erzeugt

        Args:
            log_file_path (_type_, optional): Angabe des Zielordners. Defaults to None.
        """
        self._log_file = {}
        self._log_data = []
        self._start_timestamp = 0
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """starten des Loggers"""
        print("Logger gestartet")
        self._logger_running = True
        self._start_timestamp = time.time()
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Daten an den Logger senden

        Args:
            data (list): ein Element (Liste) wird an den Logger uebergeben
        """
        if self._logger_running:
            ts = round((time.time() - self._start_timestamp), 2)
            self._log_data.append([ts] + data)

    def save(self):
        """speichert die uebergebenen Daten"""
        if self._logger_running and (len(self._log_data) > 0):
            self._logger_running = False
            self._log_file["data"] = self._log_data
            self._log_file["ende"] = str(datetime.now()).partition(".")[0]
            filename = self._log_file.get("start").partition(".")[0]
            filename = (
                filename.replace("-", "").replace(":", "").replace(" ", "_")
                + "_drive.log"
            )
            if self._log_file_path != None:
                logfile = os.path.join(self._log_file_path, filename)
                if not os.path.isdir(self._log_file_path):
                    os.mkdir(self._log_file_path)
            else:
                logfile = filename
            with open(logfile, "w") as f:
                json.dump(self._log_data, f)
            self._log_file.clear()
            self._log_data.clear()
            print("Log-File saved to:", logfile)


def driveCar(car, speed, direction, angle, duration):
    i = 0
    while i < (10 * duration):
        car.steering_angle = angle
        car.drive(speed, direction)
        car.drive_data
        time.sleep(0.1)
        i += 1
    car.stop()


def fahrparcours_stop():
    global fp_allowed
    fp_allowed = False


def fahrparcour(car, pos):
    global fp_allowed
    fp_allowed = True
    if pos == 1:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        counter = 0
        state = 0
        while fp_allowed:
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
        print("Fahrparcours 2 gewaehlt:")
        print("2 Sekunden gerade vor")
        driveCar(car, 40, 1, 0, 2)
        print("8 Sekunden vorwarts links herum")
        driveCar(car, 45, 1, -45, 8)
        print("1 Sekunde Pause")
        driveCar(car, 0, 0, 0, 1)
        print("8 Sekunden rueckwarts links herum")
        driveCar(car, 45, -1, -45, 8)
        print("2 Sekunden gerade zurueck")
        driveCar(car, 40, -1, 0, 2)
        car.stop()
        print()

    elif pos == 3:
        print("Fahrparcours 3 gewaehlt:")
        print("gerade vor bis Abstand < x")
        max_time = 200
        drive_time = 0
        distance = car.drive_data[3]
        while fp_allowed:
            while (distance > 20 or distance < 5) and drive_time < max_time:
                car.steering_angle = 0
                car.drive(40, 1)
                time.sleep(0.1)
                distance = car.drive_data[3]
                print("Abstand:", distance)
                drive_time += 1
            car.stop()
        car.stop()

    elif pos == 4:
        print("Erkundungsfahrt:")
        max_time = 1000  # 100s
        drive_time = 0
        while fp_allowed:
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
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            car_data = car.drive_data
            ir_sens = car_data[4:9]
            st_angle = car.angle_from_ir()

            if st_angle == 100:
                print("STOP gefunden")
                if not ignore_stop:
                    break
            elif st_angle == 101:
                print("invalid result")
            else:
                car.steering_angle = st_angle
            car.drive(speed_soll, 1)
            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 6:
        print("Line Follower enge Kurve")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        last_angle = 0
        reverse = 0
        time_reverse = 0.6  # max. Zeit für Rückwärtsfahrt
        counter_reverse = time_reverse / time_period
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            st_angle = car.angle_from_ir()
            if not reverse:
                car_data = car.drive_data
                if st_angle == 100:
                    if abs(last_angle) >= 35:  # war ausserhalb des Bereichs
                        reverse = 1
                        counter_reverse = time_reverse / time_period
                        car.drive(0, 0)
                    else:
                        print("STOP gefunden")
                        if not ignore_stop:
                            break
                elif st_angle == 101:
                    print("invalid result")
                else:
                    car.steering_angle = st_angle
                    car.drive(speed_soll, 1)
                    last_angle = st_angle

            else:  # Rückwärtsfahrt
                if counter_reverse > 0:
                    counter_reverse -= 1
                    car.steering_angle = 0 - last_angle
                    car.drive(30, -1)
                    if abs(st_angle) < 40:  # Linie wieder unter Mitte des PiCar
                        car.drive(0, 0)
                        reverse = 0
                else:
                    car.drive(0, 0)
                    reverse = 0

            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 7:
        print("Line Follower mit US")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 0.25 / time_period
        last_angle = 0
        reverse = 0
        time_reverse = 0.6  # max. Zeit für Rückwärtsfahrt
        us_distance = 150
        counter_reverse = time_reverse / time_period
        while counter_stop < (time_run / time_period) and fp_allowed:
            if ignore_stop > 0:
                ignore_stop -= 1
            car_data = car.drive_data
            us_distance = car_data[3]
            st_angle = car.angle_from_ir()
            if not reverse:
                if us_distance < 20 and us_distance > 0:
                    car.stop()
                    print("US-Distanz zu gering --> STOP")
                    break
                if st_angle == 100:
                    if abs(last_angle) >= 35:  # war ausserhalb des Bereichs
                        reverse = 1
                        counter_reverse = time_reverse / time_period
                        car.drive(0, 0)
                    else:
                        print("STOP gefunden")
                        if not ignore_stop:
                            break
                elif st_angle == 101:
                    print("invalid result")
                else:
                    car.steering_angle = st_angle
                    car.drive(speed_soll, 1)
                    last_angle = st_angle

            else:  # Rückwärtsfahrt
                if counter_reverse > 0:
                    counter_reverse -= 1
                    car.steering_angle = 0 - last_angle
                    car.drive(30, -1)
                    if abs(st_angle) < 40:  # Linie wieder unter Mitte des PiCar
                        car.drive(0, 0)
                        reverse = 0
                else:
                    car.drive(0, 0)
                    reverse = 0

            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    elif pos == 8:
        i = 0
        counts = 0
        print("Datenaufzeichnung IR Sensoren")
        car.stop()
        duration = 3  # Sekunden
        mps = 10
        user_in = input("Messungen pro Sekunde:")
        try:
            mps = int(user_in)
        except:
            print("das war keine Zahl!")

        user_in = input("Messdauer in Sekunden:")
        try:
            duration = int(user_in)
        except:
            print("das war keine Zahl!")
        counts = mps * duration
        while i < counts and fp_allowed:
            a = car.drive_data
            print("IR-Sensors:", a[4:10], "US-Sensor:", a[3])
            time.sleep(1 / mps)
            i += 1
        print()

    elif pos == 9:
        print("Fahrparcours 9 gewaehlt:")
        print("gerade zuruecksetzen")
        driveCar(50, -1, 0, 2)
        car.stop()
        print()

    else:
        print("Fahrparcours", pos, "nicht bekannt!")
    car.us.stop()


class BaseCar:
    def __init__(self):
        self._steering_angle = 0
        self._speed = 0
        self._direction = 1
        with open("config.json", "r") as f:
            data = json.load(f)
            turning_offset = data.get("turning_offset")
            forward_A = data.get("forward_A")
            forward_B = data.get("forward_B")
            self._log_file_path = data.get("log_file_path")
            if self._log_file_path == None:
                self._log_file_path = "Folder"
            ir_calib = data.get("ir_calib")
            if ir_calib != None:
                self._ir_calib = ir_calib

        self.fw = basisklassen.Front_Wheels(turning_offset=turning_offset)
        self.bw = basisklassen.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self._dl = Datenlogger(log_file_path=self._log_file_path)

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
        fahrparcours_stop()

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
            self._steering_angle = 0 - STEERINGE_ANGLE_MAX
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
        self._us_distance = 0

    @property
    def distance(self):
        self._us_distance = self.us.distance()
        if self._us_distance > 150:  # Wert nicht relevant
            self._us_distance = -5
        return self._us_distance

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

    def __init__(self, filter_deepth: int = 2):
        super().__init__()
        self.ir = basisklassen.Infrared()
        self._ir_sensors = self.ir.read_analog()
        self._steering_soll = [0] * filter_deepth
        self._ir_calib = None
        with open("config.json", "r") as f:
            data = json.load(f)
            ir_calib = data.get("ir_calib")
            if ir_calib != None:
                self._ir_calib = ir_calib
            else:
                self._ir_calib = [1, 1, 1, 1, 1]

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        # self._ir_sensors = self.ir.read_analog()
        self._ir_sensors = (
            (self.ir.get_average(2) * np.array(self._ir_calib)).round(2).tolist()
        )
        return self._ir_sensors

    def calibrate_ir_sensors(self):
        while True:
            input("Sensoren auf hellem Untergrund platzieren, dann Taste drücken")
            a = self.ir.get_average(100)
            print("Messergebnis:", a)
            user_in = input("Ergebnis verwenden? (j/n/q)")
            if user_in == "n":
                print("Neue Messung")
            elif user_in == "j":
                messung = np.array(a)
                ir_calib = messung.mean() / messung
                self._ir_calib = ir_calib.round(4)
                print("Kalibrierwerte:", self._ir_calib)
                data = {}
                try:
                    with open("config.json", "r") as f:
                        data = json.load(f)
                except:
                    print("File error read")
                data["ir_calib"] = self._ir_calib.tolist()
                try:
                    with open("config.json", "w") as f:
                        json.dump(data, f)
                except:
                    print("File error write")
                break
            else:
                print("Abbruch durch Beutzer")
                break

        print("IR Kalibrierung beendet")

    def angle_from_ir(self):
        """berechnet den Soll-Lenkeinschlag damit das Fahrzeug der Linie folgen kann

        Returns:
            int: Soll-Lenkeinschlag (100 bedeutet STOP)
        """
        # Lookup-Table für mögliche Sensor-Werte
        ir_data = np.array(self.ir_sensor_analog)
        compValue = IR_MARK * ir_data.max()
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
            return 101

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
        user_in = input(
            "Sollen die Daten aufgezeichnet werden (j/n/q/) (c für IR Calib)?: "
        )
        if user_in.lower() == "j":
            use_logger = True
        else:
            use_logger = False
        if user_in.lower() == "q":
            break
        if user_in == "c":
            myCar.calibrate_ir_sensors()
            next
        user_in = input(
            """Fahrparcours Auswahl: 
                1 = vor / zurueck
                2 = Kurvenfahrt
                3 = vor bis Hindernis
                4 = Erkundungsfahrt
                5 = LineFollower
                6 = LineFollower enge Kurve
                7 = LineFollower mit US
                8 = Sensor-Test
                9 = gerade zuruecksetzen
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
