from curses.ascii import isdigit

from pyparsing import java_style_comment
import PiCar
import time
import sys

myCar = PiCar.SensorCar()


def driveCar(speed, direction, angle, duration):
    i = 0
    while i < (10 * duration):
        myCar.steering_angle = angle
        myCar.drive(speed, direction)
        time.sleep(0.1)
        i += 1
    myCar.stop()


def fahrparcour(pos):
    if pos == 1:
        print("Fahrparcours 1 gewaehlt:")
        print("3 Sekunden gerade vor")
        
        driveCar(30, 1, 0, 3)
        print("eine Sekunde Pause")
        driveCar(0, 0, 0, 1)
        print("3 Sekunden gerade zurueck")
        driveCar(30, -1, 0, 3)
        myCar.stop()
        print()

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

    elif pos == 7:
        print("Fahrparcours 7 gewaehlt:")
        print("gerade zuruecksetzen")
        driveCar(50, -1, 0, 2)
        myCar.stop()
        print()

    elif pos == 8:
        print("Datenaufzeichnung IR Sensoren")
        myCar.stop()
        input("Taste für start")
        i = 0
        while i < 200:
            myCar.drive_data
            time.sleep(0.05)
            i += 1
        print()

    else:
        print("Fahrparcours", pos, "nicht bekannt!")


def main():
    use_logger = False
    while True:
        print("Test des PiCar:")
        user_in = input("Sollen die Daten aufgezeichnet werden (j/n)?: ")
        if user_in.lower() == "j":
            use_logger = True
        else:
            use_logger = False
        user_in = input(
            """Fahrparcours Auswahl: 
                1 = vor / zurueck
                2 = Kurvenfahrt
                3 = vor bis Hindernis
                4 = Erkundungsfahrt
                5 = aufgezeichnete Fahrt rueckwarts
                7 = gerade zuruecksetzen
                8 = Datenaufzeichnung IR Sensor
                "x" = abbrechen
                "q" = beenden 
                Bitte waehlen: """
        )
        if isdigit(user_in):
            if use_logger == True:
                myCar.logger_start()
            fahrparcour(int(user_in))
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
