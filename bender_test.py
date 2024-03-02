import argparse
import os
from elevenlabs import generate, play, voices, Voice, VoiceSettings, set_api_key, get_api_key, User, stream, save
from openai import OpenAI

PROMPT = "You are Bender from Futurama. Respond to my query in a snarky Bender way in 100 characters or less: "
QUERY = "Hey bender. How did your day go?"

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

parser = argparse.ArgumentParser(description='A snarky Python script with argparse.')

parser.add_argument('--query', help='GPT query.')
parser.add_argument('--passthrough', action='store_true', help='Passes throught the query')

args = parser.parse_args()

gpt_response = args.query
if not args.passthrough:
  chat_completion = client.chat.completions.create(
      messages=[
          {
              "role": "user",
              "content": PROMPT+args.query+"!!",
          }
      ],
      model="gpt-3.5-turbo",
  )
  gpt_response = chat_completion.choices[0].message.content

print(gpt_response)

user = User.from_api()
left = user.subscription.character_limit - user.subscription.character_count
print(left)

# audio = generate(
#   text=gpt_response,
#   voice=Voice(
#     voice_id="NILGfKSMoeL1zMLuhhAI",
#     settings=VoiceSettings(stability=0.18, similarity_boost=0.75, style=0.5, use_speaker_boost=True)
#   ),
#   model="eleven_multilingual_v2",
#   stream=True,
# )

audio = generate(
  text=gpt_response,
  voice=Voice(
    voice_id="NILGfKSMoeL1zMLuhhAI",
  ),
  model="eleven_multilingual_v2",
)

play(audio)
bender_mp3_path = "/home/manuel/thinking_10.mp3"
save(audio, bender_mp3_path)

user = User.from_api()
left = user.subscription.character_limit - user.subscription.character_count
print(left)