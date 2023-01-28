import random
import json
import webbrowser
import torch
import speech_recognition as sr
import time
import playsound
import os
import random
from gtts import gTTS
from time import ctime
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"




r=sr.Recognizer()



# while 1:
#     voice_data = record_audio()
#     respond(voice_data)


def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    print(sentence[0])
    if sentence[0] == "search":
                    s=""
                    for sent in sentence:
                        s=s+" "+sent

                    url = f"https://google.com/search?q={s}"
                    webbrowser.get().open(url)
                    return "ok, I will show you google"

    if sentence[0] == "youtube":
                s=""
                for sent in sentence:
                        s=s+" "+sent
                url=f"https://www.youtube.com/results?search_query={s} "
                webbrowser.get().open(url)
                return "ok, I will show you youtube"
    if  sentence[0]== "maps":
                s=[]
                for sent in sentence:
                        s.append(sent)
                s.remove('maps')
                print(s)
                s=" ".join(s) 
                url=f"https://www.google.fr/maps/place/{s}/@33.8819669,9.560764,6z"
                webbrowser.get().open(url)
                return "ok, I will show you maps"
    if sentence[0]=="vocal":

        class person:
            name = ''
            def setName(self, name):
                self.name = name
        class location:
            lieu = ''
            def setLieu(self,lieu):
                self.lieu = lieu

        def there_exists(terms):
            for term in terms:
                if term in voice_data:
                    return True
        def record_audio(ask=False):
                with sr.Microphone() as source:
                    if ask : 
                        sam_speak(ask)

                    audio =r.listen(source)
                    voice_data=''
                    try:
                        voice_data= r.recognize_google(audio)
                    except sr.UnknownValueError:
                            sam_speak('Sorry , I did not get that')
                    except sr.RequestError:
                            sam_speak('Sorry,I did not get that')
                    return voice_data
        def sam_speak(audio_string):
            tts =gTTS(text=audio_string , lang='en')
            r =random.randint(1,1000000)
            audio_file='audio-' + str(r) + '.mp3'
            tts.save(audio_file)
            playsound.playsound(audio_file)
            print(audio_string)
            os.remove(audio_file)
        def respond(voice_data):
            if there_exists(['hey','hi','hello']):
                greetings = [f"hey, how can I help you {person_obj.name}", f"hey, what's up? {person_obj.name}", f"I'm listening {person_obj.name}", f"how can I help you? {person_obj.name}", f"hello {person_obj.name}"]
                greet = greetings[random.randint(0,len(greetings)-1)]
                sam_speak(greet)



                if there_exists(["my name is"]):
                    person_name = voice_data.split("is")[-1].strip()
                    sam_speak(f"okay, i will remember that {person_name}")
                    person_obj.setName(person_name) # remember name in person object

                # 3: greeting
                if there_exists(["how are you","how are you doing"]):
                    sam_speak(f"I'm very well, thanks for asking {person_obj.name}")

                
                if 'find camping' in voice_data:
                    sam_speak("sousse sidi bou ali , in jendouba , in mahdia ")
                if 'weather in' in voice_data:
                    lieu = voice_data.split("in")[-1].strip()
                    sam_speak(f" {lieu} is perfect ")
                    location.setLieu(lieu)
                if there_exists([f"find hotels in {location.lieu}"]):
                    sam_speak(f"there is many hotels like ... ")

                if 'search' in voice_data:
                    search =record_audio('what do you want to search for?')
                    url ='https://google.com/search?q='+search
                    webbrowser.get().open(url)
                    sam_speak('Here is what i found for' + search)
               
                if 'exit' in voice_data:
                    exit()
        time.sleep(1)
        person_obj = person()
        location=location()
        sam_speak ('how can I help you?')
        while 1:
                voice_data = record_audio()
                respond(voice_data)  
    return "I do not understand..."
   


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)

# if 'find location' in voice_data:
                #     sam_speak("sousse sidi bou ali , in jendouba , in mahdia ")
 # if 'find location' in voice_data:
                #     location =record_audio('what is the location ?')
                #     url ='https://google.nl/maps/place/'+location+'/&amp;'
                #     webbrowser.get().open(url)
                #     sam_speak('Here is the loacation' + location)
                # 2: name
                # if there_exists(["what is your name","what's your name","tell me your name"]):
                #     if person_obj.name:
                #         sam_speak ("my name is Alexis")
                #     else:
                #         sam_speak("my name is Alexis. what's your name?")
 # if 'what time is it' in voice_data:
                #     sam_speak(ctime())