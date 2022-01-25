#!python3
import math

import numpy as np
import matplotlib.pyplot as plt
import sounddevice

DURATION = 2
SAMPLERATE = 8000
FREQUENCY = 440
MASTER_VOLUME = 0.02
HALF_LIFE = 0.3

overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}

def sine(t):
    volume = MASTER_VOLUME * 2 ** (-t / HALF_LIFE)
    result = 0
    for overtone, overtone_volume in overtones.items():
        result += overtone_volume * math.sin(
            math.tau * t * FREQUENCY * overtone
        )
    return volume * result


time_array = np.arange(0, DURATION, 1 / SAMPLERATE)

pressure_array = np.zeros_like(time_array)
for i, t in enumerate(time_array):
    pressure_array[i] = sine(t.item())

plt.plot(pressure_array[:60])
plt.show()

sounddevice.play(pressure_array, samplerate=SAMPLERATE)
sounddevice.wait()

