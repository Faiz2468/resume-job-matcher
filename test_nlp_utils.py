from nlp_utils import extract_keywords, match_keywords_fuzzy

def test_extract_keywords():
    text = "Python developer with experience in cloud computing and data analysis."
    keywords = extract_keywords(text)

    # Adjusted to match lemmatized and filtered output
    expected_keywords = {"python", "develop", "cloud", "computing", "data", "analysis"}

    # Using issubset to allow flexibility for spaCy variation
    assert expected_keywords.issubset(set(keywords))

def test_match_keywords_fuzzy():
    resume_kw = ["python", "cloud computing", "data analysis"]
    job_kw = ["python", "machine learning", "cloud computing"]
    result = match_keywords_fuzzy(resume_kw, job_kw)
    matched = result["matched_keywords"]
    score = result["match_score"]

    assert "python" in matched
    assert "cloud computing" in matched
    assert abs(score - 66.66) < 1