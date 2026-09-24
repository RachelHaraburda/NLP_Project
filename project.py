import nltk, pprint, random, spacy, asyncio, subprocess, sys
from random import sample
from spacy.matcher import Matcher
from nltk.tokenize import word_tokenize
from pypdf import PdfReader
from pathlib import Path
from collections import Counter
from functions import load_lang, find_pos, deepl_vocab_translation, build_cards

textfile_on = input("\nWould you like to use a filepath (y/n)?:\n").lower() == "y" #produces a boolean which is used later for sentences processing  
if textfile_on == "":
    quit()
elif textfile_on:
    user_input = input("\nPlease input the filepath of the text from which to extract vocabulary:\n") 
    if user_input == "":
        quit()
    elif not Path(user_input).suffix.lower() == ".txt" and not Path(user_input).suffix.lower() == ".pdf":
        raise ValueError("file format is not supported")

else:
    input_text = input("\nEnter text you would like to pull vocabualry from:\n") #raw string input from user
    if input_text == "":
        quit()

source = input("\nLanguage of the input text:\n") 
if source == "":
    quit()
own_translate = input("\nWould you like to use your own translator?[y/n]:\n")
if own_translate == "":
    quit()
elif own_translate.lower() == "n":
    auth = input("\nPlease provide a DeepL API key\n")
    target = input("\nWhat language would you like to translate the vocabulary words into?:\n")
    if target == "":
        quit()
word_type = input("\nWhat type of word would you like to learn?(verb, adjective, adverb, noun):\n")
if word_type == "":
    quit()
include_details = input("\nWould you like to include the morphological features for each word in your deck?[y/n]:\n")
if include_details == "":
    quit()
deck_name = input("\nName your flashcard deck: ") # enter an exisiting deck to append new cards? #
if deck_name == "":
    deck_name == input("\nYou must name your deck or enter the name of an existing deck to continue:\n") 
    if deck_name == "":
        quit()

# Load the pre-trained model
nlp = load_lang(source)

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
# key = lemma_ . value = [translation, text, morph] 

lemmas = []

for token in doc:
    if token.pos_ == pos:
        if not token.is_punct and not token.is_space: #filters out unwandted characters (!; .; \n; etc...)
            if token.lemma_ not in lemmas:
                lemmas.append(token.lemma_)
                if include_details.lower() == "y":
                    wanted_words.append([token.lemma_, token.text, str(token.morph)])
                else:
                    wanted_words.append([token.lemma_, token.text])

count = len(wanted_words)
amount = input(f"\nThere are {count} unique {word_type}s. How many words would you like to learn?(number or 'all'):\n")
if amount == "":
    quit()
elif amount == "all":
    for word in wanted_words:
        vocab_list.append(word)
else:
    for word in sample(wanted_words, int(amount)):
        vocab_list.append(word)
        

#pull token.text for translation
vocab = [item[1] for item in vocab_list] # sort out lemmas for translation


#temp to delete print("\n", vocab, type(vocab)) #[['autore', 'autori', Gender=Masc|Number=Plur]] <class 'list'>
pprint.pprint(vocab_list)

if own_translate.lower() == "y":
    print("\n")
    print('[{}]'.format(', '.join(vocab)))
#test for inserting translations and converting to cards dictionary
    translations = input("\nPlease translate the tokens and paste them here:\n")
    translations = list([x.strip() for x in translations.split(',')])
    print("\n",translations)
else:
    translations = deepl_vocab_translation(auth, vocab, source, target)

i = 0
for item in vocab_list:
    item.insert(1, translations[i])
    i += 1
#print(vocab_list)

for item in vocab_list:
    cards.update({item[0] : item[1:]})

print("\n")
pprint.pprint(cards)
print("\n")
build_cards(cards, deck_name)
