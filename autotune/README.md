# Live Auto-Tune with Backing Track (Failed Experiment)

This was an experimental Python project where I tried to build a **real-time auto-tune system** that:
- Captures live microphone input
- Detects pitch using `aubio`
- Shifts pitch to the nearest musical note
- Mixes the tuned voice with a backing track
- Outputs the combined audio in real-time

Although the idea was ambitious and educational, it ultimately **didn't work as expected in practice**.

---

## ❌ Why It Failed

- **Latency issues**: Real-time processing introduced noticeable delay, especially when applying pitch shift and noise reduction.
- **Pitch shifting artifacts**: The `scipy.signal.resample()` method led to audio artifacts when shifting frequencies.
- **Synchronization**: Mixing the backing track with live input proved difficult to keep in sync.
- **Microphone index hardcoded**: Not portable — it only worked on specific devices without adaptation logic.

---

## ✅ What I Learned

- How to capture real-time audio using `pyaudio`
- Pitch detection with `aubio` and converting frequencies to notes
- Basic pitch shifting using resampling
- Noise reduction using `noisereduce`
- The challenges of building real-time audio pipelines in Python

---

## Stack Used

- Python
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [aubio](https://aubio.org/)
- [librosa](https://librosa.org/)
- [noisereduce](https://github.com/timsainb/noisereduce)
- NumPy, SciPy

---

## Possible Future Fixes

- Use more sophisticated pitch shifting (e.g., `rubberband`, `pyworld`, or phase vocoders)
- Implement a circular buffer system to reduce latency
- Avoid blocking I/O with better stream handling or threading
- Cross-platform device selection interface

---

## 💡 Why It's Still Here

Even though this didn't work out, I'm keeping it on GitHub as a record of:
- My learning journey
- The problems I ran into
- What I’d do differently next time

Feel free to fork this, experiment, or reach out if you’re working on something similar!

---

> **Note:** This project requires a working microphone input and will try to play an audio file from `song.mp3`. Make sure to change `MIC_INDEX` and `SONG_PATH` as needed for your system.
---

## Two Approaches Attempted

### 1. **Real-Time Auto-Tune (live_mix_autotune.py)**
- Tried to apply pitch correction and mix with a song in real time.
- Used `pyaudio`, `aubio`, and `noisereduce`.
- Ultimately failed due to high latency, poor audio quality, and sync issues.

### 2. **Post-Processing Auto-Tune (record_then_autotune.py)**
- Recorded the user’s voice while playing a backing track.
- Applied pitch correction after recording using `librosa.effects.pitch_shift`.
- Output saved as a processed `.wav` file.
- Better quality than live version, but still had challenges with pitch accuracy and timing.

---

## Key Differences

| Feature                | Real-Time Script             | Post-Processing Script            |
|------------------------|------------------------------|-----------------------------------|
| Audio Processing       | Live                         | After recording                   |
| Pitch Shift Method     | `scipy.signal.resample()`    | `librosa.effects.pitch_shift()`   |
| Output Quality         | Laggy & artifact-prone       | Cleaner but less “live” feel      |
| Success Level          | 🚫 Failed                    | ⚠️ Partial Success               |
