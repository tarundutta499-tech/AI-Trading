import urllib.parse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
import requests

analyzer = SentimentIntensityAnalyzer()
NEWS_API_KEY = "7d98ec73d5fb4058869876b5f0bf02a8"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_news_sentiment(ticker_symbol):
    clean_ticker = ticker_symbol.replace(".NS", "")
    # Search for the company name strictly
    query = urllib.parse.quote(f'"{clean_ticker}"')
    
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("status") != "ok" or not data.get("articles"):
            return {"sentiment_score": 50, "positive_articles": 0, "neutral_articles": 0, "negative_articles": 0}, []
            
        articles = data["articles"]
    except Exception as e:
        print(f"News API Error for {ticker_symbol}: {e}")
        return {"sentiment_score": 50, "positive_articles": 0, "neutral_articles": 0, "negative_articles": 0}, []
        
    recent_news = []
    unique_titles = []
    
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    total_compound = 0
    valid_count = 0
    
    # 48 hour cutoff
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=48)
    
    for entry in articles:
        if len(recent_news) >= 10:
            break
            
        try:
            # News API timestamp format: 2024-03-01T12:00:00Z
            pub_date_str = entry.get("publishedAt", "")
            if pub_date_str:
                pub_date = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)
        except Exception:
            pub_date = datetime.now(timezone.utc)
            
        if pub_date >= cutoff_time:
            title = entry.get("title") or ""
            description = entry.get("description") or ""
            
            if not title or title == "[Removed]":
                continue
                
            # Deduplication
            is_duplicate = False
            for ut in unique_titles:
                if similar(title, ut) > 0.8:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue
                
            unique_titles.append(title)
            
            # Combine title and description for more robust sentiment analysis
            full_text = f"{title}. {description}"
            sentiment = analyzer.polarity_scores(full_text)
            compound = sentiment['compound']
            
            total_compound += compound
            valid_count += 1
            
            if compound >= 0.05:
                positive_count += 1
            elif compound <= -0.05:
                negative_count += 1
            else:
                neutral_count += 1
            
            recent_news.append({
                "title": title,
                "link": entry.get("url", ""),
                "published": entry.get("publishedAt", ""),
                "sentiment": compound,
                "ticker": ticker_symbol
            })
            
    if valid_count == 0:
        return {"sentiment_score": 50, "positive_articles": 0, "neutral_articles": 0, "negative_articles": 0}, []
        
    avg_compound = total_compound / valid_count
    # Convert compound (-1 to 1) to a 0-100 scale
    sentiment_score_100 = (avg_compound + 1) * 50
    
    stats = {
        "sentiment_score": sentiment_score_100,
        "positive_articles": positive_count,
        "neutral_articles": neutral_count,
        "negative_articles": negative_count
    }
    
    return stats, recent_news
