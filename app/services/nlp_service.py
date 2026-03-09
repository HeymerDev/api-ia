from keybert import KeyBERT
import spacy

class NLPService:

    def __init__(self):

        self.kw_model = KeyBERT()
        self.nlp = spacy.load("en_core_web_sm")

    def analyze(self, text):

        keywords = self.kw_model.extract_keywords(text)

        doc = self.nlp(text)

        entities = [ent.text for ent in doc.ents]

        return {
            "keywords": keywords,
            "entities": entities
        }