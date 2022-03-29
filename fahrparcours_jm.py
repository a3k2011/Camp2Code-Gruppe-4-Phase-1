from curses.ascii import isdigit
from socket import IPPROTO_UDP

import PiCar
import time
import sys
import numpy as np
import pprint
import queue

myCar = PiCar.SensorCar()

steering_soll = [0] * 5


def angle_from_ir(ir_data: list):
    global steering_soll
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
                ir_result = -45
            if sd[4] and sd[3]:  # viel nach links
                ir_result = -30
            if sd[3]:  # etwas nach links
                ir_result = -20
            if sd[3] and sd[2]:  # etwas nach links
                ir_result = -10
            if sd[0]:  # stark nach rechts
                ir_result = 45
            if sd[0] and sd[1]:  #
                ir_result = 30
            if sd[1]:  # etwas nach links
                ir_result = 20
            if sd[1] and sd[2]:  # etwas nach links
                ir_result = 10

    if ir_result < 100:
        steering_soll = steering_soll[1:]
        steering_soll.append(ir_result)
        ir_out = np.mean(steering_soll)
    else:
        ir_out = 100
    print(ir_data, "-->", ir_result, "-", ir_out)
    return ir_out


def driveCar(speed, direction, angle, duration):
    i = 0
    while i < (10 * duration):
        myCar.steering_angle = angle
        myCar.drive(speed, direction)
        time.sleep(0.1)
        i += 1
    myCar.stop()


def fahrparcour(car: PiCar.SensorCar, pos):
    if pos == 1:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        counter = 0
        state = 0
        while True:
            car.read_drive_data()
            if state == 0:
                counter = 30
                car.drive(40, 1)
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
                    state = 3
            elif state == 3:
                if counter > 0:
                    counter -= 1
                else:
                    counter = 0
                    car.drive(0, 0)
                    break
            time.sleep(0.1)

        """ driveCar(30, 1, 0, 3)
        print("eine Sekunde Pause")
        driveCar(0, 0, 0, 1)
        print("3 Sekunden gerade zurueck")
        driveCar(30, -1, 0, 3)
        myCar.stop()
        print()
        """

    elif pos == 2:
        print("Fahrparcours 2 gewaehlt:")
        print("2 Sekunden gerade vor")
        driveCar(40, 1, 0, 2)
        print("8 Sekunden vorwarts links herum")
        driveCar(45, 1, -45, 8)
        print("1 Sekunde Pause")
        driveCar(0, 0, 0, 1)
        print("8 Sekunden rueckwarts links herum")
        driveCar(45, -1, -45, 8)
        print("2 Sekunden gerade zurueck")
        driveCar(40, -1, 0, 2)
        myCar.stop()
        print()

    elif pos == 3:
        print("Fahrparcours 3 gewaehlt:")
        print("gerade vor bis Abstand < x")
        max_time = 200
        drive_time = 0
        distance = myCar.distance
        while (distance > 20 or distance < 5) and drive_time < max_time:
            myCar.steering_angle = 0
            myCar.drive(40, 1)
            time.sleep(0.1)
            distance = myCar.distance
            print("Abstand:", distance)
            drive_time += 1
        myCar.stop()

    elif pos == 4:
        print("Erkundungsfahrt:")
        max_time = 1000  # 100s
        drive_time = 0

        for i in range(10):
            print("Fahrt:", i + 1)
            distance = myCar.distance
            while (distance > 25 or distance < 1) and drive_time < max_time:
                myCar.steering_angle = 0
                myCar.drive(40, 1)
                time.sleep(0.1)
                distance = myCar.distance
                print("Abstand:", distance)
                drive_time += 1
            myCar.stop()
            print("zuruecksetzen")
            myCar.steering_angle = 45
            myCar.drive(40, -1)
            time.sleep(2)
            myCar.stop()
            myCar.steering_angle = 0

        myCar.stop()

    elif pos == 5:
        print("Fahrparcours 5 gewaehlt:")
        print("Folge der Linie")
        distance = car.read_drive_data()[-1]
        while (distance > 25 or distance < 1) and drive_time < max_time:
            myCar.steering_angle = 0
            myCar.drive(40, 1)
            time.sleep(0.1)
            distance = myCar.distance
            print("Abstand:", distance)
            drive_time += 1
        myCar.stop()
        print()

    elif pos == 7:
        print("Fahrparcours 7 gewaehlt:")
        print("gerade zuruecksetzen")
        driveCar(50, -1, 0, 2)
        myCar.stop()
        print()

    elif pos == 8:
        print("Datenaufzeichnung IR Sensoren")
        car.stop()
        input("Taste für start")
        i = 0
        while i < 2000:
            myCar.get_drive_data()
            time.sleep(0.05)
            i += 1
        print()

    elif pos == 9:
        print("Check IR Funktion")
        car.stop()
        input("Taste für start")
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        while counter_stop < (time_run / time_period):
            car_data = car.read_drive_data()
            ir_sens = car_data[4:9]
            st_angle = angle_from_ir(ir_sens)
            if st_angle != 100:
                car.steering_angle = st_angle
            else:
                print("STOP gefunden")
                # break
            car.drive(40, 1)
            time.sleep(time_period)
            counter_stop += 1
        car.stop()
        car.steering_angle = 0
        print("Ende der Strecke")

    else:
        print("Fahrparcours", pos, "nicht bekannt!")


def main():
    myCar = PiCar.SensorCar()
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
                9 = Check IR-Funktion
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
