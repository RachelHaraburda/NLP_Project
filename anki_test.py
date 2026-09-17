import genanki
import random #generate large random integer for unique ID, Anki needs it to tell Models and Decks apart.
import json #tracks which words have been exported.
import os #finds the folder,checks if seen_fronts already exists before reading it.
import spacy

nlp_models = {
    "German": spacy.load("de_core_news_sm"),
    "Japanese": spacy.load("ja_core_news_sm"),
}
#cd "C:\Users\Calvi\Downloads\Python Project Folder"  .venv\Scripts\activate

def describe_morphology(text, lang_name):          
    nlp = nlp_models[lang_name]
    doc = nlp(text) #splits text into words/tokens as well as morphological feature
    parts = [] #list that collects morphology description
    for token in doc:
        if token.is_punct: #skips punctuation like  .  !  ? 
            continue
        tag = f"{token.pos_} ({token.morph})" if str(token.morph) else token.pos_ #token.pos is part of speech. token.morph is gramatical feature(eg, Case|Gender) if checks if there are morphological features if not just NOUN
        parts.append(tag) #adds the tag to parts list
    return "<br>".join(parts) #parts has the list, join makes 1 long string. br is \n in HTML  since Anki cards are HTML is can't be \n. return gives the result back.


SEEN_FILE = "seen_fronts.json" #remembers which words have been exported already, so no duplicates
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) #determines the folder path


def load_seen_fronts():   #returns the set of words, that have been exported already
    if os.path.exists(SEEN_FILE):  #checks if seen_fronts exists yet. Important on the very first time
        with open(SEEN_FILE, "r", encoding="utf-8") as f:   #utf because of german letters like ä, ö, ü
            return set(json.load(f))  #json.load reads the file's content. set() converts list into set, good to check duplicates. returns the functions result
    return set()   # if there is nothing saved in json eg. first ever run return an empty set


def save_seen_fronts(seen):  #takes 1 input which are the exported words
    with open(SEEN_FILE, "w", encoding="utf-8") as f:   #can overwrite the file
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2) #sorted(seen) converts set back to a list good for saving the file. ensure_ascii=False makes characters like ä readable


word_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31), #unique ID for the model. 1 << 30, 1 << 31 recommended by GenAnki
    "Word Model",
    fields=[{"name": "English"}, {"name": "Target"}, {"name": "Morphology"}], #Target = target language
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{English}}", #front
            "afmt": '{{FrontSide}}<hr id="answer">{{Target}}<br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>', #back, hr id="answer" draws horizontal line(starts a new line), Target inserts translation, br is a line break. 
        },                                                  #details creates an open collapsible container just like a folder for "show morphology". summary defines a clickable label Show morphology is clickable in Anki. small morphology displays morphological features in smaller font. details closes collapsible container
        {
            "name": "Card 2", #reverse
            "qfmt": "{{Target}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}}<br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>', #small so morphology is written smaller, hidden behind toggle
        },
    ],
)

noun_model = genanki.Model(  #want to see the article with the noun. Different type of flashcard
    random.randrange(1 << 30, 1 << 31),
    "Noun Model", # note type shown in Anki note type list
    fields=[{"name": "English"}, {"name": "Article"}, {"name": "Target"}, {"name": "Morphology"}],
    templates=[
        {
            "name": "Card 1",          #a lot of inspiration from kerrickstaley's genanki python model
            "qfmt": "{{English}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Article}} {{Target}}<br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>',
        },
        {
            "name": "Card 2",
            "qfmt": "{{Article}} {{Target}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}}<br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>',
        },
    ],
)

verb_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    "Verb Model",
    fields=[{"name": "English"}, {"name": "Target"}, {"name": "Example"}, {"name": "Morphology"}], #example for a full esentence
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{English}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Target}}<br><i>{{Example}}</i><br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>',
        },
        {
            "name": "Card 2",
            "qfmt": "{{Target}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}}<br><i>{{Example}}</i><br><details><summary>Show morphology</summary><small>{{Morphology}}</small></details>',
        },
    ],
)

languages = {
    "German": {
        "words": {
            "hello": "hallo",
            "goodbye": "Tschüss",
            "How are you?": "Wie geht es dir?",
            "cat": "Katze",
        },
        "nouns": {
            "coffee": ("der", "Kaffee"), #value is a tuple ()
            "house": ("das", "Haus"),
            "woman": ("die", "Frau"),
        },
        "verbs": {
            "to eat": ("essen", "Ich esse einen Apfel."),
            "to go": ("gehen", "Ich gehe nach Hause."),
        },
    },
    "Japanese": {
        "words": {
            "hello": "こんにちは",
            "school": "学校",
        },
        "nouns": {
            "park": ("", "公園"),  #no articles in japanese  ""empty
        },
        "verbs": {
            "to eat": ("食べる", "リンゴを食べます。"),
            "to sleep": ("寝る", "私は早く寝ます。"),
        },
    },
}

