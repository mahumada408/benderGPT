import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import simpleaudio as sa
import threading

def moving_average(data, window_size=5):
    return np.convolve(data, np.ones(window_size) / window_size, mode='same')

def discretize_fft(fft_data, num_bands=8, num_rows=7):
    band_width = len(fft_data) // num_bands
    discretized = np.zeros(num_bands)
    for i in range(num_bands):
        start = i * band_width
        end = start + band_width
        discretized[i] = np.mean(fft_data[start:end])
    max_val = np.max(discretized)
    if max_val > 0:
        discretized = discretized / max_val
    discretized = discretized * (num_rows / 2) + (num_rows / 4) 
    return discretized.astype(int)

def play_audio_chunk(chunk, channels, sample_width, frame_rate):
    play_obj = sa.play_buffer(chunk, channels, sample_width, frame_rate)
    play_obj.wait_done()

def generate_frame_data(discretized_fft, x_positions, y_positions):
    frame_data = []
    for x, y in zip(x_positions, y_positions):
        row = int(y)
        col = int(x + 8)
        frame_data.append((row, col, 'red'))
    return frame_data

def update_plot(frame, byte_stream, frames_per_buffer, full_res_mode, args, fig, line, x_freq, stream_index, sample_width, frame_rate, channels):
    print("updating plot")
    index = stream_index[0]
    data = byte_stream[index:index+frames_per_buffer*sample_width*channels]
    stream_index[0] += frames_per_buffer * sample_width * channels
    print(stream_index)

    if len(data) == 0:
        plt.close(fig)
        return line,
    threading.Thread(target=play_audio_chunk, args=(data, channels, sample_width, frame_rate)).start()

    data_np = np.frombuffer(data, dtype=np.int16) / 32768.0
    if data_np.shape[0] < frames_per_buffer:
        data_np = np.pad(data_np, (0, frames_per_buffer - data_np.shape[0]), 'constant', constant_values=(0, 0))
    fft_data = np.abs(np.fft.rfft(data_np)) / frames_per_buffer

    if args.output and not full_res_mode:
        discretized_fft = discretize_fft(fft_data, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(-8, 8)
        y_pos = mirrored_fft - 3.5
        frame_data = generate_frame_data(mirrored_fft, x_pos, y_pos)
        print(frame_data)
    elif full_res_mode:
        fft_data = np.concatenate((fft_data[:0:-1], fft_data))
        smoothed_fft = moving_average(fft_data, window_size=80)
        line.set_data(x_freq, smoothed_fft * 100)
    else:
        print("should be here")
        smoothed_fft = moving_average(fft_data, window_size=80)
        discretized_fft = discretize_fft(smoothed_fft, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(-8, 8)
        line.set_data(x_pos, mirrored_fft)
    return line,

def main():
    parser = argparse.ArgumentParser(description="Symmetric FFT visualization centered on x and y axes.")
    parser.add_argument('file_path', type=str, help='Path to the .wav file')
    parser.add_argument('--mode', type=str, default='full', choices=['full', 'discrete'], help='Visualization mode: full or discrete')
    parser.add_argument('--output', action='store_true', help='Enable output mode to get frame data as a list of tuples')
    args = parser.parse_args()

    # # Load your byte stream here
    # # This is just a placeholder; you should replace it with your actual audio byte stream.
    # byte_stream = b'Your audio byte stream here'

    # # Audio data format specifications
    # sample_width = 2  # Example: 2 for 16-bit audio
    # frame_rate = 44100  # Example: 44100 Hz
    # channels = 2  # Example: 2 for stereo
    stream_index = [0]

    # Open the WAV file and read its byte stream for testing
    with wave.open(args.file_path, 'rb') as wf:
        byte_stream = wf.readframes(wf.getnframes())

    # Extract audio parameters from the WAV file
    sample_width = wf.getsampwidth()
    frame_rate = wf.getframerate()
    channels = wf.getnchannels()

    full_res_mode = args.mode == 'full'

    fig, ax = plt.subplots()
    frames_per_buffer = 512
    x_freq = np.fft.rfftfreq(frames_per_buffer, 1 / frame_rate)

    x_grid, y_grid = np.meshgrid(np.arange(-8, 8), np.arange(7))
    colors = np.full(x_grid.shape, 'yellow')
    colors[:, x_grid[0] == -5] = 'black'
    colors[:, x_grid[0] == 0] = 'black'
    colors[:, x_grid[0] == 5] = 'black'
    for x, y, c in zip(x_grid.flatten(), y_grid.flatten(), colors.flatten()):
        ax.scatter(x, y, color=c)

    if full_res_mode:
        x_freq = np.concatenate((-x_freq[:0:-1], x_freq))
        line, = ax.plot(x_freq, np.zeros(len(x_freq)))
        ax.set_ylim(-1, 1)
        ax.set_xlim(-frame_rate // 2, frame_rate // 2)
    else:
        line, = ax.plot(np.zeros(16), np.zeros(16), 'ko')
        ax.set_ylim(-1, 7)
        ax.set_xlim(-8, 7)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Magnitude')

    ani = FuncAnimation(fig, update_plot, fargs=(byte_stream, frames_per_buffer, full_res_mode, args, fig, line, x_freq, stream_index, sample_width, frame_rate, channels), blit=True, interval=20)
    plt.show()

if __name__ == '__main__':
    main()
