import time
import os
import random

import elevenlabs
import pvporcupine, pvcheetah
from pvrecorder import PvRecorder
from pygame import mixer
from openai import OpenAI

import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import simpleaudio as sa
import threading

from pydub import AudioSegment

import json
import fcntl

import serial
import subprocess

from spotify_player import play_spotify_song, stop_spotify
from photographer import take_a_picture

import base64
import requests

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.reset_input_buffer()

ENDPOINT_DURATION_SECONDS = 2 # 'Quiet' seconds indicating the end of audio capture
AUDIO_DEVICE_NAME = "Plugable USB Audio Device Analog Stereo"
AUDIO_DEVICE = PvRecorder.get_available_devices().index(AUDIO_DEVICE_NAME)
porcupine_key = os.environ.get("PORCUPINE_API_KEY")

PROMPT = "You are Bender from Futurama. Respond to my query in a Bender way in 100 characters or less: "
QUERY = "Hey bender. How did your day go?"

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

porcupine = pvporcupine.create(
    access_key=porcupine_key,
    keywords=['terminator'])

cheetah = pvcheetah.create(
    access_key=porcupine_key,
    endpoint_duration_sec=ENDPOINT_DURATION_SECONDS,
    enable_automatic_punctuation=True)

recorder = PvRecorder(
    frame_length=512,
    device_index=AUDIO_DEVICE)

done_processing_query = False

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_response(query):
    byte_stream = elevenlabs.generate(
        text=query,
        voice=elevenlabs.Voice(
            voice_id="NILGfKSMoeL1zMLuhhAI",
        ),
        model="eleven_multilingual_v2",
    )

    bender_mp3_path = "/home/manuel/bender_test_mp3.mp3"
    elevenlabs.save(byte_stream, bender_mp3_path)

    global done_processing_query
    done_processing_query = True

# Speech-to-text using Picovoice's Cheetah
def capture_input():
    transcript = ''
    while True:
        partial_transcript, is_endpoint = cheetah.process(recorder.read())
        transcript += partial_transcript
        if is_endpoint:
            transcript += cheetah.flush()
            break
    return transcript

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

def generate_frame_data(x_positions, y_positions):
    frame_data = []
    for x, y in zip(x_positions, y_positions):
        row = int(y)
        col = int(x)
        frame_data.append((row, col))
    return frame_data

def update_plot(frame, wf, frames_per_buffer, full_res_mode, args, fig, line, x_freq):
    data = wf.readframes(frames_per_buffer)
    if len(data) == 0:
        plt.close(fig)
        return line,
    threading.Thread(target=play_audio_chunk, args=(data, wf.getnchannels(), wf.getsampwidth(), wf.getframerate())).start()
    data_np = np.frombuffer(data, dtype=np.int16) / 32768.0
    if data_np.shape[0] < frames_per_buffer:
        data_np = np.pad(data_np, (0, frames_per_buffer - data_np.shape[0]), 'constant', constant_values=(0, 0))
    fft_data = np.abs(np.fft.rfft(data_np)) / frames_per_buffer

    if args.output and not full_res_mode:
        discretized_fft = discretize_fft(fft_data, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(-8, 8)
        y_pos = mirrored_fft - 3.5
        frame_data = generate_frame_data(x_pos, y_pos)
        print(frame_data)
    elif full_res_mode:
        fft_data = np.concatenate((fft_data[:0:-1], fft_data))
        smoothed_fft = moving_average(fft_data, window_size=80)
        line.set_data(x_freq, smoothed_fft * 100)
    else:
        smoothed_fft = moving_average(fft_data, window_size=80)
        discretized_fft = discretize_fft(smoothed_fft, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(-8, 8)
        line.set_data(x_pos, mirrored_fft)
    return line,

def update_led(wf, frames_per_buffer, full_res_mode, args, fig, line, x_freq, counter, frame_skip):
    data = wf.readframes(frames_per_buffer)
    if counter != frame_skip:
        return True
    if len(data) == 0:
        plt.close(fig)
        return False
    # threading.Thread(target=play_audio_chunk, args=(data, wf.getnchannels(), wf.getsampwidth(), wf.getframerate())).start()
    data_np = np.frombuffer(data, dtype=np.int16) / 32768.0
    if data_np.shape[0] < frames_per_buffer:
        data_np = np.pad(data_np, (0, frames_per_buffer - data_np.shape[0]), 'constant', constant_values=(0, 0))
    fft_data = np.abs(np.fft.rfft(data_np)) / frames_per_buffer

    if args.output and not full_res_mode:
        discretized_fft = discretize_fft(fft_data, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(0, 17)
        y_pos = mirrored_fft
        frame_data = generate_frame_data(x_pos, y_pos)
        for pixel in frame_data:
            data = f"{pixel[0]}, {pixel[1]}\n"
            ser.write(data.encode('utf-8'))
            time.sleep(0.0035)
        # exit(0)
        # waveform = {
        #     'waveform_data': frame_data,
        # }
        # file_name = "/home/benderpi/bender_in_out/waveform_data.json"
        # print('saving')
        # with open(file_name, 'w') as file:
        #     # Acquire an exclusive lock
        #     fcntl.flock(file, fcntl.LOCK_EX)

        #     json.dump(waveform, file)
        # print(frame_data)
    elif full_res_mode:
        fft_data = np.concatenate((fft_data[:0:-1], fft_data))
        smoothed_fft = moving_average(fft_data, window_size=80)
        line.set_data(x_freq, smoothed_fft * 100)
    else:
        smoothed_fft = moving_average(fft_data, window_size=80)
        discretized_fft = discretize_fft(smoothed_fft, num_bands=8, num_rows=7)
        mirrored_fft = np.concatenate((discretized_fft[::-1], discretized_fft))
        x_pos = np.arange(-8, 8)
        line.set_data(x_pos, mirrored_fft)
    return True

def stream_openai(voice_transcription):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": PROMPT+voice_transcription,
            }
        ],
        model="gpt-3.5-turbo",
        stream = True,
    )
    for chunk in chat_completion:
        yield chunk.choices[0].message.content

