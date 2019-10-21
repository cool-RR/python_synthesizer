#!python3
import math

import numpy as np
import matplotlib.pyplot as plt
import sounddevice

MASTER_VOLUME = 0.1
HALF_LIFE = 0.3

overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}

class Note:
    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

    def play(self, samplerate=8000):
        time_array = np.linspace(0, self.length,
                                 int(self.length * samplerate))
        pressure_array = np.zeros_like(time_array)
        for i, t in enumerate(time_array):
            pressure_array[i] = self.get_pressure(t.item())
        sounddevice.play(pressure_array, samplerate=samplerate)
        sounddevice.wait()

    def get_pressure(self, t):
        if 0 <= t <= self.length:
            result = 0
            for overtone, overtone_volume in overtones.items():
                result += overtone_volume * math.sin(
                    math.tau * t * self.frequency * overtone
                )
            volume = MASTER_VOLUME * self.volume * 2 ** (-t / HALF_LIFE)
            return result * volume
        else:
            return 0


if __name__ == '__main__':
    note = Note(440)
    note.play()