#Build decks
seen_fronts = load_seen_fronts()  #seen fronts holds the words that have been exported
total_added = 0  #tracks how many notes are added in the script. Visible in Terminal
total_skipped = 0 #tracks how many notes have been skipped, previously exported. Visible in Terminal

# words are new, not yet in seen_fronts across all languages combined.
new_word_count = 0   #counter
for lang_name, data in languages.items():    #loops through languages dictionary
    for english in data.get("words", {}):    # loops through word dictionary to get english(keys) words
        if f"{lang_name}|{english}" not in seen_fronts:   #checks if key/value is in seen_fronts
            new_word_count += 1   #counter +1
    for english in data.get("nouns", {}):
        if f"{lang_name}|{english}" not in seen_fronts:
            new_word_count += 1
    for english in data.get("verbs", {}):
        if f"{lang_name}|{english}" not in seen_fronts:
            new_word_count += 1

if new_word_count == 0:   #no new words
    print("No new words found. Everything has already been exported.")
    raise SystemExit  #stops the script from running further

answer = input(f"Found {new_word_count} new word(s). Add them to the deck? (y/n): ").strip().lower() #strip removes accidental spaces. lower  converts letters to lowercase
if answer not in ("y", "yes"):  #"y" "yes" tuple of accepable values
    print("Cancelled. Nothing was added or exported.")
    raise SystemExit

for lang_name, data in languages.items(): #loops through language dictionary
    deck = genanki.Deck( #creates a new(same) deck, every time the script runs
        random.randrange(1 << 30, 1 << 31),
        f"{lang_name} Vocabulary"
    )

    added_count = 0 #inside the loop so get created fresh for any language after creation of new deck
    skipped_count = 0 #same thing

    # Words
    for english, target in data.get("words", {}).items(): #data is language vocabulary. items gets keys and values
        key = f"{lang_name}|{english}"
        if key in seen_fronts: #checks if key exists in seen_fronts.json
            print(f"[{lang_name}] Skipped (duplicate): {english}") #notify user there is a duplicate
            skipped_count += 1
            continue #next loop  
        morphology = describe_morphology(target, lang_name) #using spacy to run a word through morphology function
        note = genanki.Note(model=word_model, fields=[english, target, morphology]) #builds flashcard data. word_model is the structure. fields are values
        deck.add_note(note) #attaches note to the current language deck
        seen_fronts.add(key) #record a words as seen, key gets added into seen_fronts. word will be skipped as a duplicate in future runs
        added_count += 1
        print(f"[{lang_name}] Added [word]: {english} -> {target} | {morphology}") #show user in terminal what has been added

    # Nouns
    for english, (article, target) in data.get("nouns", {}).items():
        key = f"{lang_name}|{english}"
        if key in seen_fronts:
            print(f"[{lang_name}] Skipped (duplicate): {english}")
            skipped_count += 1
            continue
        morphology = describe_morphology(target, lang_name)
        note = genanki.Note(model=noun_model, fields=[english, article, target, morphology])
        deck.add_note(note)
        seen_fronts.add(key)
        added_count += 1
        print(f"[{lang_name}] Added [noun]: {english} -> {article} {target} | {morphology}")

    # Verbs
    for english, (target, example) in data.get("verbs", {}).items():
        key = f"{lang_name}|{english}"
        if key in seen_fronts:
            print(f"[{lang_name}] Skipped (duplicate): {english}")
            skipped_count += 1
            continue
        morphology = describe_morphology(target, lang_name)
        note = genanki.Note(model=verb_model, fields=[english, target, example, morphology])
        deck.add_note(note)
        seen_fronts.add(key)
        added_count += 1
        print(f"[{lang_name}] Added [verb]: {english} -> {target} | {morphology}")

    if added_count > 0: #checks if there are any new notes, if every word is a duplicate 0
        output_path = os.path.join(OUTPUT_DIR, f"{lang_name.lower()}_vocab.apkg") #f string builds filename. os.path.join(OUTPUT_DIR) combines filname with folder path
        genanki.Package(deck).write_to_file(output_path) #exports the deck with its notes writes it as .apkg
        print(f"[{lang_name}] Deck saved as {output_path} ({added_count} new notes)")
    else:
        print(f"[{lang_name}] No new cards to add. Nothing exported.") #if added count is 0 skip file writing

    total_added += added_count #add added_count to total added and store the number in total_added
    total_skipped += skipped_count #same. grand total. good for saving file if there is anything new to save

save_seen_fronts(seen_fronts) #writes the final updated seen_fronts set back to seen_fronts.json

print(f"\nTotal added: {total_added}") #shows grand total of every new note added, across all languages   
print(f"Total skipped: {total_skipped}") #shows grand total of every duplicate skipped, across all languages
