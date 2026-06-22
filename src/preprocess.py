import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

STOP_WORDS = set(stopwords.words("english"))

STEMMER = PorterStemmer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ",text)
    tokens = text.split()
    tokens = [token for token in tokens if token.isalpha()]
    tokens = [token for token in tokens if token not in STOP_WORDS]
    tokens = [STEMMER.stem(token) for token in tokens]
    return tokens