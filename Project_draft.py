import nltk, pprint, random, spacy, asyncio
from random import sample
from spacy.matcher import Matcher
from nltk.tokenize import word_tokenize
from pypdf import PdfReader
from pathlib import Path
#from translator import *
#from anki_test import *

#auth = input("Please provide a DeepL API key\n")

textfile_on = input("Would you like to use a filepath (y/n)?:\n").lower() == "y" #produces a boolean which is used later for sentences processing  
if textfile_on == "":
    quit()
elif textfile_on:
    user_input = input("Please input the filepath of the text from which to extract vocabulary:\n") 
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
"""deck_name = input("Name your flashcard deck: ") # enter an exisiting deck to append new cards? #
if deck_name == "":
    deck_name == input("You must name your deck or enter the name of an existing deck to continue:\n") 
    if deck_name == "":
        quit()"""

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
    else:
        raise ValueError("Language not supported")

# Load the pre-trained model
nlp = load_lang(source)

def get_mor(token): # gathers then returns token lemma and token with features the way it appeared in source text
    return([token.morph])

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
        if token.lemma_ not in lemmas:
            lemmas.append(token.lemma_)
            if include_details.lower() == "y":
                wanted_words.append([token.lemma_, token.text, get_mor(token)])
            else:
                wanted_words.append([token.lemma_, token.text])

count = len(wanted_words)

if str(amount).lower() == "all":
    confirm2 = input(f"There are {count} unique {word_type}s. Are you sure you would like to add all to your deck?[y/n]: ")
    if confirm2 == "y":
        for word in wanted_words:
            vocab_list.append(word)
    elif confirm2 == "":
        quit()
    else:
        amount = input("Specify amount: ")
        if amount == "":
            quit()
        else:
            vocab_list.append(sample(wanted_words, int(amount)))
elif int(amount) >= len(wanted_words):
    amount = input(f"There are {count} unique {word_type}s and you wanted {amount} words. Specify new amount (maximum {count}): ")
    if amount == "":
        quit()
    for word in sample(wanted_words, int(amount)):
        vocab_list.append(word)
else:
    for word in sample(wanted_words, int(amount)):
        vocab_list.append(word)

#pull token.text for translation
vocab = [item[1] for item in vocab_list] # sort out lemmas for translation

pprint.pprint(vocab_list)

print('[{}]'.format(', '.join(vocab)))
#test for inserting translations and converting to cards dictionary
"""translations = input("translated tokens here:\n")
translations = list([x.strip() for x in translations.split(',')])
print(translations)
i = 0
for item in vocab_list:
    item.insert(1, translations[i])
    i += 1
#print(vocab_list)

for item in vocab_list:
    cards.update({item[0] : item[1:]})

#print(deepl_vocab_translation(auth, vocab, source, target))
print(cards)"""

"""
#Build decks
seen_fronts = load_seen_fronts() 
total_added = 0  
total_skipped = 0 

new_word_count = 0 
for deck_name, data in cards.items():    
    for english in data: 
        if f"{deck_name}|{english}" not in seen_fronts:   
            new_word_count += 1

if new_word_count == 0: 
    print("No new words found. Everything has already been exported.")
    raise SystemExit  #stops the script from running further

answer = input(f"Found {new_word_count} new word(s). Add them to the deck? (y/n): ").strip().lower()
if answer not in ("y", "yes"):  
    print("Cancelled. Nothing was added or exported.")
    raise SystemExit

for deck_name, data in cards.items(): 
    deck = genanki.Deck( #creates a new(same) deck, every time the script runs
        random.randrange(1 << 30, 1 << 31),
        f"{deck_name} Vocabulary"
    )

    added_count = 0 
    skipped_count = 0 

    # Verbs
    if pos == "VERB":
        for english, (target, example) in data.get.items():
            key = f"{deck_name}|{english}"
            if key in seen_fronts:
                    print(f"[{deck_name}] Skipped (duplicate): {english}")
                    skipped_count += 1
                    continue
            morphology = describe_morphology(target, deck_name)
            note = genanki.Note(model=verb_model, fields=[english, target, example, morphology])
            deck.add_note(note)
            seen_fronts.add(key)
            added_count += 1
            print(f"[{deck_name}] Added [verb]: {english} -> {target} | {morphology}")

    # Nouns
    if pos == "NOUN":
        for english, target in data.get.items():
            if key in seen_fronts:
                print(f"[{deck_name}] Skipped (duplicate): {english}")
                skipped_count += 1
                continue
            article = get_article(target, deck_name) #auto-detected instead of read from the dictionary
            morphology = describe_morphology(target, deck_name)
            note = genanki.Note(model=noun_model, fields=[english, article, target, morphology])
            deck.add_note(note)
            seen_fronts.add(key)
            added_count += 1
            print(f"[{deck_name}] Added [noun]: {english} -> {article} {target} | {morphology}")
    # Words
    else:
        for english, target in data.get.items():
            key = f"{deck_name}|{english}"
            if key in seen_fronts: 
                print(f"[{deck_name}] Skipped (duplicate): {english}") 
                skipped_count += 1
                continue 
            morphology = describe_morphology(target, deck_name) #generate mophology for the back of the flashcard
            note = genanki.Note(model=word_model, fields=[english, target, morphology]) #builds flashcard data
            deck.add_note(note) 
            seen_fronts.add(key) #prevents duplicates next time
            added_count += 1
            print(f"[{deck_name}] Added [word]: {english} -> {target} | {morphology}") 

    if added_count > 0: 
        output_path = os.path.join(OUTPUT_DIR, f"{deck_name.lower()}_vocab.apkg") 
        genanki.Package(deck).write_to_file(output_path) #exports the deck with its notes writes it as .apkg
        print(f"[{deck_name}] Deck saved as {output_path} ({added_count} new notes)")
    else:
        print(f"[{deck_name}] No new cards to add. Nothing exported.")

    total_added += added_count 
    total_skipped += skipped_count

save_seen_fronts(seen_fronts)

print(f"\nTotal added: {total_added}")
print(f"Total skipped: {total_skipped}")
"""
