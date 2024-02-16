import wave

def add_riff_header(input_filename, output_filename, params):
    # Read the raw audio data
    with open(input_filename, 'rb') as raw_audio_file:
        raw_audio_data = raw_audio_file.read()

    # Write the raw audio data to a new WAV file with a RIFF header
    with wave.open(output_filename, 'wb') as wav_file:
        # Set parameters: nchannels, sampwidth, framerate, nframes, comptype, compname
        wav_file.setparams(params)
        wav_file.writeframes(raw_audio_data)

# Example usage
input_filename = '/home/benderpi/bender_test.wav'  # Replace with your actual file name
output_filename = '/home/benderpi/bender_w_riff.wav'

# WAV file parameters (Example: stereo, 16-bit, 44.1 kHz)
params = (1, 2, 44100, 0, 'NONE', 'not compressed')
add_riff_header(input_filename, output_filename, params)

# wf = wave.open(output_filename, 'rb')


# def get_wav_params(filename):
#     # Open the WAV file
#     with wave.open(filename, 'rb') as wav_file:
#         # Extract parameters
#         nchannels = wav_file.getnchannels()
#         sampwidth = wav_file.getsampwidth()
#         framerate = wav_file.getframerate()
#         nframes = wav_file.getnframes()
#         comptype = wav_file.getcomptype()
#         compname = wav_file.getcompname()

#         return nchannels, sampwidth, framerate, nframes, comptype, compname

# # Example usage
# filename = '/home/benderpi/Desktop/wired_8k.wav'  # Replace with your WAV file name
# params = get_wav_params(filename)
# print("WAV file parameters:", params)
