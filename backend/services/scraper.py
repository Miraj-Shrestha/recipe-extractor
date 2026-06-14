"""
scraper.py — Web scraping service for extracting text content from recipe URLs.

Uses requests to fetch the HTML and BeautifulSoup to parse it.
Strips out non-content elements (scripts, styles, nav, ads, footers)
to give the AI only the relevant recipe text to work with.
"""

import requests
from bs4 import BeautifulSoup


# Headers to mimic a real Chrome browser (many recipe sites block basic scrapers)
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/126.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Chromium";v="126", "Google Chrome";v="126", "Not-A.Brand";v="8"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

# HTML tags that contain non-content elements we want to remove
TAGS_TO_REMOVE = [
    'script', 'style', 'nav', 'footer', 'header',
    'aside', 'iframe', 'noscript', 'svg', 'form',
]

# CSS classes/ids commonly used for ads and non-content sections
AD_PATTERNS = [
    'ad', 'advertisement', 'sidebar', 'comment', 'social',
    'share', 'newsletter', 'popup', 'modal', 'cookie',
    'related-post', 'recommended', 'promo',
]


def scrape_url(url: str) -> str:
    """
    Scrape a recipe URL and return the cleaned text content.

    Args:
        url: The full URL of the recipe page

    Returns:
        Cleaned text content of the page, ready for AI extraction

    Raises:
        ValueError: If the URL is invalid or the page can't be fetched
    """
    try:
        # Fetch the page HTML
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        raise ValueError(f"Invalid URL format: {url}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to: {url}")
    except requests.exceptions.Timeout:
        raise ValueError(f"Request timed out for: {url}")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error {e.response.status_code} for: {url}")

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove non-content tags
    for tag_name in TAGS_TO_REMOVE:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove elements with ad-related class names or IDs
    for pattern in AD_PATTERNS:
        # Remove by class
        for element in soup.find_all(class_=lambda c: c and pattern in c.lower()):
            element.decompose()
        # Remove by id
        for element in soup.find_all(id=lambda i: i and pattern in i.lower()):
            element.decompose()

    # Try to find the main content area first (more focused extraction)
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find(class_='recipe') or
        soup.find(class_='content') or
        soup.find(id='content') or
        soup.find('body') or
        soup
    )

    # Extract text, collapsing whitespace
    text = main_content.get_text(separator='\n', strip=True)

    # Clean up excessive blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = '\n'.join(lines)

    # Truncate if too long (Gemini has a context window limit)
    max_chars = 15000
    if len(cleaned_text) > max_chars:
        cleaned_text = cleaned_text[:max_chars] + '\n\n[Content truncated...]'

    return cleaned_text
