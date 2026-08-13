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
#pypdf extract text from pdf file

input_text = input("Enter text you would like to pull vocabualry from: ") #
word_type = input("What type of word would you like to learn?(verb, adjective, adverb, noun): ")
#add most frequent. suggest for use with larger texts only such as pdf
source = input("Language of the input text: ") 
#target = input("What language would you like to translate the vocabulary words into?: ") 
amount = input("How many words would you like to have in your deck?(define with number or write 'all' to retrieve all insances): ")
include_details = input("Would you like to include the morphological feature for each word in your deck?[y/n]: ")
#deck_name = input("Name your flashcard deck: ") # enter an exisiting deck to append new cards?


def find_pos(word_type):
    if word_type.lower() == "adjective":
        pos = "ADJ"
    if word_type.lower() == "adverb":
        pos = "ADV"
    if word_type.lower() == "noun":
        pos = "NOUN"
        #its possible to sort by word gender
    if word_type.lower() == "verb":
        pos = "VERB"
        # matcher
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
    if str(source).lower() == "ukrainian":
        source_lang = spacy.load("uk_core_news_sm")
        return source_lang
    if str(source).lower() == "french":
        source_lang = spacy.load("fr_core_news_sm")
        return source_lang
    #if str(source).lower() == "chinese":
     #   source_lang = spacy.load("zh_core_web_sm")
      #  return source_lang
    else:
        return("Language not supported")

# Load the pre-trained model
nlp = define_lang(source)
#tnlp = define_lang(target) # for translation (back of flashcard)
# Process the sentence
doc = nlp(input_text)
pos = find_pos(word_type)
wanted_words= [] # list of all words that match the desired word type
# to do: make cards a class with named positional features
cards= [] # random selected vocabualry words from text 
two_sides = {} # dictionary of target language words with transations
#print(doc)

#class Card():
#    def __init__(self,):

verb_pattern_matcher = [{}]
#for verbs it would make sense to add token.text with morphological features AND token.lemma_
#this would reduce the need to include several tables in different tenses, but gives the user more context
#there is no good data set for conjugating verbs especially in non-english or ambiguous tokens

def get_mor_lem(token): # gathers then returns token lemma and token with features the way it appeared in source text
    tex = token.text
    mor = token.morph
    lem = token.lemma_
    mor_lem = (lem, tex, mor)
    return(mor_lem)

for token in doc:
    #print(token.pos_)
    if token.pos_ == pos:
        if token.lemma_ not in wanted_words:
            if include_details == "y":
                wanted_words.append(get_mor_lem(token))
            #match
            # wanted_words.append(match)
            else:
                wanted_words.append(token.lemma_)

count = len(wanted_words)
if str(amount).lower() == "all":
    confirm1 = input(f"There are {count} unique {word_type}s. Are you sure you would like to add all to your deck?[y/n]: ")
    if confirm1 == "y":
        for word in wanted_words:
            cards.append(word)
    else:
        amount = input("Specify amount: ")
        cards.append(sample(wanted_words, int(amount)))
elif int(amount) >= len(wanted_words):
    amount = input(f"There are {count} unique {word_type}s and you wanted {amount} words. Specify new amount (maximum {count}): ")
    cards.append(sample(wanted_words, int(amount)))
else:
    cards.append(sample(wanted_words, int(amount)))

#print(wanted_words)
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
