import speech_recognition as sr
from gtts import gTTS

r=sr.Recognizer()

tts =gTTS(text=audio_string , lang='en')
with sr.Microphone() as source:
    print('Say something')
    audio =r.listen(source)
    voice_data= r.recognize_google(audio)
    print(voice_data)