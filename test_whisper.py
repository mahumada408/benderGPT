# This is to test OpenAI's whisper model

import whisper

model = whisper.load_model("tiny")
result = model.transcribe("/home/pi/benderGPT/out2.wav")
print(f' The text in video: \n {result["text"]}')