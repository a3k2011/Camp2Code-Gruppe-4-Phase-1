import os
import time
from datetime import datetime
import soniccar_tim as SCT
from basisklassen import Infrared


class InfraredCar(SCT.SonicCar):

    INF_FREQ = 0.1

    def __init__(self):
        super().__init__()
        self._inf = Infrared()
        self._analog = None

    @property
    def analog(self):
        analog = self._inf.read_analog()
        self._analog = analog
        return self._analog

    def getFahrdaten(self):
        return {'v': self.speed, 'sa': self.steering_angle, 'dir': self.direction, 'dist': self._distance, 'inf': [0,0,0,0,0] if self._analog is None else self._analog}

    def infFunction(self):
        while self._active:
            self.analog
            time.sleep(self.INF_FREQ)

    def fp1(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.submit(self.usFunction)
        self._worker.submit(self.infFunction)
        self._worker.shutdown(wait=False)

        # Vorwaerts 3sec
        self.drive(v, 1)
        time.sleep(3)

        # Stillstand 1sec
        self.stop()
        time.sleep(1)

        # Rueckwaerts 3sec
        self.drive(v, -1)
        time.sleep(3)

        # Ende
        self._active = False
        self.stop()
