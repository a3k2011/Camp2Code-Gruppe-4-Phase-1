import basisklassen
import time

class BaseCar:
    def __init__(self):
        self.steering_angle = 0
        self.speed = 0
        self.direction = 1
        self.fw = basisklassen.Front_Wheels()
        self.bw = basisklassen.Back_Wheels()
    
    def drive(self, geschwindigkeit, lenkwinkel):
        self.fw.turn(lenkwinkel)
        self.bw.speed = geschwindigkeit
        if self.direction == 1:
            self.bw.forward()
        else:
            self.bw.backward()
        
    def stop(self):
        self.bw.stop()
        
#Main

car1 = BaseCar()
car1.drive(50, 45)
time.sleep(1)
car1.stop()
        




