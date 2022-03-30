from curses.ascii import isdigit
import PiCar_work as PiCar
import time
import sys
import numpy as np


def driveCar(car, speed, direction, angle, duration):
    i = 0
    while i < (10 * duration):
        car.steering_angle = angle
        car.drive(speed, direction)
        time.sleep(0.1)
        i += 1
    car.stop()


def fahrparcour(car: PiCar.SensorCar, pos):
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
        car.stop()
        input("Taste für start")
        speed_limit = 100
        speed_soll = 40
        counter_stop = 0
        time_period = 0.01
        time_run = 25  # Sekunden
        ignore_stop = 1 / time_period
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


def getParcoursList():
    return [
        {"label": "FP 1, vor-zurück", "value": 1},
        {"label": "FP 2, im Kreis", "value": 2},
        {"label": "FP 3, US-Testfahrt", "value": 3},
        {"label": "FP 4, LineFollower", "value": 4},
        {
            "label": "FP 5: LineFollower",
            "value": 5,
        },
    ]


def main():
    myCar = PiCar.SensorCar(filter_deepth=4)
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
