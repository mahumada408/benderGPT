from time import time
import os

import elevenlabs
import pvporcupine, pvcheetah
from pvrecorder import PvRecorder
from pygame import mixer
from openai import OpenAI

ENDPOINT_DURATION_SECONDS = 2 # 'Quiet' seconds indicating the end of audio capture
AUDIO_DEVICE_NAME = "Plugable USB Audio Device Analog Stereo"
AUDIO_DEVICE = PvRecorder.get_available_devices().index(AUDIO_DEVICE_NAME)
porcupine_key = os.environ.get("PORCUPINE_API_KEY")

PROMPT = "You are Bender from Futurama. Respond to my query in a snarky Bender way in 100 characters or less: "
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
            voice_transcription = capture_input()
            print(f"voice: {voice_transcription}")

            if "terminate call" in voice_transcription.lower():
                recorder.stop()
                break

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

            print(f"GPT: {gpt_response}")

            # Generate audio from eleven labs
            audio = elevenlabs.generate(
                text=gpt_response,
                voice=elevenlabs.Voice(
                    voice_id="NILGfKSMoeL1zMLuhhAI",
                ),
                model="eleven_multilingual_v2",
            )

            # Convert response to audio
            current_time = time()
            elevenlabs.save(audio, "/home/benderpi/bender_test.wav")
            audio_time = time() - current_time
            print(f"Finished generating audio in {audio_time:.2f} seconds.")

            user = User.from_api()
            left = user.subscription.character_limit - user.subscription.character_count
            print(left)

if __name__ == '__main__':
    main()

