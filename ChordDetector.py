import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import struct
import scipy.signal as signal
from PCP import compute_PCP
import json
import sys, getopt
import keyboard
from math import floor

NOTE_MIN = 48      #You can use the function note_name to find out which note this is (C3)
NOTE_MAX = 107       
FRAME_SIZE = 1048*2   
FRAMES_PER_FFT = 8*2 #8 is best for single note detection
FSAMP = FRAME_SIZE*FRAMES_PER_FFT*2 #Improving SAMPLES_PER_FFT/FSAMP increases the resolution but lowering FSAMP reduces speed

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT
NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(floor(n/12 - 1))


def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

# load in the template chord shapes for comparison
def get_templates(chords):
    #Change the number at the end of templates depending on what chords you want to load: templates- min,maj, templates1- min,maj,dim, templates2-min,maj,dim,7
    #You need to change the chords in the function get_nested_circle_of_fifths() to match the ones loaded in
    with open("data/chord_templates2.json", "r") as fp:
        templates_json = json.load(fp)
    templates = []

    for chord in chords:
        if chord == "N":
            continue
        templates.append(templates_json[chord])

    return templates


def get_nested_circle_of_fifths():
    chords = [
        "N",
        #major:
        "G","G#","A","A#","B","C","C#","D","D#","E","F","F#",
        #minor:
        "Gm","G#m","Am","A#m","Bm","Cm","C#m","Dm","D#m","Em","Fm","F#m",
        #dim:
        "Gdim","G#dim","Adim","A#dim","Bdim","Cdim","C#dim", "Ddim","D#dim","Edim","Fdim","F#dim"
        #7:"
        #,"G7", "G#7", "A7", "A#7", "B7", "C7", "C#7", "D7", "D#7", "E7", "F7", "F#7"
    ]
    return chords


CHORDS= get_nested_circle_of_fifths()
TEMPLATES = get_templates(CHORDS)


def CMR(u, v):
    return np.dot(u, v) / np.sqrt(np.sum(np.square(u)) *np.sum(np.square(v)))


def  detect_chord(buf):
    chroma = compute_PCP(buf, FSAMP)
    print(chroma)
    cor_vec = np.zeros(len(TEMPLATES))
    for i in range(len(TEMPLATES)):
        #cor_vec[i] = np.correlate(chroma, np.array(templates[i]))
        cor_vec[i] = CMR(chroma, np.array(TEMPLATES[i]))
        if TEMPLATES[i][-3:] == "dim":
            cor_vec[i]*=1.1
        if TEMPLATES[i][-1] == '7':
            cor_vec[i]*=0.6
    id_chord = np.argmax(cor_vec) + 1
    print(np.max(cor_vec))
    print(CHORDS[id_chord])
    return CHORDS[id_chord]


def detect_note(buf, window):
    #The function is more precise in detecting one note
    fft = np.fft.fft(buf*window)
    fft = fft[:len(fft)//2+1]*2/11000

    #Slashing the higher freaquencies to avoid false posetives when detecting notes at lower ones
    for i in range(imin, imax):
        if i*FREQ_STEP > 520:
            fft[i] /= (np.log10(i)*1.5)
        if i*FREQ_STEP > 1000:
            fft[i] /= 2*(np.log10(i)*8)
        if i*FREQ_STEP < 250:
            fft[i] *= 2*(np.log10(i))
    
    
    fftRange = fft[imin:imax]
    #Finding two highest amplitudes
    freq = (np.abs(fftRange).argmax() + imin) * FREQ_STEP
    pom = np.append(fftRange[:int(freq/FREQ_STEP) - imin - 5], fftRange[int(freq/FREQ_STEP) - imin + 5:])
    freq1 = (np.abs(pom).argmax() + imin) * FREQ_STEP

    # Get note number and nearest note
    n = freq_to_number(freq)
    n0 = int(round(n))
    n = freq_to_number(freq1)
    n1 = int(round(n))
    print ('freq: {:7.2f} Hz     note: {:<3s}  note2: {:<3s}'.format(freq, note_name(n0), note_name(n1)))
    

    #uncomment to plot the spectrograph of every note
    """plt.close(fig)
    plt.subplot(1,2,1)
    m = range(len(buf[-SAMPLES_PER_FFT:]))
    plt.plot(m, np.abs(buf[-SAMPLES_PER_FFT:]))
    plt.subplot(1,2,2)
    l = range(len(fft))
    plt.stem(l, fft)
    plt.show()"""
    return "note1: " + note_name(n0) + " note2: " + note_name(n1)


#Main code
def audio_transcription(argv):
    method = "chords"
    try:
        opts, args = getopt.getopt(argv, "hm:", ["method="])
    except getopt.GetoptError:
        print(getopt.GetoptError.msg)
    for opt, arg in opts:
        if opt in ("-m", "--method"):
                if(arg == "notes" or arg == "chords"):
                    method = arg
                else:
                    print("method must be 'chords' or 'notes'")
                    sys.exit()

    buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
    num_frames = 0

    #Initialize note detection check
    note_detected = 0

    # Initialize audio
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE,
                                input_device_index=1)

    stream.start_stream()

    print ('Stream open sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')

    #Filters that might be useful

    #b, a = signal.butter(2, 2*90/FSAMP, btype='highpass')
    #sos = signal.butter(0, 100, 'hp',fs = FSAMP, output ='sos')

    notes = []
    counter = 0
    
    # Create Hanning window function if we are detecting notes
    if method == "notes":
        window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

# As long as we are getting data:
    while stream.is_active():

        # Shift the buffer down and new data in
        buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
        data = stream.read(FRAME_SIZE)
        buf[-FRAME_SIZE:] = struct.unpack(str(FRAME_SIZE) + 'h', data)

        # Console output once we have a full buffer
        if num_frames<= FRAMES_PER_FFT:
            num_frames += 1

        #We check for peaks in the audio signal so we don't have to in the 
        if (note_detected == 0 and 20*np.log10(max(np.abs(buf[-FRAME_SIZE:]))) > 70) or counter != 0:
            note_detected = 1
            counter = counter + 1
            

        if num_frames >= FRAMES_PER_FFT:
            if(note_detected > 0):
            
                if counter>= FRAMES_PER_FFT:
                    if(method == "chords"):
                        notes.append(detect_chord(buf))
                    else:
                        notes.append(detect_note(buf, window))
                    counter = 0
                note_detected = 0

        if keyboard.is_pressed('f'):
                print("Key 'f' pressed. Stopping audio stream...")
                break
    stream.close()  
    if method == "chords":
        print("chords: ")
    else:
        print("notes: ") 

    for note in notes:
        print(note)




if __name__ == "__main__":
    audio_transcription(sys.argv[1:])
