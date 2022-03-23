import basecarhs
import time

c1 = basecarhs.BaseCar()
#c1.steering_angle = 45
c1.drive(100, 1)
time.sleep(2)
c1.drive(50, -1)
time.sleep(3)
#c1.steering_angle = 90
#time.sleep(2)
c1.stop()