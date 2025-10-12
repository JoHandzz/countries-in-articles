import spacy
import demonym

def find_countries(doc, lookup_map):
    
    found_countries = set()
    article_lower = doc.text.lower() 

    # Identify and collect tokens from PERSON entities to avoid false positives.
    person_tokens = set()
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            person_tokens.update({token.text for token in ent})

    # Create sets of words and their base forms (lemmas) from the document,
    words_in_text = {token.text for token in doc if token.text not in person_tokens}
    lemmas_in_text = {token.lemma_.lower() for token in doc if token.text not in person_tokens}
    
    # 3. Iterate through the lookup map to find matches.
    for demonym, country in lookup_map.items():
        # Handle multi-word demonyms (e.g., "costa rican")
        if ' ' in demonym:
            if demonym in article_lower:
                found_countries.add(country)
        
        # Handle single-word demonyms 
        else:
            # Check if the demonym matches a word or its base form in the text.
            if demonym in words_in_text or demonym in lemmas_in_text:
                found_countries.add(country)
                
    return ", ".join(sorted(list(found_countries)))



## Small test for the function

nlp = spacy.load("da_core_news_sm")
text = "en grønlænder spiser franske kager"
doc = nlp(text.lower())
demonym = demonym.DANISH

print(find_countries(doc,demonym))
