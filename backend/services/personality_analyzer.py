import json
import re
import os
import random
from typing import Dict, List
from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


class PersonalityAnalyzer:
    def __init__(self):
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()

        # Initialize Hugging Face pipeline for text classification
        try:
            self.classifier = pipeline("sentiment-analysis")
        except Exception as e:
            print(f"Error loading Hugging Face model: {e}")
            self.classifier = None

        # Personality trait keywords
        self.openness_keywords = ['creative', 'innovative', 'curious', 'adventurous', 'new', 'ideas', 'learn',
                                  'artistic', 'imaginative']
        self.conscientiousness_keywords = ['organized', 'detail-oriented', 'responsible', 'disciplined', 'achieve',
                                           'goal', 'plan', 'reliable']
        self.extraversion_keywords = ['team', 'lead', 'present', 'communicate', 'social', 'group', 'collaborate',
                                      'outgoing', 'energetic']
        self.agreeableness_keywords = ['help', 'support', 'cooperate', 'friendly', 'empathy', 'teamwork', 'kind',
                                       'compassionate']
        self.neuroticism_keywords = ['stress', 'pressure', 'anxiety', 'worry', 'nervous', 'tense', 'moody']

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze personality traits from CV text using a combination of:
        1. Hugging Face model for sentiment analysis
        2. NLTK sentiment analysis
        3. Keyword-based analysis
        """
        # Get sentiment scores
        sentiment = self.sia.polarity_scores(text)

        # Use Hugging Face model if available
        hf_prediction = {}
        if self.classifier:
            try:
                # Split text into chunks to avoid token limit
                chunks = self._split_text(text)
                all_predictions = []

                for chunk in chunks:
                    prediction = self.classifier(chunk)
                    all_predictions.extend(prediction)

                # Aggregate predictions
                hf_prediction = self._aggregate_predictions(all_predictions)
            except Exception as e:
                print(f"Error with Hugging Face model: {e}")

        # Get keyword-based scores
        keyword_scores = {
            'openness': self._calculate_keyword_score(text, self.openness_keywords),
            'conscientiousness': self._calculate_keyword_score(text, self.conscientiousness_keywords),
            'extraversion': self._calculate_keyword_score(text, self.extraversion_keywords),
            'agreeableness': self._calculate_keyword_score(text, self.agreeableness_keywords),
            'neuroticism': self._calculate_keyword_score(text, self.neuroticism_keywords)
        }

        # Combine all scores
        final_scores = {}
        for trait in keyword_scores:
            # Start with keyword score
            score = keyword_scores[trait]

            # Adjust based on sentiment
            if trait == 'neuroticism':
                score += sentiment['neg'] * 0.5
            else:
                score += sentiment['pos'] * 0.3

            # Adjust based on Hugging Face prediction if available
            if hf_prediction and 'positive' in hf_prediction:
                if trait == 'neuroticism':
                    score -= hf_prediction['positive'] * 0.2
                else:
                    score += hf_prediction['positive'] * 0.2

            # Ensure score is between 0 and 1
            final_scores[trait] = max(0, min(1, score))

        return final_scores

    def analyze_test_answers(self, answers: Dict[str, str]) -> Dict[str, float]:
        """
        Analyze personality traits from online test answers.
        This is a simplified version of a Big Five personality test.
        """
        traits = {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }

        # Simple scoring based on a few sample questions
        if 'q1' in answers:  # Question about trying new things
            traits['openness'] += 0.2 if answers['q1'] == 'yes' else -0.1

        if 'q2' in answers:  # Question about organization
            traits['conscientiousness'] += 0.2 if answers['q2'] == 'yes' else -0.1

        if 'q3' in answers:  # Question about social gatherings
            traits['extraversion'] += 0.2 if answers['q3'] == 'yes' else -0.1

        if 'q4' in answers:  # Question about helping others
            traits['agreeableness'] += 0.2 if answers['q4'] == 'yes' else -0.1

        if 'q5' in answers:  # Question about worrying
            traits['neuroticism'] += 0.2 if answers['q5'] == 'yes' else -0.1

        # Ensure scores are between 0 and 1
        for trait in traits:
            traits[trait] = max(0, min(1, traits[trait]))

        return traits

    def _split_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks to avoid token limit."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _aggregate_predictions(self, predictions: List[Dict]) -> Dict[str, float]:
        """Aggregate predictions from multiple chunks."""
        # This is a simplified aggregation - in a real implementation,
        # you would map the model's output to personality traits
        positive_count = sum(1 for p in predictions if p['label'] == 'POSITIVE')
        negative_count = sum(1 for p in predictions if p['label'] == 'NEGATIVE')
        total = len(predictions)

        return {
            'positive': positive_count / total if total > 0 else 0.5,
            'negative': negative_count / total if total > 0 else 0.5
        }

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate a simple score based on keyword frequency."""
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
        return min(1.0, keyword_count / len(keywords))