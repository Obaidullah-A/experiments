import pyaudio
import numpy as np
import aubio
import librosa
import librosa.effects
import noisereduce as nr
import soundfile as sf
import simpleaudio as sa
from collections import deque

CHUNK = 2048  
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100  
MIC_INDEX = 2  
ROLLING_AVG_WINDOW = 5  

SONG_PATH = "song.mp3"  
y, sr = librosa.load(SONG_PATH, sr=RATE)
song_wave = (y * 32767).astype(np.int16)  

p = pyaudio.PyAudio()

input_stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=MIC_INDEX,
    frames_per_buffer=CHUNK
)

a_tuner = aubio.pitch("yin", CHUNK * 2, CHUNK, RATE)
a_tuner.set_unit("Hz")
a_tuner.set_tolerance(0.8)

NOTES = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])  

def closest_note(freq):
    return NOTES[np.argmin(np.abs(NOTES - freq))]

pitch_history = deque(maxlen=ROLLING_AVG_WINDOW)

def smooth_pitch(pitch):
    pitch_history.append(pitch)
    return np.mean(pitch_history)

print("Recording... Sing along with the song.")

play_obj = sa.play_buffer(song_wave, 1, 2, RATE)

recorded_audio = []
try:
    song_pos = 0
    while song_pos + CHUNK < len(y):
        
        audio_data = np.frombuffer(input_stream.read(CHUNK), dtype=np.float32)
        recorded_audio.append(audio_data)
        song_pos += CHUNK

except KeyboardInterrupt:
    print("Recording stopped.")

play_obj.wait_done()  

input_stream.stop_stream()
input_stream.close()
p.terminate()

recorded_audio = np.concatenate(recorded_audio)

recorded_audio = nr.reduce_noise(y=recorded_audio, sr=RATE)

processed_audio = []
for i in range(0, len(recorded_audio), CHUNK):
    chunk = recorded_audio[i:i+CHUNK]
    detected_pitch = a_tuner(chunk)[0]
    smoothed_pitch = smooth_pitch(detected_pitch) if detected_pitch > 0 else detected_pitch
    tuned_pitch = closest_note(smoothed_pitch) if smoothed_pitch > 0 else smoothed_pitch
    
    if smoothed_pitch > 0:
        chunk = np.array(chunk, dtype=np.float32)  
        processed_audio.append(librosa.effects.pitch_shift(chunk, sr=RATE, n_steps=(tuned_pitch - smoothed_pitch) / 12))
    else:
        processed_audio.append(chunk)

processed_audio = np.concatenate(processed_audio)

OUTPUT_FILE = "processed_output.wav"
sf.write(OUTPUT_FILE, processed_audio, RATE)
print(f"Processed audio saved to {OUTPUT_FILE}")