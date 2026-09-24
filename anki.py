import genanki
import random
import json 
import os 
import spacy


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
