#!pypy3
import math
import random

import numpy as np
import matplotlib.pyplot as plt
import sounddevice
import mido


MASTER_VOLUME = 0.01
HALF_LIFE = 0.3
INITIAL_DELAY = 0.2

overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}

class Audio:
    def play(self, samplerate=8000):
        n_delay_samples = int(INITIAL_DELAY * samplerate)
        time_array = np.arange(0, self.length, 1 / samplerate)
        pressure_array = np.zeros(n_delay_samples + len(time_array))
        sounddevice.play(pressure_array, samplerate=samplerate)
        for i, t in enumerate(time_array, start=n_delay_samples):
            pressure_array[i] = self.get_pressure(t.item())
        sounddevice.wait()

class Note(Audio):
    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

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

class Sequence(Audio):
    def __init__(self, offsets_and_notes):
        self.offsets_and_notes = tuple(offsets_and_notes)
        self.length = max(offset + note.length for offset, note
                          in self.offsets_and_notes)

    def get_pressure(self, t):
        return sum(note.get_pressure(t - offset) for offset, note in
                   self.offsets_and_notes)


class MidiSequence(Sequence):
    def __init__(self, path):
        offsets_and_notes = []

        current_time = 0
        for message in mido.MidiFile(path):
            current_time += message.time
            if message.type != 'note_on':
                continue
            offsets_and_notes.append((
                current_time,
                Note(
                    440 * 2 ** ((message.note - 69) / 12),
                    message.velocity / 127
                )
            ))

        Sequence.__init__(self, offsets_and_notes)


if __name__ == '__main__':
    midi_sequence = MidiSequence('FurElise.mid')
    midi_sequence.play()
