import pvporcupine, pvcheetah
from pvrecorder import PvRecorder

ENDPOINT_DURATION_SECONDS = 2 # 'Quiet' seconds indicating the end of audio capture

porcupine_key = os.environ.get("PORCUPINE_API_KEY")

cheetah = pvcheetah.create(
    access_key=porcupine_key,
    endpoint_duration_sec=ENDPOINT_DURATION_SECONDS,
    enable_automatic_punctuation=True)

recorder = PvRecorder(
    frame_length=porcupine.frame_length,
    device_index=AUDIO_DEVICE)

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

    script = capture_input()

if __name__ == '__main__':
    main()

