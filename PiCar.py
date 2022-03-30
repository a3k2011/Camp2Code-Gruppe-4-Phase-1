import basisklassen
import time
import json
import numpy as np
import datenlogger
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor


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


STEERINGE_ANGLE_MAX = 45


class BaseCar:

    LOG_FREQ = 0.1

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
                self._log_file_path = "Logger"
        self.fw = basisklassen.Front_Wheels(turning_offset=turning_offset)
        self.bw = basisklassen.Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self._active = False
        self._worker = None
        self._dl = None

    def startDriveMode(self):
        self._active = True
        self._dl = datenlogger.Datenlogger(log_file_path=self._log_file_path)
        self._worker = ThreadPoolExecutor(max_workers=5)
        self._worker.submit(self.dlWorker)

    def endDriveMode(self, waitingWorker=False):
        if waitingWorker:
            self._worker.shutdown(wait=True)
        else:
            self._worker.shutdown(wait=False)
        self._active = False
        self.stop()

    def dlWorker(self):
        self._dl.start()
        while self._active:
            self._dl.append(self.drive_data)
            time.sleep(self.LOG_FREQ)
        self._dl.save()

    @property
    def drive_data(self):
        return [self.speed, self.direction, self.steering_angle]

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

    def fp1(self, v=50):
        print("Fahrparcour 1 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        # Vorwaerts 3sec
        self.drive(v, 1)
        time.sleep(3)

        # Stillstand 1sec
        self.stop()
        time.sleep(1)

        # Rueckwaerts 3sec
        self.drive(v, -1)
        time.sleep(3)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        print("Fahrparcour 1 beendet.")

    def fp2(self, v=50):
        print("Fahrparcour 2 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        for sa in [(-STEERINGE_ANGLE_MAX + 5), (STEERINGE_ANGLE_MAX - 5)]:
            # Vorwaerts 1sec gerade
            self.steering_angle = 0
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
            self.steering_angle = 0
            time.sleep(1)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        print("Fahrparcour 2 beendet.")


class Sonic(BaseCar):

    US_FREQ = 0.05
    US_OFFSET = 25

    def __init__(self):
        super().__init__()
        self.us = basisklassen.Ultrasonic()
        self._distance = self.US_OFFSET + 1
        self._hindernis = False
        self._tmpspeed = None

    def startDriveMode(self):
        super().startDriveMode()
        self._worker.submit(self.usWorker)

    def usWorker(self):
        while self._active:
            if self._hindernis == False and not (self.distance - self.US_OFFSET) > 0:
                self._hindernis = True
            else:
                time.sleep(self.US_FREQ)

    def inputWorker(self):
        while self._active:
            inpUser = input("Fahrbefehl eingeben: ")
            dictBefehle = {
                "f": "self.direction = 1",
                "b": "self.direction = -1",
                "e": "self._active = False",
            }
            try:
                if inpUser in dictBefehle:
                    exec(dictBefehle[inpUser])
                elif type(int(inpUser)) and int(inpUser) >= 0 and int(inpUser) <= 100:
                    self.speed = int(inpUser)
                    self._tmpspeed = int(inpUser)
                else:
                    raise Exception
            except Exception:
                print("Kein gültiger Befehl oder gültige Geschwindigkeit!")
                continue

    def rangierenWorker(self):
        while self._active:
            if self._hindernis:

                self.drive(50, -1)
                self.steering_angle = -40

                cntTime = time.perf_counter()
                while (time.perf_counter() - cntTime) < 2.55:
                    time.sleep(0.1)

                self.steering_angle = 0
                self.drive(self._tmpspeed, 1)

                self._hindernis = False

    @property
    def distance(self):
        dist = self.us.distance()
        self._distance = dist if dist >= 0 else (self.US_OFFSET + 1)
        return self._distance

    @property
    def drive_data(self):
        return [self.speed, self.direction, self.steering_angle, self._distance]

    def usstop(self):
        self.us.stop()

    def fp3(self, v=50):
        print("Fahrparcour 3 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()

        # Starte die Fahrt
        self.steering_angle = 0
        self.drive(v, 1)
        while self._active and not self._hindernis:
            time.sleep(0.1)

        # Ende Drive Mode
        self.endDriveMode(waitingWorker=False)
        self.usstop()
        print("Fahrparcour 3 beendet.")

    def fp4(self, v=50):
        print("Fahrparcour 4 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()
        self._worker.submit(self.rangierenWorker)
        self._worker.submit(self.inputWorker)
        self._tmpspeed = v

        # Starte die Fahrt
        self.steering_angle = 0
        self.drive(v, 1)

        # Wartet auf Fertigstellung aller Threads
        self.endDriveMode(waitingWorker=True)

        # Ende Drive Mode
        self.usstop()
        print("Fahrparcour 4 beendet.")


class SensorCar(Sonic):
    """Die Klasse SensorCar fuegt die Funtkion des IR-Sensors zur SonicCar-Klasse hinzu

    Args:
        SonicCar (_type_): Erbt von der Klasse SonicCar
    """

    IF_FREQ = 0.05

    def __init__(self, filter_deepth: int = 5):
        super().__init__()
        self.ir = basisklassen.Infrared()
        self._ir_sensor_analog = self.ir.read_analog()
        self._ir_sensors = [20, 20, 10, 20, 20]
        self._line = True
        self._steering_soll = [0] * filter_deepth

    def startDriveMode(self):
        super().startDriveMode()
        self._worker.submit(self.ifWorker)

    def ifWorker(self):
        while self._active:
            self.ir_sensor_analog
            time.sleep(self.IF_FREQ)

    @property
    def ir_sensor_analog(self):
        """Ausgabe der Werte der IR-Sensoren

        Returns:
            list: Analogwerte der 5 IR-Sensoren
        """
        self._ir_sensors = self.ir.read_analog()
        # self._ir_sensors = self.ir.get_average(2)
        return self._ir_sensors

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
            self._distance,
        ]
        data += self._ir_sensors

        return data

    def lenkFunction(self):
        while self._active:
            ir_data = np.array(self._ir_sensors)
            print(ir_data)
            compValue = 0.6 * ir_data.max()
            print(compValue)
            sensor_digital = np.where(ir_data < compValue, 1, 0)
            print(sensor_digital)
            lookupValue = (lookup * sensor_digital).sum()
            print(lookupValue)
            ir_result = angle_from_sensor.get(lookupValue)
            if ir_result != None:
                print(ir_result)
                if ir_result < 100:
                    self._steering_soll = self._steering_soll[1:]
                    self._steering_soll.append(ir_result)
                    ir_out = np.mean(self._steering_soll)
                    self.steering_angle = ir_out
                else:
                    ir_out = 100
                    self._line = False
                    self._active = False
            else:
                print("IR-Wert unbekannt:", sensor_digital)

            time.sleep(self.IF_FREQ)

    def lineFunction(self):
        while self._active:
            std = np.std(self._ir_sensors)
            if std < 2.5 and std != 0:
                self._line = False
                self._active = False
            time.sleep(self.IF_FREQ)

    def fp5(self, v=50):
        print("Fahrparcour 5 gestartet.")
        # Starte Drive Mode
        self.startDriveMode()
        """
        Hier muss eine Reaktions-Funktion zum Worker submitted werden!
        Bsp: lenkFunction
        """
        self._worker.submit(self.lenkFunction)
        # self._worker.submit(self.inputWorker)

        # Starte die Fahrt
        self.steering_angle = 0
        self.drive(v, 1)

        # Wartet auf Fertigstellung aller Threads
        self.endDriveMode(waitingWorker=True)

        # Ende Drive Mode
        self.steering_angle = 0
        self.usstop()
        print("Fahrparcour 5 beendet.")

    def test_ir(self):
        for i in range(5):
            print(self._ir_sensor_analog)
            time.sleep(self.IF_FREQ)