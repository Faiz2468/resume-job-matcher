from keyword_extraction import extract_keywords_from_text

def test_extract_keywords_from_text():
    sample_text = """
    Experienced data analyst with proficiency in Python, SQL, and machine learning. 
    Seeking a role in data science or cloud computing.
    """

    keywords = extract_keywords_from_text(sample_text)

    # Expect common noun phrases to appear
    expected_keywords = {
        "experienced data analyst",
        "proficiency",
        "python",
        "sql",
        "machine learning",
        "data science",
        "cloud computing"
    }

    assert expected_keywords.issubset(set(keywords))