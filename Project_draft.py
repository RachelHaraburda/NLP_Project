import nltk, pprint, random, spacy, asyncio
#import stanza
from random import sample
from spacy.matcher import Matcher
from nltk.tokenize import word_tokenize
from googletrans import Translator
from pypdf import PdfReader
from pathlib import Path

#pypdf extract text from pdf file
# reference: the front of the card: token lemma
# back: translation
# expandable bar at the bottom of the screen: word in sentence as it appears in the source text with morphological features if desired 

textfile_on = input("Would you like to use a filepath (y/n)?:\n").lower() == "y" #produces a boolean which is used later for sentences processing  
if textfile_on == "":
    quit()
elif textfile_on:
    user_input = input("Please input the filepath of the text from which to extract the vocabulary:\n") 
    if user_input == "":
        quit()
    elif not Path(user_input).suffix.lower() == ".txt" and not Path(user_input).suffix.lower() == ".pdf":
        raise ValueError("file format is not supported")

else:
    input_text = input("Enter text you would like to pull vocabualry from:\n") #raw string input from user
    if input_text == "":
        quit()

word_type = input("What type of word would you like to learn?(verb, adjective, adverb, noun):\n")
if word_type == "":
    quit()
#add most frequent. suggest for use with larger texts only such as pdf
source = input("Language of the input text:\n") 
if source == "":
    quit()
target = input("What language would you like to translate the vocabulary words into?:\n")
if target == "":
    quit()
amount = input("How many words would you like to learn?(define with number or write 'all' to retrieve all insances):\n")
if amount == "":
    quit()
include_details = input("Would you like to include the morphological features for each word in your deck?[y/n]:\n")
if include_details == "":
    quit()
#make_deck = input("Do you want to make a flashcard deck")
#deck_name = input("Name your flashcard deck: ") # enter an exisiting deck to append new cards? #


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
        #matcher
    return pos
# for verbs add pattern match to include ADP ex. get off, wait on
# no available tag for prepositions with pos alone

def define_lang(l):
    if str(l).lower() == "english":
        l = "en"
        return l
    if str(l).lower() == "german":
        l = "en"
        return l
    if str(l).lower() == "russian":
        l = "ru"
        return l
    if str(l).lower() == "ukrainian":
        l = "uk"
        return l
    if str(l).lower() == "french":
        l = "fr"
        return l
    #if str(l).lower() == "chinese":
      #  return l
    else:
        return("Language not supported")
    
def load_lang(source):
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
    if str(source).lower() == "italian":
        source_lang = spacy.load("it_core_news_sm")
        return source_lang
    #if str(source).lower() == "chinese":
     #   source_lang = spacy.load("zh_core_web_sm")
      #  return source_lang
    else:
        raise ValueError("Language not supported")

# Load the pre-trained model
nlp = define_lang(source)
#tnlp = define_lang(target) # for translation (back of flashcard)

source = define_lang(source)
target = define_lang(target) # for translation (back of flashcard)

def get_tex_mor(token): # gathers then returns token lemma and token with features the way it appeared in source text
    tex = token.text
    mor = token.morph
    tex_mor = (tex, mor)
    return(tex_mor)
    #return((token.text, token.morph))

def pull_sentence(token):
    [sentence + '.' for sentence in source.split('.') if token in sentence] # stackoverflow Python how to extract sentence containing a word

#lt = LibreTranslateAPI("https://translate.terraprint.co/")
#lt.translate(token.lemma_, source, target)

lemmas = []
words = []

def translated_text(words):
    trans = GoogleTranslator(source= source, target= target).translate_batch(words)
    return trans

# Process the sentence
if textfile_on:   
    file_path = Path(user_input)
    if file_path.suffix.lower() == ".txt": #use pathlib (previously regex) to check file format. supported file formats are currently: txt, pdf
        with open(file_path, "r") as file:
            doc = nlp(file.read())
    elif file_path.suffix.lower() == ".pdf": #use pypdf to open pdf files and extract text
        reader = PdfReader(file_path)
        #number_of_pages = len(reader.pages)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        #text = page.extract_text()
        doc = nlp(text)
    else:
        raise ValueError("file format is not supported")
else:
    doc = nlp(input_text)# raw input text

pos = find_pos(word_type)
wanted_words= [] # list of all words that match the desired word type
vocab_list= [] # random selected vocabualry words from text 
cards = {} # dict of card with lemma as key, sentence where word appears in source text plus additional features as value list 
# key = lemma_ . value = [translation, text, morph, sentance] 
# value.append

for token in doc:
    #print(token.pos_) 
        if token.pos_ == pos:
            if token.lemma_ not in wanted_words:
                if include_details.lower() == "y":
                    card = (token.lemma_, get_tex_mor(token))#(token.lemma_, translation, get_tex_mor)
                    wanted_words.append(card)
                else:
                    card = (token.lemma_)#, translation)
                    wanted_words.append(card)

count = len(wanted_words)

if str(amount).lower() == "all":
    confirm2 = input(f"There are {count} unique {word_type}s. Are you sure you would like to add all to your deck?[y/n]: ")
    if confirm2 == "y":
        for word in wanted_words:
            vocab_list.append(word)
    elif confirm2 == "":
        quit
    else:
        amount = input("Specify amount: ")
        vocab_list.append(sample(wanted_words, int(amount)))
elif int(amount) >= len(wanted_words):
    amount = input(f"There are {count} unique {word_type}s and you wanted {amount} words. Specify new amount (maximum {count}): ")
    if amount == "":
        quit()
    vocab_list.append(sample(wanted_words, int(amount)))
else:
    vocab_list.append(sample(wanted_words, int(amount)))


#batch translate (vocab_list)

pprint.pprint(vocab_list) 
#print(cards)

