# job_keywords.py

# Predefined keyword lists based on job roles
keyword_database = {
    "data_scientist": [
        "python",
        "machine learning",
        "data science",
        "statistics",
        "pandas",
        "scikit-learn",
        "tensorflow",
        "keras",
        "deep learning",
        "sql",
        "data visualization",
        "numpy",
        "matplotlib",
        "nlp"
    ],
    "cloud_engineer": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "ci/cd",
        "devops",
        "linux",
        "cloud security",
        "serverless",
        "cloud architecture"
    ],
    "full_stack_developer": [
        "html",
        "css",
        "javascript",
        "react",
        "node.js",
        "express",
        "mongodb",
        "postgresql",
        "rest api",
        "git",
        "docker",
        "ci/cd"
    ]
}

# Default fallback
default_keywords = keyword_database["data_scientist"]

# Function to get keywords by role
def get_job_keywords(role: str = "data_scientist"):
    return keyword_database.get(role.lower(), default_keywords)