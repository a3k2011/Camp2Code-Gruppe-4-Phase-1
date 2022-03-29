import os
import time
from datetime import datetime
import numpy as np
import soniccar_tim as SCT
from basisklassen import Infrared


class InfraredCar(SCT.SonicCar):

    INF_FREQ = 0.05

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

    def lenkFunction(self):
        dictActions = {'0': 'self.steering_angle = 45',
                        '1': 'self.steering_angle = 60',
                        '2': 'self.steering_angle = 90',
                        '3': 'self.steering_angle = 120',
                        '4': 'self.steering_angle = 135'}
        while self._active:
            idx_min = str(np.argmin(self._analog))
            std = np.std(self._analog)
            if std < 3.5:
                print(std)
                self._active = False
                break
            if idx_min in dictActions:
                    exec(dictActions[idx_min])

            time.sleep(self.INF_FREQ)

    def inf_test(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.submit(self.usFunction)
        self._worker.submit(self.infFunction)
        self._worker.shutdown(wait=False)

        # Start
        time.sleep(3)

        # Ende
        self._active = False
        self.stop()

    def fp5(self, v):
        # Initialisiere Threads
        self._active = True
        self._worker.submit(self.loggerFunction)
        self._worker.submit(self.usFunction)
        self._worker.submit(self.infFunction)
        self._worker.submit(self.lenkFunction)
        
        # Vorwaerts 3sec
        self.drive(v, 1)

        # Ende
        self._worker.shutdown(wait=True)
        self.steering_angle = 90
        self.stop()
