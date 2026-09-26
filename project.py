import nltk, pprint, random, spacy, asyncio, subprocess, sys, os
from random import sample
from spacy.matcher import Matcher
from nltk.tokenize import word_tokenize
from pypdf import PdfReader
from pathlib import Path
from collections import Counter
from functions import *

textfile_on = input("\nWould you like to use a filepath (y/n)?:\n") #produces a boolean which is used later for sentences processing  
if textfile_on.lower() == "y":
    user_input = input("\nPlease input the filepath of the text from which to extract vocabulary:\n") 
    if user_input == "":
        quit()
    elif not Path(user_input).suffix.lower() == ".txt" and not Path(user_input).suffix.lower() == ".pdf":
        raise ValueError("file format is not supported")
if textfile_on != "n" and textfile_on != "y":
    quit()
elif textfile_on == "n" :
    input_text = input("\nEnter text you would like to pull vocabualry from:\n") #raw string input from user
    if input_text == "":
        quit()

dpl = input("\nWould you like to use a DeepL API key[y/n]:\n")
if dpl == "":
    quit()
source = input("\nLanguage of the input text:\n")
if source == "":
    quit()
elif dpl.lower() == "y":
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_DIR = os.path.join(OUTPUT_DIR, "Vocab_Config")
    AUTH_FILE = os.path.join(CONFIG_DIR, "deepl_authentication_key.txt")
    
    auth = ""

    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as file:
            auth = file.read()
        
    if not auth:
        auth = input("\nPlease provide a DeepL API key\n")
        if auth == "":
            quit()
        with open(AUTH_FILE, "w") as file: 
            file.write(auth)
            
    target = input("\nWhat language would you like to translate the vocabulary words into?:\n")
    if target == "":
        quit()
word_type = input("\nWhat type of word would you like to learn?(verb, adjective, adverb, noun):\n")
if word_type == "":
    quit()
include_details = input("\nWould you like to include the morphological features for each word in your deck?[y/n]:\n")
if include_details == "":
    quit()

# Load the pre-trained model
nlp = load_lang(source)

# Process the sentence
if textfile_on.lower() == "y":   
    file_path = Path(user_input)
    if file_path.suffix.lower() == ".txt": #use pathlib (previously regex) to check file format. supported file formats are currently: txt, pdf
        with open(file_path, "r", encoding="utf-8") as file:
            doc = nlp(file.read())
    elif file_path.suffix.lower() == ".pdf": #use pypdf to open pdf files and extract text
        reader = PdfReader(file_path)
        #number_of_pages = len(reader.pages)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        doc = nlp(text)
    else:
        raise ValueError("file format is not supported")
else:
    doc = nlp(input_text)# raw input text

pos = find_pos(word_type)
wanted_words= [] # list of all words that match the desired word type
vocab_list= [] # random selected vocabualry words from text 
cards = {} # dict of card with lemma as key, sentence where word appears in source text plus additional features as value list 
# key = lemma_ . value = [translation, text, morph] 

lemmas = []
seen_fronts = load_seen_fronts()
skip_counter = 0

sentences = [sent.text for sent in doc.sents]

for token in doc:
    if token.pos_ == pos:
        if not token.is_punct and not token.is_space and not token.is_digit: #filters out unwandted characters (!; .; \n; etc...)
            if token.lemma_ not in lemmas and token.lemma_ not in seen_fronts:
                lemmas.append(token.lemma_)
                ex_sen = []
                for sentence in sentences:
                    if str(token.text) in sentence:
                        ex_sen.append(sentence)
                s = random.choice(ex_sen)
                if include_details.lower() == "y":
                    wanted_words.append([token.lemma_, token.text, s, str(token.morph)])
                else:
                    wanted_words.append([token.lemma_, token.text, s])
            elif token.lemma_ in seen_fronts:
                skip_counter += 1

count = len(wanted_words)
if count == 0:
    print("No new words were found")
    raise SystemExit

amount = input(f"\nThere are {count} unique {word_type}s. How many words would you like to learn?(number or 'all'):\n")
if amount == "":
    quit()
elif amount.lower() == "all":
    for word in wanted_words:
        vocab_list.append(word)
else:
    for word in sample(wanted_words, int(amount)):
        vocab_list.append(word)
        

#pull token.lemma_ for translation
vocab = [item[0] for item in vocab_list]

pprint.pprint(vocab_list)

if dpl.lower() == "n":
    print("\n",', '.join(map(str, vocab)))
    translations = input("\nPlease translate the tokens and paste them here:\n")
    if translations == "":
        quit()
    else:
        translations = list([x.strip() for x in translations.split(',')])
else:
    translations = deepl_vocab_translation(auth, vocab, source, target)

i = 0
for item in vocab_list:
    item.insert(1, translations[i])
    i += 1
#print(vocab_list)

for item in vocab_list:
    cards.update({item[0] : item[1:]})

deck_name = input("\nName your flashcard deck: ") # enter an exisiting deck to append new cards? #
if deck_name == "":
    deck_name == input("\nYou must name your deck or enter the name of an existing deck to continue:\n") 
    if deck_name == "":
        quit()

print("\n")
#pprint.pprint(cards)
print("\n")
build_cards(cards, deck_name)
print(f"Total skipped: {skip_counter}")
