"""from ankiapi import AnkiApi

anki = AnkiApi()

# Create a new deck
anki.create_deck("Python Programming")

# Add a flashcard
anki.add_flashcard(
    deck_name="Python Programming",
    front="What is a Python list comprehension?",
    back="A concise way to create lists using a single line of code with a for loop and optional conditions."
)"""

import spacy

# Load the pre-trained model for the source language (English)
source_lang = spacy.load("en_core_web_sm")

# Load the pre-trained model for the target language (German)
target_lang = spacy.load("de_core_news_sm")

# Define the text to translate
text = "SpaCy is a powerful Python library for natural language processing."

# Process the source text
doc = source_lang(text)

# Initialize the translated text variable
translated_text = ""

# Iterate over sentences in the processed text
for sent in doc.sents:
    translated_sent = ""
    
    # Iterate over tokens in each sentence
    for token in sent:
        # Append the translated token to the sentence
        translated_sent += token._.translations['de'] + " "
    
    # Capitalize the translated sentence and append to the overall translation
    translated_text += translated_sent.capitalize()

# Print the translated text
print(translated_text) 



