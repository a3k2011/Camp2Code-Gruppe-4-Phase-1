import PiCar
import time
import datenlogger
import random

def distance_check(dist):
    if (dist > 20 or dist < 0): 
        dist = True
    else: 
        dist = False
    return dist

def fahrparcours1():
    print("Fahrparcours 1 startet")
    car.drive(100, 1)
    time.sleep(2)
    car.drive(50, -1)
    time.sleep(3)
    #c1.steering_angle = 90
    #time.sleep(2)
    car.stop()

def fahrparcours2():
    print("Fahrparcours 2 startet")
    car.drive(100, 1)
    time.sleep(1)
    car.stop()
    
    for i in range(7):
        car.steering_angle = 20
        car.drive(60, 1)
        time.sleep(1)
    car.stop()
    
    for i in range(7):
        car.steering_angle = 20
        car.drive(60, -1)
        time.sleep(1)
    car.stop()
    
    car.steering_angle = 0
    car.drive(100, -1)
    time.sleep(1)
    car.stop()

def fahrparcours3():

    print("Fahrparcours 3 startet")
    car.drive(50,1)
    daten = car.drive_data
    while (daten[3] > 10 or daten[3] < 0):
        print(daten[3])
        logger.append(daten)
        time.sleep(0.05)
        daten = car.drive_data
    print(daten[3])
    car.stop()

def fahrparcours4():

    print("Fahrparcours 4 startet")
    zeit_start = time.time()
    zeit_delta = 0
    zeit_ereignis=0

    car.drive(50,1)
    car.steering_angle = 0
    
    while (zeit_delta < 20):
        daten = car.drive_data

        if (distance_check(daten[3]) == False):
            car.drive(50,-1)
            car.steering_angle = random.choice([30, -30])
            zeit_ereignis = time.time()
        
        if (time.time()-zeit_ereignis > 2):
            car.steering_angle = 0
            car.drive(50,1)
        
        logger.append(daten)
    
        zeit_delta = time.time()-zeit_start
        time.sleep(0.05)
    
    car.steering_angle = 0
    car.stop()


""" H A U P T P R O G R A M M """

car = PiCar.Sonic()
logger = datenlogger.Datenlogger(log_file_path="Logger")
logger.start()  #Logger starten

print()
parcours = input("Welcher Fahrparcours soll gestartet werden? ")
if parcours == "1": fahrparcours1()
elif parcours == "2": fahrparcours2()
elif parcours == "3": fahrparcours3()
elif parcours == "4": fahrparcours4()

else:
    print("falsche Eingabe")

logger.save()   #Logger beenden