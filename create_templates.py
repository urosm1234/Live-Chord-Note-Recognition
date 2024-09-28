
#Run just once

import json
import numpy as np

template = dict()
major = ["G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#"]
minor = ["Gm", "G#m", "Am", "A#m", "Bm", "Cm", "C#m", "Dm", "D#m", "Em", "Fm", "F#m"]
chord7 = ["G7", "G#7", "A7", "A#7", "B7", "C7", "C#7", "D7", "D#7", "E7", "F7", "F#7"]
dim = ["Gdim", "G#dim", "Adim", "A#dim", "Bdim", "Cdim", "C#dim", "Ddim", "D#dim", "Edim", "Fdim", "F#dim"]

offset = 0
num_chords = len(major)

base = {'major': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], 'minor': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], 'dim':[1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0], 'chord7': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0] }
# initialise lists with zeros
for chord in range(num_chords):
    template[major[chord]] = list()
    template[minor[chord]] = list()
    template[major[chord]] = np.zeros(12)
    template[minor[chord]] = np.zeros(12)
    template[dim[chord]] = np.zeros(12)
    template[chord7[chord]] = np.zeros(12)

for chord in range(num_chords):
    
    template[major[chord]] = base['major'][-offset:] + base['major'][:-offset]
    template[minor[chord]] = base['minor'][-offset:] + base['minor'][:-offset]
    template[dim[chord]] = base['dim'][-offset:] + base['dim'][:-offset]
    template[chord7[chord]] = base['chord7'][-offset:] + base['chord7'][:-offset]
    offset += 1

# check if everything is loaded correctly
for key, value in template.items():
    print(key, value)
      

# save as JSON file
with open("chord_templates2.json", "w") as fp:
    json.dump(template, fp, sort_keys=False)
    print("Saved succesfully to JSON file")
