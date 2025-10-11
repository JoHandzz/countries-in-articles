import spacy
import demonym



def find_countries(article_text, lookup_map, langugage):
    found_countries = set()
    article_lower = article_text.lower()

    if langugage == "Danish":
        nlp = spacy.load('da_core_news_sm')  

    # MANGLER DE ANDRE LANDE
    
    doc = nlp(article_lower)
    

    # 2. Identify and collect all tokens belonging to recognized PERSON entities.
    person_tokens = set()
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            person_tokens.update({token.text for token in ent})

    # Set of original words in text (excluding those in person_tokens)
    words_in_text = {token.text for token in doc if token.text not in person_tokens}
    
    # Set of lemmatized root words (excluding those whose original token was in person_tokens)
    lemmas_in_text = {token.lemma_.lower() for token in doc if token.text not in person_tokens}
    
    # 4. Iterate through the lookup map to find matches.
    for demonym, country in lookup_map.items():
        if ' ' in demonym:  # Hadle multiword like costa rica
            if demonym in article_lower:
                found_countries.add(country)
        
        #  Handle Single-word keys (e.g., "dansk", "german")
        else:
            if demonym in words_in_text or demonym in lemmas_in_text:
                found_countries.add(country)
                
    return ", ".join(sorted(list(found_countries)))

txt = "En grøndlænder og en dansker går en tur. De spiser æbler og franske tærter. Det gør ham fra costa rica sur"


print(find_countries(txt, demonym.DANISH, "Danish"))