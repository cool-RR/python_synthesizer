#!pypy3
import math
import random

import numpy as np
import sounddevice
import mido

MASTER_VOLUME = 0.1

delay_seconds = 0.2


class Audio:
    def play(self, samplerate=8000):
        delay = int(delay_seconds * samplerate)
        time_array = np.linspace(0, self.length,
                                 int(self.length * samplerate))
        pressure_array = np.zeros(len(time_array) + delay, dtype='d')

        sounddevice.play(pressure_array, samplerate=samplerate)

        for i, t in enumerate(time_array, start=delay):
            pressure_array[i] = self.get_pressure(t.item())

        sounddevice.wait()


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



class MidiSequence(Sequence):
    tempo = None

    def __init__(self, path):
        self.midi = mido.MidiFile(path)

        members = []

        meta_track, track, *_ = self.midi.tracks

        tempo_messages = [message for message in meta_track if
                          message.type == 'set_tempo']
        self.tempo = tempo_messages[0].tempo

        current_time = 0
        for message in track:
            if message.type not in {'note_on', 'note_off'}:
                continue
            time_interval = mido.tick2second(
                message.time, self.midi.ticks_per_beat, self.tempo)
            current_time += time_interval
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
