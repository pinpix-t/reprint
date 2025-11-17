import re
from typing import List, Dict, Tuple
from collections import Counter
import spacy

# Initialize spaCy model (will need to download: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# Product keywords
PRODUCT_KEYWORDS = {
    "photobook": ["photobook", "photo book", "photo-book", "book"],
    "calendar": ["calendar", "calender"],
    "canvas": ["canvas", "canvas print"],
    "mug": ["mug", "coffee mug"],
    "poster": ["poster", "poster print"],
    "blanket": ["blanket", "throw"],
    "puzzle": ["puzzle", "jigsaw"],
    "metalprint": ["metal print", "metalprint", "metal"],
    "layflatbook": ["layflat", "lay flat", "lay-flat"],
    "bottle": ["bottle", "water bottle"],
    "tile": ["tile", "photo tile"],
    "labprint": ["lab print", "labprint"]
}

# Quality issue keywords
QUALITY_KEYWORDS = {
    "damage": ["damaged", "damage", "broken", "cracked", "torn", "ripped", "bent", "dented"],
    "defect": ["defect", "defective", "flaw", "imperfection", "faulty"],
    "quality": ["poor quality", "low quality", "bad quality", "quality issue"],
    "shipping": ["shipping damage", "damaged in transit", "packaging", "delivery"],
    "color": ["color", "colour", "faded", "wrong color", "color issue"],
    "print": ["print quality", "blurry", "pixelated", "fuzzy", "print issue"],
    "size": ["wrong size", "size issue", "too small", "too large"],
    "missing": ["missing", "incomplete", "partially missing"],
    "scuff": ["scuff", "scratched", "mark", "marking", "fingerprint"],
    "ink": ["ink", "smudge", "stain", "mark"]
}

def extract_products(text: str) -> List[str]:
    """Extract product mentions from text."""
    if not text:
        return []
    
    text_lower = text.lower()
    found_products = []
    
    for product, keywords in PRODUCT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_products.append(product)
                break
    
    return list(set(found_products))

def extract_quality_issues(text: str) -> List[str]:
    """Extract quality issue mentions from text."""
    if not text:
        return []
    
    text_lower = text.lower()
    found_issues = []
    
    for issue, keywords in QUALITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_issues.append(issue)
                break
    
    return list(set(found_issues))

def extract_facilities(text: str) -> List[str]:
    """
    Extract facility mentions from text.
    SECURITY: Uses compiled regex with bounded quantifiers to prevent ReDoS.
    """
    if not text:
        return []
    
    # SECURITY: Pre-compile pattern with bounded quantifier to prevent ReDoS
    # Limit facility code length (e.g., FacilityS050 = max 3 digits)
    facility_pattern = re.compile(r'Facility[A-Z]\d{1,5}', re.IGNORECASE)  # Bounded: 1-5 digits
    
    # Limit text length
    if len(text) > 10000:
        text = text[:10000]
    
    try:
        facilities = facility_pattern.findall(text)
        return list(set(facilities))
    except Exception as e:
        logger.warning(f"Error extracting facilities: {e}")
        return []

def analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis - returns 'positive', 'negative', or 'neutral'."""
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    
    negative_words = ["bad", "terrible", "awful", "horrible", "disappointed", "poor", 
                     "worst", "broken", "damaged", "defective", "faulty", "wrong"]
    positive_words = ["good", "great", "excellent", "amazing", "perfect", "love", 
                     "happy", "satisfied", "wonderful", "fantastic"]
    
    negative_count = sum(1 for word in negative_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"

def process_review_text(text: str) -> Dict:
    """Process a single review text and extract all relevant information."""
    if not text:
        return {
            "products": [],
            "issues": [],
            "facilities": [],
            "sentiment": "neutral"
        }
    
    return {
        "products": extract_products(text),
        "issues": extract_quality_issues(text),
        "facilities": extract_facilities(text),
        "sentiment": analyze_sentiment(text)
    }

def aggregate_review_analysis(reviews: List[Dict]) -> Dict:
    """Aggregate analysis across multiple reviews."""
    all_products = []
    all_issues = []
    all_facilities = []
    sentiments = []
    
    for review in reviews:
        # Try to find text field
        text = None
        for field in ["review_text", "comment", "text", "content", "description", "body", "message", "review"]:
            if field in review and review[field]:
                text = str(review[field])
                break
        
        if not text:
            continue
        
        analysis = process_review_text(text)
        all_products.extend(analysis["products"])
        all_issues.extend(analysis["issues"])
        all_facilities.extend(analysis["facilities"])
        sentiments.append(analysis["sentiment"])
    
    # Count frequencies
    product_counts = Counter(all_products)
    issue_counts = Counter(all_issues)
    facility_counts = Counter(all_facilities)
    sentiment_counts = Counter(sentiments)
    
    return {
        "products": dict(product_counts.most_common()),
        "issues": dict(issue_counts.most_common()),
        "facilities": dict(facility_counts.most_common()),
        "sentiments": dict(sentiment_counts),
        "total_reviews": len(reviews),
        "reviews_with_issues": sum(1 for r in reviews if any(
            field in r and r[field] and any(
                keyword in str(r[field]).lower() 
                for keywords in QUALITY_KEYWORDS.values() 
                for keyword in keywords
            )
            for field in ["review_text", "comment", "text", "content", "description", "body", "message", "review"]
        ))
    }

