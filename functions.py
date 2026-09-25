import  spacy, subprocess, sys, genanki, random, os, json
import deepl, langcodes, language_data #not required if using external translator

def load_lang(source): # Loads the spacy models and if needed installs them automatically. Installed models can be checked via "python -m spacy validate" 
    models = {
        "english":"en_core_web_sm"
        ,"german":"de_core_news_sm"
        ,"french":"fr_core_news_sm"
        ,"italian":"it_core_news_sm"
        ,"spanish":"es_core_news_sm"
        ,"portuguese":"pt_core_news_sm"
        ,"greek":"el_core_news_sm"
        ,"swedish":"sv_core_news_sm"
        ,"finnish":"fi_core_news_sm"
        ,"polish":"pl_core_news_sm"
        ,"ukrainian":"uk_core_news_sm"
        ,"russian":"ru_core_news_sm"
        ,"japanese":"ja_core_news_sm"
        ,"chinese":"zh_core_web_sm"
        ,"korean":"ko_core_news_sm"
        ,"dutch":"nl_core_news_sm"
        ,"danish":"da_core_news_sm"}

    try:
        selected_model = models[source]
        return spacy.load(selected_model)
    except KeyError:
            raise ValueError(f"Language not supported: {source}")
    except OSError:
       print(f"The model {selected_model} is not installed, proceeding with installation ...")
       subprocess.check_call([sys.executable, "-m", "spacy", "download", selected_model])
       return spacy.load(selected_model)

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

#deepl implementation /// authentication key, has to be provided by the user
def deepl_vocab_translation(key, vocab, source, target):
    source_code = langcodes.find(source)
    target_code = langcodes.find(target)

    if target_code == langcodes.find("english"):
        target_code = "EN-US"

    auth_key = str(key)
    deepl_client = deepl.DeepLClient(auth_key)
    translated = []
    
    for word in vocab:
        translation = deepl_client.translate_text(str(word), source_lang=str(source_code) ,target_lang=str(target_code))
        translated.append(translation.text)
    
    return(translated)



#/////////////////////////////////////
#//////////anki card builder//////////

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(OUTPUT_DIR, "Vocab_Config")
os.makedirs(CONFIG_DIR, exist_ok=True)

SEEN_FILE = os.path.join(CONFIG_DIR, "seen_fronts.json") #remembers which words have been exported already, so no duplicates

def load_seen_fronts(): 
    if os.path.exists(SEEN_FILE): 
        with open(SEEN_FILE, "r", encoding="utf-8") as f:   #utf makes non latin characters like ä or 私 read correctly
            return set(json.load(f))
    return set()

def save_seen_fronts(seen): 
    with open(SEEN_FILE, "w", encoding="utf-8") as f: 
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2) #ensure_ascii=False keeps characters like ä or 私 as they are

word_model = genanki.Model(
    1892138122,
    "Word Model",
    fields=[{"name": "front"}, {"name": "Back"}, {"name": "Morphology"}], #back = back language
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{front}}", 
            "afmt": '{{FrontSide}}<hr id="answer">{{Back}}<br><details><summary>Show morphology</summary><br><small>{{Morphology}}</small></details>',
        },
    ],
)
def build_cards(cards, deck_name):# takes a dictionary and a string as arguments
    total_added = 0 
    seen_fronts = load_seen_fronts()
    new_word_count = 0 # words are new, not yet in seen_fronts

    added_count = 0 
    skipped_count = 0

    """for lang_name, data in languages.items():    
    for front in data.get("words", {}): 
        if f"{lang_name}|{front}" not in seen_fronts:   
            new_word_count += 1   
    for front in data.get("nouns", {}):
        if f"{lang_name}|{front}" not in seen_fronts:
            new_word_count += 1

    if new_word_count == 0: 
        print("No new words found. Everything has already been exported.")
        raise SystemExit  #stops the script from running further

    answer = input(f"Found {new_word_count} new word(s). Add them to the deck? (y/n): ").strip().lower()
    if answer not in ("y", "yes"):  
        print("Cancelled. Nothing was added or exported.")
        raise SystemExit"""

    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)#creates a new(same) deck, every time the script runs
    for front_vocab, back_vocab in cards.items(): 
        if front_vocab in seen_fronts: 
            print(f"[{deck_name}] Skipped (duplicate): {front_vocab}") 
            skipped_count += 1
            continue 
        morphology = back_vocab[2] #generate mophology for the back of the flashcard
        note = genanki.Note(model=word_model, fields=[front_vocab, back_vocab[0], morphology]) #builds flashcard data
        deck.add_note(note)
        seen_fronts.add(front_vocab) #prevents duplicates next time
        added_count += 1
        print(f"[{deck_name}] Added [word]: {front_vocab} -> {back_vocab[0]} | {morphology}") 
    
    if added_count > 0: 
        output_path = os.path.join(CONFIG_DIR, f"{deck_name}.apkg") 
        genanki.Package(deck).write_to_file(output_path) #exports the deck with its notes writes it as .apkg
        print("\n")
        print(f"[{deck_name}] Deck saved as {output_path} ({added_count} new notes)")
    else:
        print(f"[{deck_name}] No new cards to add. Nothing exported.")

    total_added += added_count
    
    save_seen_fronts(seen_fronts)
    print(f"\nTotal added: {total_added}")
    


