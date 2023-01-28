import nltk
import numpy as np

#nltk.download('punkt')
from nltk.stem.porter import PorterStemmer 
stemer =PorterStemmer() #creer stemer
def tokenize(sentence):
    return nltk.word_tokenize(sentence)

def stem(word):
    return stemer.stem(word.lower())
def bag_of_words(tokenized_sentence,all_words):
    """
        sentence =["hello","how","are","you" ]
        words=["hi","hello","I","you","bye","thank","cool"]
        bag=[0,1,0,1,0,0,0]
    """
    tokenized_sentence=[stem(w) for w in tokenized_sentence]
    bag =np.zeros(len(all_words),dtype=np.float32)
    for idx,w in enumerate(all_words):
      if w in tokenized_sentence:
          bag[idx]=1.0
    return bag

# a="Can I pay with Paypal?"
# a=tokenize(a)
# print(a)
# words=["organize","organizes","organizing"]
# stemmed_words=[stem(w) for w in words]
# print (stemmed_words)
# ['organ', 'organ', 'organ']

# sentence =["hello","how","are","you" ]
# words=["hi","hello","I","you","bye","thank","cool"]
# bag=bag_of_words(sentence,words)
# print(bag) bag=[0,1,0,1,0,0,0]