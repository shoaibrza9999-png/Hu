import os
import requests
from bs4 import BeautifulSoup
import re

SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')

def fetch_price(url):
    """
    Fetches the Amazon product page using ScraperAPI and extracts the title and price.
    Returns a tuple: (title, price_as_float)
    """
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'render': 'false', # Often we just need the HTML.
        'country_code': 'us'
    }

    html = ""
    # Send request to ScraperAPI
    # Fallback to direct request if ScraperAPI fails (e.g. invalid API key or out of credits)
    try:
        response = requests.get('http://api.scraperapi.com', params=payload)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"ScraperAPI failed: {e}. Falling back to direct request...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
        except Exception as e2:
            print(f"Direct request failed: {e2}")
            # Try once more without raise_for_status to see if we get *some* HTML,
            # as Amazon sometimes returns 503 but gives the page.
            if "response" in locals() and response is not None and response.text:
                html = response.text
            else:
                return "Unknown Title", None

    soup = BeautifulSoup(html, 'html.parser')

    # Extract Title
    title_element = soup.find(id='productTitle')
    title = title_element.text.strip() if title_element else "Unknown Title"

    # Extract Price
    # Amazon has many different price selectors. We try the most common ones.
    price_selectors = [
        'span.a-price span.a-offscreen',
        'span#priceblock_ourprice',
        'span#priceblock_dealprice',
        'span.a-color-price',
        'span.apexPriceToPay > span.a-offscreen',
        'div[data-csa-c-buying-option-type="NEW"] span.a-price span.a-offscreen'
    ]

    price_str = None
    for selector in price_selectors:
        price_element = soup.select_one(selector)
        if price_element and price_element.text.strip():
            price_str = price_element.text.strip()
            break

    if not price_str:
        print("Could not find price in the HTML.")
        return title, None

    # Clean the price string (remove currency symbols, commas)
    # e.g., "$1,234.56" -> "1234.56"
    # "₹1,234.56" -> "1234.56"
    clean_price = re.sub(r'[^\d.]', '', price_str)

    try:
        # Some prices might be ranges or have extra text, take the first valid number
        # If it's something like "12.99 - 14.99", this basic regex approach might just mash it together.
        # Let's extract the first float-like pattern.
        match = re.search(r'\d+(\.\d{1,2})?', clean_price)
        if match:
             return title, float(match.group())
        return title, float(clean_price)
    except ValueError:
        print(f"Failed to parse price string: {price_str}")
        return title, None

if __name__ == '__main__':
    # Simple test run when executing the scraper directly
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.amazon.com/dp/B08F7PTF53'
    print(f"Testing with URL: {test_url}")
    print(fetch_price(test_url))
