#!python3
import math

import numpy as np
import matplotlib.pyplot as plt
import sounddevice


MASTER_VOLUME = 0.2


class Audio:
    def play(self, samplerate=8000):
        time_array = np.linspace(0, self.length,
                                 int(self.length * samplerate))
        pressure_array = np.zeros(time_array.shape, dtype='d')
        for i, t in enumerate(time_array):
            pressure_array[i] = self.get_pressure(t.item())
        sounddevice.play(pressure_array, samplerate=samplerate,
                         blocking=True)


class Note(Audio):
    overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}
    half_life = 0.3

    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

    def get_pressure(self, t):
        if (0 <= t <= self.length):
            result = 0
            for overtone, overtone_volume in self.overtones.items():
                result += overtone_volume * math.sin(
                    math.tau * t * self.frequency * overtone
                )
            volume = (MASTER_VOLUME * self.volume *
                      2 ** (-t / self.half_life))
            result *= volume
            return result
        else:
            return 0

class Sequence(Audio):
    def __init__(self, members):
        self.members = tuple(members)
        self.length = max(
            offset + member.length for offset, member in self.members
        )

    def get_pressure(self, t):
        return sum(member.get_pressure(t - offset) for offset, member in
                   self.members)



if __name__ == '__main__':
    sequence = Sequence((
        (0.0, Note(440 * 2 ** (0 / 12))),
        (0.2, Note(440 * 2 ** (4 / 12))),
        (0.4, Note(440 * 2 ** (7 / 12))),
        (0.6, Note(440 * 2 ** (4 / 12))),
        (0.8, Note(440 * 2 ** (12 / 12))),
    ))
    sequence.play()
