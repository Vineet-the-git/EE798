import pyaudio
import numpy as np
import time


chunk_size = 1024
sample_rate = 44100
window_size = 2

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size)

def preprocess_audio(audio_chunk):
    # Apply a windowing function (e.g., Hamming window) to the audio chunk
    windowed_chunk = audio_chunk * np.hamming(len(audio_chunk))
    # Normalize the audio data
    normalized_chunk = windowed_chunk / np.max(np.abs(windowed_chunk))
    return normalized_chunk

def autocorrelation_pitch_estimation(audio_chunk, sample_rate):
    autocorr = np.correlate(audio_chunk, audio_chunk, mode='full')
    lag = np.argmax(autocorr[len(autocorr)//2:])  # Find lag with highest peak
    fundamental_frequency = sample_rate / lag
    return fundamental_frequency

def fft_pitch_estimation(audio_chunk, sample_rate):
    spectrum = np.fft.fft(audio_chunk)
    freqs = np.fft.fftfreq(len(spectrum), d=1/sample_rate)
    peak_freq_index = np.argmax(np.abs(spectrum))
    fundamental_frequency = abs(freqs[peak_freq_index])
    return fundamental_frequency

pitch_buffer = []  # Store pitch values for the window
start_time = time.time()

try:
    while True:
        audio_data = np.frombuffer(stream.read(chunk_size), dtype=np.float32)
        preprocessed_data = preprocess_audio(audio_data)
        pitch = fft_pitch_estimation(preprocessed_data, sample_rate)
        pitch_buffer.append(pitch)

        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time >= window_size:
            average_pitch = np.mean(pitch_buffer)
            print(f"Average pitch (over {window_size} sec): {average_pitch:.2f} Hz", end='\r')

            # Clear pitch buffer and reset start time
            pitch_buffer = []
            start_time = current_time

except KeyboardInterrupt:
    pass
finally:
    print("\nExiting...")
    stream.stop_stream()
    stream.close()
    p.terminate()