def play_audio_file(args, bender_mp3_path):
    # Load an MP3 file
    audio = AudioSegment.from_file(bender_mp3_path)

    # Set the frame rate to 8000 Hz
    audio = audio.set_frame_rate(8000)

    # Export to a WAV file with the specified frame rate
    out_wav_path = "/home/manuel/bender_wav_test.wav"
    audio.export(out_wav_path, format="wav")

    wf = wave.open(out_wav_path, 'rb')

    full_res_mode = args.mode == 'full'

    fig, ax = plt.subplots()
    frames_per_buffer = 512
    x_freq = np.fft.rfftfreq(frames_per_buffer, 1 / wf.getframerate())

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
        ax.set_xlim(-wf.getframerate() // 2, wf.getframerate() // 2)
    else:
        line, = ax.plot(np.zeros(16), np.zeros(16), 'ko')
        ax.set_ylim(-1, 7)
        ax.set_xlim(-8, 7)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Magnitude')

    # Load a wave file
    wave_obj = sa.WaveObject.from_wave_file(out_wav_path)

    # Play the wave file
    play_obj = wave_obj.play()

    counter = 0
    frame_skip = 0
    while(update_led(wf, frames_per_buffer, full_res_mode, args, fig, line, x_freq, counter, frame_skip)):
        counter = counter + 1
        time.sleep(0.01)
        if counter == frame_skip + 1:
            counter = 0

def pic_request(voice_request):
    #  Path to your image
    # image_path = take_a_picture()
    image_path = "/home/manuel/cool_picture.png"

    # Getting the base64 string
    base64_image = encode_image(image_path)

    api_key = os.environ.get("OPENAI_API_KEY")

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": PROMPT+voice_request
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']



def main():
    parser = argparse.ArgumentParser(description="Symmetric FFT visualization centered on x and y axes.")
    parser.add_argument('--mode', type=str, default='discrete', choices=['full', 'discrete'], help='Visualization mode: full or discrete')
    parser.add_argument('--output', action='store_true', default=True, help='Enable output mode to get frame data as a list of tuples')
    parser.add_argument('--no-face-detect', action='store_true', help='No face tracking')
    args = parser.parse_args()

    print('Listening...')

    recorder.start()

    process = None

    playing_song = False

    # Start the face tracker
    if process is None:
        cmd = ['python', '/home/manuel/benderGPT/test_face_detection.py']
        print(args.no_face_detect)
        if args.no_face_detect:
            cmd.append('--no-tracking')
        print(cmd)
        process = subprocess.Popen(cmd)

    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if result >= 0:
            print('keyword detected')
            if playing_song:
                playing_song = stop_spotify()

            voice_transcription = capture_input()
            print(f"voice: {voice_transcription}")
            gpt_response = None

            if "terminate call" in voice_transcription.lower():
                recorder.stop()
                if process is not None:
                    process.terminate()
                break
            
            if "stop song" in voice_transcription.lower():
                stop_spotify()
                continue
            
            if "play" in voice_transcription.lower():
                voice_transcription = voice_transcription+"list the song and band in this format 'artist, <artist>, song, <song> - <your snarky response>'"

            if "take a picture" in voice_transcription.lower():
                # if process is not None:
                #     print("killing face detect")
                #     process.terminate()
                #     time.sleep(1)
                voice_request = voice_transcription.lower().split("take a picture")[1]
                gpt_response = pic_request(voice_request)
                # process = subprocess.Popen(['python', '/home/manuel/benderGPT/test_face_detection.py'])
            else:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": PROMPT+voice_transcription,
                        }
                    ],
                    model="gpt-3.5-turbo",
                )
                gpt_response = chat_completion.choices[0].message.content


            print(gpt_response)

            spotify_query = ""
            if "play" in voice_transcription.lower():
                spotify_query = gpt_response.split("-")[0]
                gpt_response = gpt_response.split("-")[1]

            # Start a thread to process the gpt query
            threading.Thread(target=generate_response, args=(gpt_response,)).start()

            # play a thinking file while that finishes
            random_thought = random.randint(1, 10)
            play_audio_file(args, f"/home/manuel/bender_thinking/thinking_{random_thought}.mp3")

            while True:
                global done_processing_query
                if done_processing_query:
                    play_audio_file(args, "/home/manuel/bender_test_mp3.mp3")
                    done_processing_query = False
                    break
            
            if "play" in voice_transcription.lower():
                playing_song = play_spotify_song(spotify_query)


if __name__ == '__main__':
    main()

