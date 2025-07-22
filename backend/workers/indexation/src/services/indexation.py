import fitz
from src.models.classifier import ClassifierResponse
from src.services.layout_classifier import LayoutClassifier


class IndexationService:
    def __init__(self):
        self.classifier = LayoutClassifier()
        
    def to_html(self, doc: fitz.Document, mapping: []):
        pass
        

    def run(self, pdf_bytes: bytes):
        doc = fitz.open(pdf_bytes)

        classifier_response: ClassifierResponse = self.classifier.classify(doc)
        
        
