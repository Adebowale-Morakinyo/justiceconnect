from transformers import pipeline


class ComplaintAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="finiteautomata/bertweet-base-sentiment-analysis",
        )
        self.ner = pipeline("ner", model="Davlan/bert-base-multilingual-cased-ner-hrl")

    def analyze_complaint(self, text):
        """Extract key entities and urgency"""
        # Sentiment analysis
        sentiment = self.classifier(text)[0]

        # Named Entity Recognition
        entities = self.ner(text)
        locations = [e["word"] for e in entities if e["entity"] == "LOC"]
        people = [e["word"] for e in entities if e["entity"] == "PER"]

        return {
            "urgency": "HIGH" if sentiment["label"] == "NEG" else "MEDIUM",
            "locations": locations,
            "people_involved": people,
            "sentiment_score": sentiment["score"],
        }
