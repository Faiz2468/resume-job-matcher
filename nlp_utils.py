import spacy
from rapidfuzz import fuzz

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    # Add Noun Chunks
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip().lower()
        if chunk_text and not chunk.root.is_stop:
            keywords.add(chunk_text)

    # Add Named Entities
    for ent in doc.ents:
        ent_text = ent.text.strip().lower()
        if ent.label_ in {"ORG", "PERSON", "GPE", "PRODUCT"}:
            keywords.add(ent_text)

    # Add Significant Tokens
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN", "ADJ"} and not token.is_stop and token.is_alpha:
            keywords.add(token.lemma_.lower())

    return list(keywords)

def match_keywords_fuzzy(resume_keywords, job_keywords, threshold=80):
    matched = []
    job_set = set(k.lower() for k in job_keywords)
    resume_set = set(k.lower() for k in resume_keywords)

    for job_kw in job_set:
        for resume_kw in resume_set:
            similarity = fuzz.ratio(job_kw, resume_kw)
            if similarity >= threshold:
                matched.append(job_kw)
                break

    score = len(matched) / len(job_set) * 100 if job_set else 0

    return {
        "matched_keywords": matched,
        "match_score": score
    }