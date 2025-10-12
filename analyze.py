def find_countries(doc, lookup_map):
    valid_countries = set(lookup_map.values())
    lookup_lower = {key.lower(): value for key, value in lookup_map.items()}
    for country in valid_countries:
        lookup_lower[country.lower()] = country

    found_countries = set()

    # Looking for GPE: Geopolitical Entity or LOC: Location
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:  
            candidate = lookup_lower.get(ent.text.lower())
            #  Add it ONLY if the canonical name is in valid_countries 
            if candidate and candidate in valid_countries:
                found_countries.add(candidate)

    # Trying to ignore names with countries in them such as Michael Jordan
    person_tokens = {token.text.lower() for ent in doc.ents if ent.label_ == 'PERSON' for token in ent}

    # All unique lemmas i.e words in the text
    words_and_lemmas = {token.text.lower() for token in doc if token.text.lower() not in person_tokens}

    # Is converted to rootform: "running" -> "run"
    words_and_lemmas.update({token.lemma_.lower() for token in doc if token.text.lower() not in person_tokens})
    
    # Search using set intersection
    matching_keys = words_and_lemmas.intersection(lookup_lower.keys())
    for key in matching_keys:
        candidate = lookup_lower[key]
        if candidate in valid_countries:
            found_countries.add(candidate)

    # 5. Handle multi-word keys like costa rica
    article_lower = doc.text.lower()
    for key, country in lookup_lower.items():
        if ' ' in key and key in article_lower:
            if country in valid_countries:
                found_countries.add(country)
            
    if not found_countries:
        return ""
    return ", ".join(sorted(list(found_countries)))


# FOR TESTING IN FILE
# ALSO IMPORT THESE IN THE TOP:
# import spacy
# import demonym



# nlp = spacy.load("de_core_news_sm")
# text = "usa und Dänemark, ich wohne in Berlin, Abschneidens, France, Frankreichs, L'Haÿ-les-Roses, Land, Pariser"
# doc = nlp(text)
# demonym = demonym.GERMAN

# print(find_countries(doc,demonym))