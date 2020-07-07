#!python3
import math

import numpy as np
import matplotlib.pyplot as plt
import sounddevice

DURATION = 2
SAMPLERATE = 8000
FREQUENCY = 440
MASTER_VOLUME = 0.2

def sine(t):
    return MASTER_VOLUME * math.sin(math.tau * t * FREQUENCY)


time_array = np.linspace(0, DURATION, DURATION * SAMPLERATE)

pressure_array = np.zeros_like(time_array)
for i, t in enumerate(time_array):
    pressure_array[i] = sine(t.item())

plt.plot(pressure_array[:60])
plt.show()

sounddevice.play(pressure_array, samplerate=SAMPLERATE)
sounddevice.wait()

