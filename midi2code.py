from music21 import converter, instrument, note, chord
import json
import sys

def extractNote(element):
    return int(element.pitch.ps)

def extractDuration(element):
    return element.duration.quarterLength

def extractAmplitude(element):
    if element.isRest:
        return 0
    else:
        return 1

def midi2note(n):
    return n - 60

def midiNotes2notes(notes):
    return [tuple(map(lambda x:midi2note(x),list(note))) for note in notes]

from magenta.models.gansynth.lib import generate_util as gu

def get_notes(midi_path):
    a,b = gu.load_midi(midi_path)

    durations = list(b["end_times"] - b["start_times"])
    notes = list(map(lambda x : tuple((int(x),)),b["pitches"]))
    start = list(b["start_times"])
    return start, notes, durations, [1]*len(notes)

def findFreeSpace(note_start,last_ends):
    #print(note_start, last_ends)
    for k, last_end in last_ends.items():
        if last_end <= note_start:
            return k
    return -1
    
def notesProcessing(values,start,length):
    notes_info = list(zip(values[0],values[1],values[2],values[3]))
    #notes_info = sorted(notes_info, key=lambda x : x[0])
    notes_info = sorted(list(filter(lambda x : (start <= x[0]) and (x[0] + 4 < start + length), notes_info)), key=lambda x : x[0])
    
    notes_per_beat = {str(k): [] for k in map(lambda x : x[0], notes_info)}

    for note in notes_info:
        notes_per_beat[str(note[0])].append(note)

    notes_at_the_same_time = 30
    print(notes_at_the_same_time)
    final_notes = []
    final_durs = []
    final_amps = []

    final_data = {str(i):([],[],[],[]) for i in range(notes_at_the_same_time)}
    last_ends = {str(i):0 for i in range(notes_at_the_same_time)}

    for _, notes_data in notes_per_beat.items():
        for note_data in notes_data:
            k = findFreeSpace(note_data[0],last_ends)
            if k != -1:
                start, notes, durations, amps = final_data[k]
                last_end = last_ends[k]
                if last_end < note_data[0]:
                    start.append(last_end)
                    notes.append((0,))
                    durations.append(note_data[0]-last_end)
                    amps.append(0)

                start.append(note_data[0])
                notes.append(note_data[1])
                if note_data[0] + note_data[2] > length: 
                    durations.append(length-note_data[0])
                else:
                    durations.append(note_data[2])
                amps.append(note_data[3])

                if note_data[0] + note_data[2] > last_end:
                    last_ends[k] = note_data[0] + note_data[2]

    for k,v in final_data.items():
        start, notes, durations, amps = v
        if sum(durations) < length:
            start.append(-1)
            notes.append((0,))
            durations.append(length - sum(durations))
            amps.append(0)

    final_data2 = {}
    for k,v in final_data.items():
        if len(v[0]) > 1:
            final_data2[k] = v

    return final_data2

def main(midiFile,output_file,start,length):

    data = {}
    data["piano"] = get_notes(midiFile)


    with open('/home/mathi/Escritorio/midi2code/base_file.py','r') as f:
        text = f.read()

    letters = ["j","k","l"]

    i = 0
    u = 0
    final_compas = [[]]
    for k, v in data.items():
        if len(v[0]) > 0 and len(v[1]) > 0:
            values = list(data.values())
            values_i = values[i]
            final_data = notesProcessing(values_i,start,length)
            for final_v in final_data.values():
                notes = midiNotes2notes(final_v[1])
                dur = final_v[2]
                amps = final_v[3]
                letter = letters[int(u/10)]
                final_compas[0].append(f"\t{letter}{u%10} >> piano({notes},dur={dur},amp={amps},scale=list(range(12)))\n")
                u += 1
        i+=1

    final_compas = list(filter(lambda x : len(x) > 0, final_compas))
    i = 0
    for compass in final_compas:
            text += "@structure\n"
            text += "def parte{}():\n".format(i)
            i+=1
            for instrument_i in compass:
                text += instrument_i
    text += "\ndef run():\n\tstart = Clock.mod({}) - 0.1\n".format(8)
    for i in range(len(final_compas)):
            text += "\tClock.schedule(parte{}, start + {})\n".format(i,8*i)

    with open(output_file,'w') as f:
        f.write(text)

file_path = sys.argv[1]
start = int(sys.argv[2])
length = int(sys.argv[3])

outputFile = file_path.split("/")[-1].replace(".mid",".py")

main(file_path, outputFile, start, length)
