import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz

def check_similarity(skills, titles, job_title, job_skills):
    stop_words = set(stopwords.words('english'))
    user = skills + titles
    job = job_skills + job_title
    user = " ".join(user)
    job = " ".join(job)
    user_tokens = word_tokenize(user)
    job_tokens = word_tokenize(job)
    user = " ".join([w for w in user_tokens if not w in stop_words])
    job = " ".join([w for w in job_tokens if not w in stop_words])
    return fuzz.token_set_ratio(user, job)