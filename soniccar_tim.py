import time
import os
from datetime import datetime
import basecar_tim as BCT
from basisklassen import Ultrasonic


class SonicCar(BCT.BaseCar):

    US_OFFSET = 10

    def __init__(self):
        super().__init__()
        self._us = Ultrasonic()
        self._distance = 999

    def drive(self, v, dir):
        self.speed = v
        self.direction = dir

        logFilename = "CarLog-" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        while ((self.distance if self._distance > 0 else 999) - SonicCar.US_OFFSET) > 0:
            
            self.writeLoggingFile(logFilename)
            time.sleep(0.025)

        self.stop()
 
    @property 
    def distance(self):
        self._distance = self._us.distance()
        return self._distance

    def getFahrdaten(self):
        return (str(self.speed), str(self.steering_angle), str(self.direction), str(self._distance))

    def writeLoggingFile(self, logFilename):
        
        path = os.path.join("Logger", logFilename)
        logTS = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
        v, sa, dir, dist = self.getFahrdaten()
        logContent = logTS + " - " + v + "% - " + sa + "° - " + dir + " - " + dist + "cm\n"

        try:
            with open(path, "a") as logs: 
                logs.write(logContent)
        except Exception:
            print("Die Messung konnte nicht geloggt werden!")
    



