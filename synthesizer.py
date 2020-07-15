#!pypy3
import math
import random

import numpy as np
import matplotlib.pyplot as plt
import sounddevice
import mido


MASTER_VOLUME = 0.05
HALF_LIFE = 0.3
INITIAL_DELAY = 0.2
SAMPLERATE = 32_000

overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}

class Audio:
    def play(self):
        self.n_delay_samples = int(INITIAL_DELAY * SAMPLERATE)
        time_array = np.linspace(0, self.length,
                                 int(self.length * SAMPLERATE))
        self.pressure_array = np.zeros(
            self.n_delay_samples + len(time_array)
        )
        sounddevice.play(self.pressure_array, samplerate=SAMPLERATE)
        self.update_pressure()
        sounddevice.wait()

class Note(Audio):
    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

    def get_pressure(self):
        t = np.arange(int(self.length * SAMPLERATE)) / SAMPLERATE
        result = sum(
            overtone_volume * np.sin(2 * np.pi * t * self.frequency * overtone)
            for overtone, overtone_volume in overtones.items())
        volume = (MASTER_VOLUME * self.volume * 2 ** (-t / HALF_LIFE))
        return result * volume


class Sequence(Audio):
    def __init__(self, offsets_and_notes):
        self.offsets_and_notes = tuple(offsets_and_notes)
        self.length = max(offset + note.length for offset, note
                          in self.offsets_and_notes)

    def __init__(self, offsets_and_notes):
        self.offsets_and_notes = tuple(offsets_and_notes)
        self.length = max(
            offset + note.length for offset, note in self.offsets_and_notes
        )

    def update_pressure(self):
        for offset, note in self.offsets_and_notes:
            pressure = note.get_pressure()
            offset = int(offset * SAMPLERATE) + self.n_delay_samples
            self.pressure_array[offset : offset + len(pressure)] += pressure

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
