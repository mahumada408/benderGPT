import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import simpleaudio as sa
import threading

# Function for simple moving average
def moving_average(data, window_size=5):
    return np.convolve(data, np.ones(window_size) / window_size, mode='same')

# Set up argument parser
parser = argparse.ArgumentParser(description="Symmetric FFT visualization centered on x-axis.")
parser.add_argument('file_path', type=str, help='Path to the .wav file')
args = parser.parse_args()

# Open the .wav file
wf = wave.open(args.file_path, 'rb')
frame_rate = wf.getframerate()
channels = wf.getnchannels()
sample_width = wf.getsampwidth()

# Prepare matplotlib plot for updating
fig, ax = plt.subplots()
frames_per_buffer = 512  # Adjust as needed
x_freq = np.fft.rfftfreq(frames_per_buffer, 1 / frame_rate)
x_freq = np.concatenate((-x_freq[:0:-1], x_freq))  # Symmetric frequency axis
line, = ax.plot(x_freq, np.zeros(len(x_freq)))
ax.set_ylim(-1, 1)  # Centered around y-axis
ax.set_xlim(-frame_rate // 2, frame_rate // 2)  # Symmetric x-axis
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude')

# Function to play audio chunk
def play_audio_chunk(chunk):
    play_obj = sa.play_buffer(chunk, channels, sample_width, frame_rate)
    play_obj.wait_done()

# Update function for the plot and audio
def update_plot(frame):
    data = wf.readframes(frames_per_buffer)
    if len(data) == 0:
        plt.close(fig)  # Close the plot once playback is finished
        return line,
    threading.Thread(target=play_audio_chunk, args=(data,)).start()
    data_np = np.frombuffer(data, dtype=np.int16)
    data_np = data_np / 32768.0  # Normalize to [-1, 1]
    if data_np.shape[0] < frames_per_buffer:
        data_np = np.pad(data_np, (0, frames_per_buffer - data_np.shape[0]), 'constant', constant_values=(0, 0))
    fft_data = np.abs(np.fft.rfft(data_np)) / frames_per_buffer
    fft_data = np.concatenate((fft_data[:0:-1], fft_data))  # Symmetric FFT data
    max_magnitude = np.max(fft_data)
    smoothed_fft = moving_average(fft_data, window_size=80)  # Adjust window size as needed
    line.set_ydata(smoothed_fft / max_magnitude)  # Normalize to [-1, 1] range
    return line,

# Create animation with faster updates
ani = FuncAnimation(fig, update_plot, blit=True, interval=20)  # Reduced interval for faster updates

plt.show()
