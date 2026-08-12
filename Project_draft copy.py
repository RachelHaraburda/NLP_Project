import nltk
#import stanza
import random
from random import sample
import spacy
from spacy_langdetect import LanguageDetector
from spacy.matcher import Matcher
from nltk.collocations import *
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

input_text = input("Paste in the text you would like to pull vocabualry from: ") #
word_type = input("What type of word would you like to learn?(verb, adjective, adverb, noun): ")
source = input("Language of the input text: ") 
#target = input("What language would you like to translate the vocabulary words into?: ") 
amount = int(input("How many words would you like to have in your deck?: "))

def find_pos(word_type):
    if word_type.lower() == "adjective":
        pos = "ADJ"
    if word_type.lower() == "adverb":
        pos = "ADV"
    if word_type.lower() == "noun":
        pos = "NOUN"
    if word_type.lower() == "verb":
        pos = "VERB"
    return pos
# for verbs add pattern match to include ADP ex. get off, wait on
# no available tag for prepositions with pos alone
# other option: all word_types matchers include detailed tags for chunking / check dependancies
def define_lang(source):
    #print(source)
    if str(source).lower() == "english":
        source_lang = spacy.load("en_core_web_sm")
        return source_lang
    if str(source).lower() == "german":
        source_lang = spacy.load("de_core_news_sm")
        return source_lang
    if str(source).lower() == "russian":
        source_lang = spacy.load("ru_core_news_sm")
        return source_lang
    else:
        return("Language not supported")

# Load the pre-trained model
nlp = define_lang(source)

# Process the sentence
doc = nlp(input_text)

# Iterate through the document and print the tags
#for token in doc:
    #print(f"Word: {token.text}, POS: {token.pos_}, Detailed Tag: {token.tag_}")


 # convert text to lowercase for processing. Might be unnessecary/ hurtful expecially in German
pos = find_pos(word_type)
wanted_words= [] # list of all words that match the desired word type
cards= [] # random selected vocabualry words from text 
two_sides = {} # dictionary of target language words with transations
#print(doc)
for token in doc:
    #print(token.pos_)
    if token.pos_ == pos:
        if token.text not in wanted_words:
                wanted_words.append(token.text)

cards.append(sample(wanted_words, amount))
print(wanted_words)
print(cards)

"""for c in cards:
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

print(translation('bicycle', pos='n', lang='fra'))"""
