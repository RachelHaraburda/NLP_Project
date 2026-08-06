import nltk
#import stanza
import random
from random import sample
import spacy
#from spacy_langdetect import LanguageDetector
from spacy.matcher import Matcher
from nltk.collocations import *
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

input_text = input("Paste in the text you would like to pull vocabualry from: ") #
wordtype = input("What type of word would you like to learn?(verb, adjective, adverb): ")
lang = input("Language of the input text: ") # link to nltk abreviations?
native = input("What language would you like to translate the vocabulary words into?: ") 
amount = int(input("How many words would you like to have in your deck?: "))

tokens = word_tokenize(input.lower()) # convert text to lowercase for processing. Might be unnessecary/ hurtful expecially in German
wanted_words= [] # list of all words that match the desired word type
cards= [] # random selected vocabualry words from text 
two_sides = {} # dictionary of target language words with transations
for token in tokens:
    if token == wordtype:
        wanted_words.append(token)
    for word in wanted_words:
        cards.append(sample(wanted_words, {amount}))

for c in cards:
    vocab = translation(token, pos = wordtype, lang)
    two_sides.update(c, vocab)

#def translation_(word, pos, lang= lang): desired is the input variables can be inputed into the function

# example of how the translation can work from homework 4 exercise 2
def translation(word, pos= wordtype, lang= lang):
    target = lang
    translation = []
    for synset in wn.synsets(word, pos, lang= 'eng'):
        for flemma in synset.lemmas(lang = target):
            word = flemma.name()
            if word not in translation:
                translation.append(word)
    return sorted(translation, key = str.lower)

print(translation('bicycle', pos='n', lang='fra'))


from ankiapi import AnkiApi

# Initialize the API (make sure Anki is running with AnkiConnect add-on)
anki = AnkiApi()

# Create a new deck
anki.create_deck("Python Programming")

# Add a flashcard
anki.add_flashcard(
    deck_name="Python Programming",
    front="What is a Python list comprehension?",
    back="A concise way to create lists using a single line of code with a for loop and optional conditions."
)