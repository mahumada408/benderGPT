import pyaudio
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Define the callback function that will be called when audio data is available
def callback(indata, frames, time, status):
    # Convert the audio data to a NumPy array
    data = np.frombuffer(indata, dtype=np.float32)

    # Plot the waveform
    plt.clear()
    plt.plot(data)
    plt.draw()

# Create a PyAudio stream
stream = pyaudio.PyAudio().open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=44100,
    input=True,
    stream_callback=callback
)

# Start the stream
stream.start_stream()

# Wait for the user to press Enter
plt.show()

# Stop the stream
stream.stop_stream()

# Close the stream
stream.close()
