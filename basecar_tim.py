import basisklassen as bk


class BaseCar(object):


    def __init__(self):
        self._fw = bk.Front_Wheels()
        self._bw = bk.Back_Wheels()
        # self.speed = 0
        self.steering_angle = 90
        self.direction = 1

    def drive(self, v, dir):
        self.speed = v
        self.direction = dir

    def stop(self):
        self._bw.stop()

    @property
    def speed(self):
        return self._bw.speed

    @speed.setter
    def speed(self, v):
        self._bw.speed = v

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = self._fw.turn(angle)
        # self._fw.turn(angle)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, dir):
        self._direction = -1 if dir==-1 else 0 if dir==0 else 1
        self.stop() if dir==0 else self._bw.backward() if dir==-1 else self._bw.forward()
        #self._bw.backward() if dir==-1 else self._bw.forward()

    

