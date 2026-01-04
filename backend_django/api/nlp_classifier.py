import re
import string
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
from textblob import TextBlob

class ComplaintClassifier:
    def __init__(self):
        self.departments = {
            'Public Works & Infrastructure': [
                'road', 'pothole', 'bridge', 'highway', 'street', 'pavement',
                'construction', 'infrastructure', 'building', 'repair', 'crack',
                'footpath', 'sidewalk', 'manholes', 'traffic', 'signal'
            ],
            'Water Supply & Sanitation': [
                'water', 'supply', 'leak', 'pipe', 'drainage', 'sewage', 'sewer',
                'plumbing', 'tank', 'tap', 'contaminated', 'dirty', 'underground',
                'overflow', 'blockage', 'sanitation'
            ],
            'Electricity & Power': [
                'electricity', 'power', 'light', 'electric', 'transformer', 'wire',
                'cable', 'pole', 'outage', 'blackout', 'billing', 'meter', 'voltage',
                'street light', 'lamp', 'current'
            ],
            'Transportation': [
                'bus', 'transport', 'traffic', 'parking', 'vehicle', 'metro', 'train',
                'station', 'route', 'schedule', 'conductor', 'driver', 'fare',
                'congestion', 'jam'
            ],
            'Health & Medical Services': [
                'hospital', 'health', 'medical', 'doctor', 'clinic', 'medicine',
                'patient', 'emergency', 'ambulance', 'sanitation', 'hygiene',
                'disease', 'epidemic', 'vaccination', 'treatment'
            ],
            'Education': [
                'school', 'education', 'teacher', 'student', 'classroom', 'college',
                'university', 'exam', 'books', 'library', 'fees', 'admission',
                'facility', 'building'
            ],
            'Police & Safety': [
                'police', 'crime', 'theft', 'robbery', 'violence', 'safety', 'security',
                'assault', 'harassment', 'accident', 'emergency', 'law', 'order',
                'patrol', 'station'
            ],
            'Revenue & Tax': [
                'tax', 'revenue', 'property', 'bill', 'payment', 'certificate',
                'license', 'permit', 'registration', 'assessment', 'collection',
                'refund', 'penalty', 'dues'
            ],
            'Environment & Pollution': [
                'pollution', 'environment', 'air', 'noise', 'waste', 'garbage',
                'trash', 'dump', 'smell', 'odor', 'toxic', 'contamination',
                'disposal', 'recycling', 'clean'
            ],
            'Consumer Affairs': [
                'consumer', 'product', 'service', 'fraud', 'cheating', 'scam',
                'defective', 'refund', 'warranty', 'quality', 'shop', 'store',
                'merchant', 'seller', 'buyer'
            ]
        }

        self.urgency_keywords = {
            'high': [
                'urgent', 'emergency', 'dangerous', 'critical', 'serious', 'severe',
                'life-threatening', 'accident', 'injury', 'death', 'fire', 'burst',
                'major', 'huge', 'massive', 'immediate', 'crisis'
            ],
            'medium': [
                'problem', 'issue', 'concern', 'need', 'requires', 'attention',
                'moderate', 'significant', 'important', 'recurring'
            ]
        }

        self.model = None
        self.load_or_train_model()

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = ' '.join(text.split())
        return text

    def extract_keywords(self, text: str) -> List[str]:
        text_lower = text.lower()
        keywords = []
        for dept, dept_keywords in self.departments.items():
            for keyword in dept_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
        return list(set(keywords))[:10]

    def determine_urgency(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()

        high_count = sum(1 for keyword in self.urgency_keywords['high'] if keyword in text_lower)
        medium_count = sum(1 for keyword in self.urgency_keywords['medium'] if keyword in text_lower)

        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity

            if high_count >= 2 or sentiment < -0.5:
                return 'High', 0.9
            elif high_count >= 1 or sentiment < -0.2:
                return 'High', 0.75
            elif medium_count >= 2:
                return 'Medium', 0.7
            elif medium_count >= 1:
                return 'Medium', 0.6
            else:
                return 'Low', 0.5
        except:
            if high_count >= 1:
                return 'High', 0.7
            elif medium_count >= 1:
                return 'Medium', 0.6
            else:
                return 'Low', 0.5

    def analyze_sentiment(self, text: str) -> str:
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            if polarity > 0.1:
                return 'Positive'
            elif polarity < -0.1:
                return 'Negative'
            else:
                return 'Neutral'
        except:
            return 'Neutral'

    def keyword_based_classify(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}

        for dept, keywords in self.departments.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += text_lower.count(keyword)
            scores[dept] = score

        if all(score == 0 for score in scores.values()):
            return 'Others', 0.5

        best_dept = max(scores.items(), key=lambda x: x[1])
        total_score = sum(scores.values())
        confidence = min(best_dept[1] / max(total_score, 1), 1.0)

        confidence = 0.6 + (confidence * 0.35)

        return best_dept[0], confidence

    def load_or_train_model(self):
        model_path = os.path.join(os.path.dirname(__file__), 'complaint_classifier.pkl')

        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                return
            except:
                pass

        training_data = self.generate_training_data()
        X = [item['text'] for item in training_data]
        y = [item['department'] for item in training_data]

        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('clf', MultinomialNB(alpha=0.1))
        ])

        self.model.fit(X, y)

        try:
            joblib.dump(self.model, model_path)
        except:
            pass

    def generate_training_data(self) -> List[Dict]:
        training_data = []

        templates = {
            'Public Works & Infrastructure': [
                "There is a huge pothole on {location} causing accidents",
                "The road near {location} is in very bad condition with cracks",
                "Bridge at {location} needs urgent repair, dangerous for vehicles",
                "Street pavement is broken on {location}",
                "Construction debris blocking the road at {location}",
                "Manhole cover missing on {location}, very dangerous"
            ],
            'Water Supply & Sanitation': [
                "No water supply in {location} for the past {days} days",
                "Water leak from underground pipe at {location}",
                "Sewage overflow on {location}, terrible smell",
                "Drainage system blocked at {location}",
                "Contaminated water supply in {location}",
                "Water tank not cleaned for months in {location}"
            ],
            'Electricity & Power': [
                "Power outage in {location} for {days} days",
                "Street light not working at {location}",
                "Electricity bill incorrect for {location}",
                "Transformer making loud noise near {location}",
                "Electric wire hanging dangerously at {location}",
                "Voltage fluctuation issues in {location}"
            ],
            'Transportation': [
                "Bus service irregular on route {location}",
                "Heavy traffic congestion at {location}",
                "No parking space available near {location}",
                "Bus conductor rude and misbehaving on route {location}",
                "Traffic signal not working at {location}",
                "Need bus stop at {location}"
            ],
            'Health & Medical Services': [
                "Hospital staff negligent at {location}",
                "No medicines available at clinic in {location}",
                "Poor sanitation in hospital at {location}",
                "Doctor absent from duty at {location} health center",
                "Emergency services delayed in {location}",
                "Need ambulance service in {location}"
            ],
            'Education': [
                "School building in poor condition at {location}",
                "Teachers absent frequently at {location} school",
                "No proper classroom facilities in {location}",
                "Library books outdated at {location} college",
                "School fees too high in {location}",
                "Need new school in {location} area"
            ],
            'Police & Safety': [
                "Theft reported in {location}, no police response",
                "Safety concern in {location} at night",
                "Need police patrol in {location}",
                "Harassment case at {location}",
                "Traffic violation common at {location}",
                "Crime rate increasing in {location}"
            ],
            'Revenue & Tax': [
                "Property tax assessment wrong for {location}",
                "Birth certificate not issued for {location} resident",
                "Tax refund pending for {location}",
                "Need trade license for shop at {location}",
                "Property registration delayed at {location}",
                "Tax bill incorrect for {location}"
            ],
            'Environment & Pollution': [
                "Air pollution very high at {location}",
                "Garbage not collected from {location}",
                "Noise pollution from factory at {location}",
                "Waste dump causing smell at {location}",
                "Toxic waste disposal issue at {location}",
                "Need recycling facility at {location}"
            ],
            'Consumer Affairs': [
                "Defective product purchased from shop at {location}",
                "Fraud by shopkeeper in {location}",
                "No refund given by store at {location}",
                "Poor quality goods sold at {location}",
                "Cheating in weighing scale at {location}",
                "Consumer rights violated at {location}"
            ]
        }

        locations = ["Main Street", "Park Avenue", "Central Square", "Green Valley",
                     "River Road", "Market Area", "Colony", "Sector 4"]
        days_options = ["2", "3", "5", "7"]

        for dept, templates_list in templates.items():
            for template in templates_list:
                for i in range(5):
                    location = locations[i % len(locations)]
                    days = days_options[i % len(days_options)]
                    text = template.format(location=location, days=days)
                    training_data.append({'text': text, 'department': dept})

        return training_data

    def get_suggested_steps(self, department: str, urgency: str) -> List[str]:
        common_steps = [
            "Verify the complaint details and location.",
            "Assess the severity of the issue on-site if necessary.",
            "Assign a field officer to inspect the reported issue."
        ]

        specific_steps = {
            'Public Works & Infrastructure': [
                "Check for road maintenance records/schedules.",
                "Deploy a repair crew with necessary materials (asphalt/concrete).",
                "Ensure safety barriers are placed around the hazard."
            ],
            'Water Supply & Sanitation': [
                "Inspect the pipeline/source for leaks or blockages.",
                "Test water quality samples if contamination is reported.",
                "Coordinate with the sanitation department for cleanup."
            ],
            'Electricity & Power': [
                "Check the local grid status and transformer health.",
                "Dispatch a lineman to repair the fault/restore power.",
                "Ensure safety protocols are followed to prevent electrical accidents."
            ],
            'Transportation': [
                "Verify schedule adherence/vehicle condition.",
                "Address staff behavior or traffic management issues.",
                "Review route planning if congestion is reported."
            ],
            'Health & Medical Services': [
                "Investigate staff attendance/medicine availability.",
                "Ensure facility hygiene standards are met.",
                "Address patient grievances immediately."
            ],
            'Education': [
                "Inspect school infrastructure/facilities.",
                "Meet with school administration regarding staff/fees.",
                "Ensure educational standards are maintained."
            ],
            'Police & Safety': [
                "Dispatch a patrol unit to the reported location.",
                "Register an FIR if a crime is confirmed.",
                "Increase surveillance in the affected area."
            ],
            'Revenue & Tax': [
                "Verify property/tax records in the database.",
                "Process the refund/certificate issuance.",
                "Correct any billing discrepancies."
            ],
            'Environment & Pollution': [
                "Measure pollution levels at the site.",
                "Identify the source of pollution/waste.",
                "Enforce regulations and initiate cleanup."
            ],
            'Consumer Affairs': [
                "Verify the purchase receipt and product condition.",
                "Contact the seller/merchant for mediation.",
                "Initiate consumer protection proceedings if fraud is found."
            ]
        }
        
        steps = specific_steps.get(department, ["Investigate the matter further."])
        
        if urgency == 'High':
            steps.insert(0, "IMMEDIATE ACTION REQUIRED: Prioritize this complaint.")
        
        return common_steps + steps

    def classify(self, complaint_text: str) -> Dict:
        preprocessed = self.preprocess_text(complaint_text)

        dept_keyword, conf_keyword = self.keyword_based_classify(complaint_text)

        urgency, urgency_conf = self.determine_urgency(complaint_text)
        keywords = self.extract_keywords(complaint_text)
        sentiment = self.analyze_sentiment(complaint_text)

        try:
            if self.model:
                dept_ml = self.model.predict([preprocessed])[0]
                proba = self.model.predict_proba([preprocessed])[0]
                conf_ml = float(max(proba))

                if conf_ml > conf_keyword:
                    final_dept = dept_ml
                    final_conf = conf_ml
                else:
                    final_dept = dept_keyword
                    final_conf = conf_keyword
            else:
                final_dept = dept_keyword
                final_conf = conf_keyword
        except:
            final_dept = dept_keyword
            final_conf = conf_keyword

        # Generate suggested steps
        suggested_steps = self.get_suggested_steps(final_dept, urgency)

        return {
            'predictedDepartment': final_dept,
            'confidenceScore': round(final_conf, 2),
            'urgency': urgency,
            'keywords': keywords,
            'sentiment': sentiment,
            'suggestedSteps': suggested_steps
        }

classifier = ComplaintClassifier()
