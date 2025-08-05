import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords_from_text(text):
    doc = nlp(text)

    # Collect meaningful nouns and noun phrases, remove stopwords and punctuation
    keywords = set()

    for chunk in doc.noun_chunks:
        keyword = chunk.text.strip().lower()
        if len(keyword) > 1 and not chunk.root.is_stop and chunk.root.is_alpha:
            keywords.add(keyword)

    # Also include named entities
    for ent in doc.ents:
        if ent.label_ in {"ORG", "GPE", "PERSON", "PRODUCT", "SKILL"}:
            keywords.add(ent.text.strip().lower())

    return list(keywords)