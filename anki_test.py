import genanki
import random
import json 
import os 
import spacy

"""nlp_models = {
    "German": spacy.load("de_core_news_sm"),
    "Japanese": spacy.load("ja_core_news_sm"),
}"""

"""def get_tex_mor(token):       #
    tex = token.text          #
    mor = token.morph         #Rachel's morphology, can be deleted once merged 
    tex_mor = (tex, mor)      # 
    return(tex_mor)           #"""


def describe_morphology(text, lang_name):          
    nlp = nlp_models[lang_name]
    doc = nlp(text) #splits text into words/tokens as well as morphological feature
    parts = [] #list of morphology
    for token in doc: 
        if token.is_punct:
            continue
        tex, mor = get_tex_mor(token) #gets words from tex and morphology from mor
        tag = f"{tex}: {mor}" if str(mor) else tex #convert mor into a string. checks if mor is empty if empty false(show just word) true morphology exists build string with word and morphology
        parts.append(tag) 
    return "<br>".join(parts) #br is \n in HTML


#def get_article(back, lang_name): #detects German articles
    if lang_name != "German":
        return ""
    nlp = nlp_models[lang_name]  
    doc = nlp(back) 
    for token in doc:
        morph_str = str(token.morph) #convert to a string
        if "Gender=Masc" in morph_str:
            return "der"
        elif "Gender=Fem" in morph_str:
            return "die"
        elif "Gender=Neut" in morph_str:
            return "das"
    return "" #if no gender return empty string


SEEN_FILE = "seen_fronts.json" #remembers which words have been exported already, so no duplicates
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_seen_fronts(): 
    if os.path.exists(SEEN_FILE): 
        with open(SEEN_FILE, "r", encoding="utf-8") as f:   #utf makes non latin characters like ä or 私 read correctly
            return set(json.load(f))
    return set()  


def save_seen_fronts(seen): 
    with open(SEEN_FILE, "w", encoding="utf-8") as f: 
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2) #ensure_ascii=False keeps characters like ä or 私 as they are


word_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31), #unique ID for the model. 1 << 30, 1 << 31 recommended by GenAnki
    "Word Model",
    fields=[{"name": "front"}, {"name": "Back"}, {"name": "Morphology"}], #back = back language
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{front}}", 
            "afmt": '{{FrontSide}}<hr id="answer">{{back}}<br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },                                                  
        {
            "name": "Card 2", #reverse
            "qfmt": "{{Back}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{front}}<br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>', 
        },
    ],
)

noun_model = genanki.Model(  #want to see the article with the noun. Different type of flashcard
    random.randrange(1 << 30, 1 << 31),
    "Noun Model", # note type shown in Anki note type list
    fields=[{"name": "front"}, {"name": "Article"}, {"name": "back"}, {"name": "Morphology"}],
    templates=[
        {
            "name": "Card 1",          #a lot of inspiration from kerrickstaley's genanki python model
            "qfmt": "{{front}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Article}} {{back}}<br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },
        {
            "name": "Card 2",
            "qfmt": "{{Article}} {{back}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{front}}<br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },
    ],
)

"""#verb_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    "Verb Model",
    fields=[{"name": "front"}, {"name": "back"}, {"name": "Example"}, {"name": "Morphology"}], #example for a full esentence
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{front}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{back}}<br><i>{{Example}}</i><br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },
        {
            "name": "Card 2",
            "qfmt": "{{back}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{front}}<br><i>{{Example}}</i><br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },
    ],
)"""

"""#languages = {
    "German": {
        "words": {
            "hello": "hallo",
            "goodbye": "Tschüss",
            "How are you?": "Wie geht es dir?",
            "cat": "Katze",
        },
        "nouns": {
            "coffee": "Kaffee", 
            "house": "Haus",
            "woman": "Frau",
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
            "park": "公園", 
        },
        "verbs": {
            "to eat": ("食べる", "リンゴを食べます。"),
            "to sleep": ("寝る", "私は早く寝ます。"),
        },
    },
}"""

#Build decks
seen_fronts = load_seen_fronts() 
total_added = 0  
total_skipped = 0 

# words are new, not yet in seen_fronts across all languages combined.
new_word_count = 0 
"""for lang_name, data in languages.items():    
    for front in data.get("words", {}): 
        if f"{lang_name}|{front}" not in seen_fronts:   
            new_word_count += 1   
    for front in data.get("nouns", {}):
        if f"{lang_name}|{front}" not in seen_fronts:
            new_word_count += 1"""

"""if new_word_count == 0: 
    print("No new words found. Everything has already been exported.")
    raise SystemExit  #stops the script from running further

answer = input(f"Found {new_word_count} new word(s). Add them to the deck? (y/n): ").strip().lower()
if answer not in ("y", "yes"):  
    print("Cancelled. Nothing was added or exported.")
    raise SystemExit"""

def build_cards(pos, languages, deck_name): # takes a dictionary as argument
    for f, b in languages.items(): 
        deck = genanki.Deck( #creates a new(same) deck, every time the script runs
            random.randrange(1 << 30, 1 << 31),
            f"{deck_name}"
        )
    
        added_count = 0 
        skipped_count = 0 
        # Nouns
        if pos == "NOUN":
            for front, back in languages.items():
                key = f
                if key in seen_fronts:
                    print(f"[{deck_name}] Skipped (duplicate): {front}")
                    skipped_count += 1
                    continue
                #article = get_article(back, lang_name) #auto-detected instead of read from the dictionary
                morphology = b[2]
                note = genanki.Note(model=noun_model, fields=[front, back, morphology])
                deck.add_note(note)
                seen_fronts.add(key)
                added_count += 1
                #print(f"[{lang_name}] Added [noun]: {front} -> {back} | {morphology}")
        # Words
        else:
            key = f
            if key in seen_fronts: 
                print(f"[{deck_name}] Skipped (duplicate): {front}") 
                skipped_count += 1
                continue 
            morphology = b[2] #generate mophology for the back of the flashcard
            note = genanki.Note(model=word_model, fields=[front, back, morphology]) #builds flashcard data
            deck.add_note(note) 
            seen_fronts.add(key) #prevents duplicates next time
            added_count += 1
            print(f"[{deck_name}] Added [word]: {front} -> {back} | {morphology}") 
    
        
        if added_count > 0: 
            output_path = os.path.join(OUTPUT_DIR, f"{deck_name}_vocab.apkg") 
            genanki.Package(deck).write_to_file(output_path) #exports the deck with its notes writes it as .apkg
            print(f"[{deck_name}] Deck saved as {output_path} ({added_count} new notes)")
        else:
            print(f"[{deck_name}] No new cards to add. Nothing exported.")
    
        total_added += added_count 
        total_skipped += skipped_count

save_seen_fronts(seen_fronts)

print(f"\nTotal added: {total_added}")
print(f"Total skipped: {total_skipped}")
