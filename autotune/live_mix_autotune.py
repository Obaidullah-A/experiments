import pyaudio
import numpy as np
import aubio
import scipy.signal
import librosa
import noisereduce as nr

CHUNK = 1024  
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100  
MIC_INDEX = 2  

SONG_PATH = "song.mp3"  
y, sr = librosa.load(SONG_PATH, sr=RATE)

p = pyaudio.PyAudio()

input_stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=MIC_INDEX,  
    frames_per_buffer=CHUNK
)

output_stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=CHUNK
)

a_tuner = aubio.pitch("yin", CHUNK * 2, CHUNK, RATE)
a_tuner.set_unit("Hz")
a_tuner.set_tolerance(0.8)

NOTES = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])  

def closest_note(freq):
    return NOTES[np.argmin(np.abs(NOTES - freq))]

def pitch_shift(data, orig_freq, target_freq):
    if orig_freq == 0 or target_freq == 0:
        return data  
    shift_factor = target_freq / orig_freq
    return scipy.signal.resample(data, int(len(data) * shift_factor))

print("Live Auto-Tune Running... Press Ctrl+C to stop.")

try:
    song_pos = 0
    while True:
        
        audio_data = np.frombuffer(input_stream.read(CHUNK), dtype=np.float32)
        
        audio_data = nr.reduce_noise(y=audio_data, sr=RATE)
        
        detected_pitch = a_tuner(audio_data)[0]
        
        tuned_pitch = closest_note(detected_pitch) if detected_pitch > 0 else detected_pitch
        
        tuned_audio = pitch_shift(audio_data, detected_pitch, tuned_pitch) if detected_pitch > 0 else audio_data
        
        if song_pos + CHUNK < len(y):
            song_segment = y[song_pos:song_pos + CHUNK]
            song_pos += CHUNK
        else:
            song_segment = np.zeros(CHUNK)  
        
        min_len = min(len(tuned_audio), len(song_segment))
        tuned_audio = tuned_audio[:min_len]
        song_segment = song_segment[:min_len]
        mixed_audio = 0.5 * tuned_audio + 0.5 * song_segment  
        
        output_stream.write(mixed_audio.astype(np.float32).tobytes())

except KeyboardInterrupt:
    print("Stopping...")
    input_stream.stop_stream()
    input_stream.close()
    output_stream.stop_stream()
    output_stream.close()
    p.terminate()