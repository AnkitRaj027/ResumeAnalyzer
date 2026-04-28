import string
import nltk
from nltk.corpus import stopwords
import PyPDF2
import io

# Ensure resources are downloaded safely
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    words = text.split()
    try:
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w not in stop_words]
    except Exception:
        pass
    return " ".join(words)

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"