'''
    Diese Datei enthaelt die Fahrparcours.
'''
import time
import datenlogger as DL
from cmath import log
from datetime import datetime
import os, json

def fahrparcour1(bc, v=50):

    # Vorwaerts 3sec
    bc.drive(v, 1)
    time.sleep(3)

    # Stand 1sec
    bc.stop()
    time.sleep(1)

    # Rueckwaerts 3sec
    bc.drive(v, -1)
    time.sleep(3)

    #Ende
    bc.stop()

def fahrparcour2(bc, v=50, listSA=None):

    if listSA == None:
        listSA =[50,130]

    for sa in listSA:
        # Vorwaerts 1sec gerade
        bc.steering_angle = 90
        bc.drive(v, 1)
        time.sleep(1)

        # Vorwaerts 8sec Max Lenkwinkel 
        bc.steering_angle = sa
        time.sleep(8)

        # Stoppen
        bc.stop()

        # Rueckwaerts 8sec Max Lenkwinkel
        bc.drive(v, -1)
        time.sleep(8)

        # Rueckwaerts 1sec gerade
        bc.steering_angle = 90
        time.sleep(1)

        # Ende
        bc.stop()

def fahrparcour3(sc, v=50):
    
    # Vorwaerts bis Hindernis
    sc.drive(v, 1)

def fahrparcour4(sc, v=50):

    dl = DL.Datenlogger(log_file_path="Logger")
    dl.start()
    # Erkundungstour X Runden
    for i in range(1):

        sc.drive(v, 1)

        while (sc.distance - sc.US_OFFSET) > 0:
            dl.append(sc.getFahrdaten())
            time.sleep(0.1)
        
        sc.stop()

        sc.rangieren()

    sc.stop()

    dl.save()