import deepl, langcodes, language_data

#deepl authentication key, has to be provided by the user

#deepl implementation
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


#test = ["ciao"]
#print(deepl_vocab_translation(auth_key, test, "italian", "english"))




#print(langcodes.find("english"))

# attempt with deeptranslator: "deep_translator.exceptions.AuthorizationException: Unauthorized access with the api key..."
"""from deep_translator import (DeeplTranslator) 

auth_key = "5001ea04-483a-403b-ae8c-a2be1b1410b1:fx"

text = "You are awesome!"

translated = DeeplTranslator(api_key=auth_key, source="en", target="de", use_free_api=True).translate(text)

print(translated)"""

