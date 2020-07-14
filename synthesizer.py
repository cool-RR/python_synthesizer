#!pypy3
import math
import random

import numpy as np
import sounddevice
import mido

MASTER_VOLUME = 0.1


class Audio:
    def play(self, samplerate=48000, delay_seconds=0.2):
        self.samplerate = samplerate
        self.delay = int(delay_seconds * samplerate)
        self.pressure_array = np.zeros(
            int(self.length * samplerate) + self.delay, dtype='d')
        sounddevice.play(self.pressure_array, samplerate=self.samplerate)
        self.update_pressure()
        sounddevice.wait()


class Note:

    overtones = {i: 1 / (i ** 1.5) for i in range(1, 8)}
    half_life = 0.3

    def __init__(self, frequency, volume=1):
        self.frequency = frequency
        self.volume = volume
        self.length = 1.5

    def get_pressure(self, samplerate):
        t = np.arange(int(self.length * samplerate)) / samplerate
        result = sum(
            overtone_volume * np.sin(2 * np.pi * t * self.frequency * overtone)
            for overtone, overtone_volume in self.overtones.items())
        volume = (MASTER_VOLUME * self.volume * 2 ** (-t / self.half_life))
        return result * volume


class Sequence(Audio):
    def __init__(self, members):
        self.members = tuple(members)
        self.length = max(
            offset + member.length for offset, member in self.members
        )

    def update_pressure(self):
        for offset, note in self.members:
            pressure = note.get_pressure(self.samplerate)
            offset = int(offset * self.samplerate) + self.delay
            self.pressure_array[offset:offset + len(pressure)] += pressure


class MidiSequence(Sequence):

    def __init__(self, path):
        members = []

        current_time = 0
        for message in mido.MidiFile(path):
            current_time += message.time
            if message.type != 'note_on':
                continue
            members.append((
                current_time,
                Note(
                    220 * 2 ** ((message.note - 57) / 12),
                    message.velocity / 127
                )
            ))

        Sequence.__init__(self, members)


if __name__ == '__main__':
    midi_sequence = MidiSequence('FurElise.mid')
    midi_sequence.play()
