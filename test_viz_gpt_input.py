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

# Function to discretize FFT data for a 7x16 display
def discretize_fft(fft_data, num_bands=16, num_rows=7):
    band_width = len(fft_data) // num_bands
    discretized = np.zeros(num_bands)
    for i in range(num_bands):
        start = i * band_width
        end = start + band_width
        discretized[i] = np.mean(fft_data[start:end])
    discretized = np.clip(discretized / np.max(discretized), 0, 1)  # Normalize to [0, 1]
    discretized = (discretized * num_rows).astype(int)  # Scale to 0-6
    return discretized

# Set up argument parser
parser = argparse.ArgumentParser(description="Symmetric FFT visualization centered on x and y axes.")
parser.add_argument('file_path', type=str, help='Path to the .wav file')
parser.add_argument('--mode', type=str, default='full', choices=['full', 'discrete'], help='Visualization mode: full or discrete')
args = parser.parse_args()

# Open the .wav file
wf = wave.open(args.file_path, 'rb')
frame_rate = wf.getframerate()
channels = wf.getnchannels()
sample_width = wf.getsampwidth()

# Determine visualization mode
full_res_mode = args.mode == 'full'

# Prepare matplotlib plot for updating
fig, ax = plt.subplots()
frames_per_buffer = 512  # Adjust as needed
x_freq = np.fft.rfftfreq(frames_per_buffer, 1 / frame_rate)
if full_res_mode:
    x_freq = np.concatenate((-x_freq[:0:-1], x_freq))  # Symmetric frequency axis for full resolution
    line, = ax.plot(x_freq, np.zeros(len(x_freq)))
    ax.set_ylim(-1, 1)  # Centered around y-axis
    ax.set_xlim(-frame_rate // 2, frame_rate // 2)  # Full symmetric frequency range
else:
    line, = ax.plot(np.zeros(16), np.zeros(16), 'ro')  # 16 points for 16 frequency bands (8 mirrored)
    ax.set_ylim(0, 7)  # 7 rows of pixels
    ax.set_xlim(-8, 7)  # 8 columns of pixels mirrored
ax.set_xlabel('Frequency')
ax.set_ylabel('Magnitude')
ax.grid(True)

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
    if full_res_mode:
        fft_data = np.concatenate((fft_data[:0:-1], fft_data))  # Symmetric FFT data
        smoothed_fft = moving_average(fft_data, window_size=80)  # Adjust window size as needed
        line.set_data(x_freq, smoothed_fft * 100)  # Centered around y=0
    else:
        smoothed_fft = moving_average(fft_data, window_size=80)  # Adjust window size as needed
        discretized_fft = discretize_fft(smoothed_fft, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))  # Mirror the data
        x_pos = np.arange(-8, 8)  # Adjusted x positions for 16 points
        line.set_data(x_pos, mirrored_fft)
    return line,

# Create animation with updates
ani = FuncAnimation(fig, update_plot, blit=True, interval=20)

plt.show()
