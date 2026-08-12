from ankiapi import AnkiApi

#Testdictionary
testdict= {"watch": "視聴","car": "車","tree": "木", "apple":"りんご"}


# function that creates a new Anki deck and fills it with Flashcards based on a given dictionary
def make_a_deck(input_dict, target_deck):
    try:
        # Initialize the API (make sure Anki is running with AnkiConnect add-on)
        anki = AnkiApi()
        # Create a new deck
        anki.create_deck(target_deck)
    
        #create flashcard for each Key-Value pair
        for key, value in input_dict.items():
            anki.add_flashcard(
                deck_name= target_deck,
                front= key,
                back= value)
    
    # In case the user has not launched Anki: 
    except RuntimeError:
        print("Launch Anki first and try again")

make_a_deck(testdict, "Test Deck")

