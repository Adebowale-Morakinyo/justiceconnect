import json
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np


class ACJAEngine:
    def __init__(self):
        # Load lightweight embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.qa_pipeline = pipeline(
            "question-answering", model="nlpaueb/legal-bert-small-uncased"
        )

        # Load ACJA sections
        with open("data/acja_sections.json") as f:
            self.sections = json.load(f)

        # Create search index
        self._create_search_index()

    def _create_search_index(self):
        """Create FAISS index for semantic search"""
        section_texts = [
            f"{s['section']}: {s['title']} - {s['content']}" for s in self.sections
        ]
        self.embeddings = self.embedder.encode(section_texts)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def get_legal_response(self, query, language="en"):
        """Get most relevant ACJA section with explanation"""
        # Semantic search
        query_embedding = self.embedder.encode([query])
        D, I = self.index.search(query_embedding, k=1)
        best_section = self.sections[I[0][0]]

        # Generate plain language explanation
        context = f"ACJA Section {best_section['section']}: {best_section['content']}"
        explanation = self.qa_pipeline(
            question=f"Explain {query} in simple terms", context=context
        )["answer"]

        # Add multilingual support
        if language != "en":
            explanation = self._translate_response(explanation, language)

        return {
            "section": best_section["section"],
            "title": best_section["title"],
            "content": best_section["content"],
            "explanation": explanation,
        }

    def _translate_response(self, text, target_lang):
        """Translate to Pidgin/Hausa (placeholder - integrate LibreTranslate API later)"""
        translations = {
            "pidgin": {
                "arrest": "wetin police fit do",
                "bail": "how to come out for station",
            },
            # Add more translations
        }
        return translations.get(target_lang, {}).get(text.lower(), text)
