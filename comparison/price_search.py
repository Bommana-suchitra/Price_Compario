import requests
import os
import re
from urllib.parse import quote_plus

# ==================================================
# CONFIGURATION
# ==================================================
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', "ad7aedaa34msh57cb97ff1ebaf7ap184a0djsn5c0a4ca44f30")
SERP_API_KEY = os.environ.get('SERP_API_KEY', "01d3edbb3a4293f7397d9d41ba4c398eb500c0bae344516a4a4e715e6a3b0a25")  
API_ERRORS = []
TIMEOUT = 10  # seconds timeout for all API requests

# ==================================================
# UTILITIES
# ==================================================
def clean_price(price):
    try:
        return float(re.sub(r"[^\d.]", "", str(price)))
    except:
        return None

# ==================================================
# AMAZON SEARCH
# ==================================================
def amazon_search(query):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    params = {"query": query, "page": "1", "country": "IN"}
    results = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        data = response.json()
        products = data.get("data", {}).get("products", [])
        for item in products[:1]:
            price = clean_price(item.get("product_price") or item.get("price"))
            if not price:
                continue
            results.append({
                "title": item.get("product_title") or item.get("title"),
                "price": price,
                "image": item.get("product_photo") or item.get("image"),
                "rating": item.get("product_star_rating"),
                "link": item.get("product_url"),
                "source": "Amazon"
            })
    except Exception as e:
        API_ERRORS.append(f"Amazon Error: {e}")
    return results

# ==================================================
# EBAY SEARCH (SERP API)
# ==================================================


def ebay_search(query):
    print("🔵 EBAY QUERY:", query)

    url = "https://serpapi.com/search"
    params = {
        "engine": "ebay",
        "ebay_domain": "ebay.com",
        "_nkw": query,
        "api_key": SERP_API_KEY
    }

    results = []

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("organic_results", [])
        print("🟢 EBAY ITEMS FOUND:", len(items))

        for item in items[:1]:
            price_data = item.get("price", {})
            price = price_data.get("extracted") if isinstance(price_data, dict) else None

            results.append({
                "title": item.get("title", "N/A"),
                "price": price,
                "image": item.get("thumbnail"),
                "rating": item.get("seller", {}).get("positive_feedback_in_percentage"),
                "link": item.get("link"),
                "source": "eBay"
            })

    except Exception as e:
        API_ERRORS.append(f"eBay API Error: {e}")
        print("🔴 EBAY ERROR:", e)

    return results



# ==================================================
# GOOGLE SEARCH (SERP API)
# ==================================================
def google_search(query):
    if not SERP_API_KEY:
        API_ERRORS.append("SERP_API_KEY missing for Google")
        return []

    url = "https://serpapi.com/search"
    params = {
    "engine": "google_shopping",
    "q": query,
    "api_key": SERP_API_KEY,
    "gl": "IN",
    "hl": "en",
}

    results = []

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        data = response.json()
        items = data.get("shopping_results", [])
        for item in items[:1]:
            price = clean_price(item.get("price"))
            if not price:
                continue
            results.append({
                "title": item.get("title"),
                "price": price,
                "image": item.get("thumbnail"),
                "rating": item.get("seller", {}).get("positive_feedback_in_percentage"),
                "link": item.get("link"),
                "source": "Google"
            })
    except Exception as e:
        API_ERRORS.append(f"Google Error: {e}")
    return results
