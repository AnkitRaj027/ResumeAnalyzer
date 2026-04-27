import string
import nltk
from nltk.corpus import stopwords

# Ensure resources are downloaded safely
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text):
    if not text:
        return ""
        
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    words = text.split()

    try:
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words]
    except Exception:
        # Fallback if stopwords fail
        pass

    return " ".join(words)