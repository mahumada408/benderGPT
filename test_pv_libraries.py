import os
import pvporcupine, pvcheetah
from pvrecorder import PvRecorder

ENDPOINT_DURATION_SECONDS = 2 # 'Quiet' seconds indicating the end of audio capture
AUDIO_DEVICE = "Plugable USB Audio Device Analog Stereo"
MIC_INDEX = 3
porcupine_key = os.environ.get("PORCUPINE_API_KEY")

porcupine = pvporcupine.create(
    access_key=porcupine_key,
    keywords=['terminator'])

cheetah = pvcheetah.create(
    access_key=porcupine_key,
    endpoint_duration_sec=ENDPOINT_DURATION_SECONDS,
    enable_automatic_punctuation=True)

recorder = PvRecorder(
    frame_length=512,
    device_index=MIC_INDEX)

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

def main():
    print('Listening...')

    recorder.start()

    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if result >= 0:
            print('keyword detected')
            script = capture_input()
            print(script)

if __name__ == '__main__':
    main()

