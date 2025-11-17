from typing import List, Dict, Optional
from datetime import datetime, timedelta
from utils.db_access import get_reviews, get_review_text_fields
from utils.nlp_processor import aggregate_review_analysis, process_review_text

def analyze_reviews(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """Analyze reviews for quality/damage issues."""
    reviews = get_reviews(start_date=start_date, end_date=end_date)
    
    if not reviews:
        return {
            "products": {},
            "issues": {},
            "facilities": {},
            "sentiments": {},
            "total_reviews": 0,
            "reviews_with_issues": 0,
            "top_products_with_issues": [],
            "trending_concerns": []
        }
    
    aggregated = aggregate_review_analysis(reviews)
    
    # Get top products with issues
    top_products = sorted(
        aggregated["products"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Get trending concerns (top issues)
    top_issues = sorted(
        aggregated["issues"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Create product-issue pairs
    product_issue_pairs = []
    for review in reviews:
        text = None
        for field in get_review_text_fields():
            if field in review and review[field]:
                text = str(review[field])
                break
        
        if text:
            analysis = process_review_text(text)
            for product in analysis["products"]:
                for issue in analysis["issues"]:
                    product_issue_pairs.append(f"{product}:{issue}")
    
    from collections import Counter
    product_issue_counts = Counter(product_issue_pairs)
    
    return {
        **aggregated,
        "top_products_with_issues": [
            {"product": p, "count": c, "percentage": (c / aggregated["total_reviews"]) * 100}
            for p, c in top_products
        ],
        "trending_concerns": [
            {"issue": i, "count": c, "percentage": (c / aggregated["total_reviews"]) * 100}
            for i, c in top_issues
        ],
        "product_issue_matrix": dict(product_issue_counts.most_common(20))
    }

def get_review_summary(days: int = 7) -> Dict:
    """Get summary of reviews for the last N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return analyze_reviews(start_date=start_date, end_date=end_date)

def get_product_quality_summary(product: str, days: int = 30) -> Dict:
    """Get quality summary for a specific product."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    reviews = get_reviews(start_date=start_date, end_date=end_date)
    
    # Filter reviews mentioning the product
    product_reviews = []
    for review in reviews:
        text = None
        for field in get_review_text_fields():
            if field in review and review[field]:
                text = str(review[field])
                break
        
        if text and product.lower() in text.lower():
            product_reviews.append(review)
    
    if not product_reviews:
        return {
            "product": product,
            "total_reviews": 0,
            "issues": {},
            "sentiment_breakdown": {}
        }
    
    aggregated = aggregate_review_analysis(product_reviews)
    
    return {
        "product": product,
        "total_reviews": len(product_reviews),
        "issues": aggregated["issues"],
        "sentiment_breakdown": aggregated["sentiments"]
    }

