import string
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

def clean_text(text):
    text = text.lower()
    
    words = text.split()

    words = [
        w for w in words
        if w not in stopwords.words('english')
        and w not in string.punctuation
    ]

    return " ".join(words)