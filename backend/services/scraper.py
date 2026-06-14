"""
scraper.py — Web scraping service for extracting text content from recipe URLs.

Uses requests to fetch the HTML and BeautifulSoup to parse it.
Strips out non-content elements (scripts, styles, nav, ads, footers)
to give the AI only the relevant recipe text to work with.

If direct scraping fails (sites block cloud IPs), falls back to a
free proxy service to fetch the page.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


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

# Free proxy services to try when direct scraping is blocked
PROXY_URLS = [
    "https://api.allorigins.win/raw?url={}",
    "https://api.codetabs.com/v1/proxy?quest={}",
]


def _fetch_html(url: str) -> str:
    """
    Fetch the HTML content of a URL.
    Tries direct request first, then falls back to proxy services
    if the site blocks cloud server IPs.

    Args:
        url: The full URL to fetch

    Returns:
        Raw HTML string

    Raises:
        ValueError: If all methods fail
    """
    # Attempt 1: Direct request
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.MissingSchema:
        raise ValueError(f"Invalid URL format: {url}")
    except requests.exceptions.ConnectionError:
        pass  # Try proxy fallback
    except requests.exceptions.Timeout:
        pass  # Try proxy fallback
    except requests.exceptions.HTTPError:
        pass  # Try proxy fallback

    # Attempt 2: Try proxy services as fallback
    encoded_url = quote(url, safe='')
    for proxy_template in PROXY_URLS:
        try:
            proxy_url = proxy_template.format(encoded_url)
            response = requests.get(proxy_url, timeout=20)
            response.raise_for_status()
            if len(response.text) > 100:  # Sanity check
                return response.text
        except Exception:
            continue

    raise ValueError(
        f"Could not fetch the recipe page. The site may be blocking automated requests. "
        f"URL: {url}"
    )


def _clean_html(html: str) -> str:
    """
    Parse HTML and extract clean text content suitable for AI extraction.

    Args:
        html: Raw HTML string

    Returns:
        Cleaned text content
    """
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

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

    # Truncate if too long (LLMs have context window limits)
    max_chars = 15000
    if len(cleaned_text) > max_chars:
        cleaned_text = cleaned_text[:max_chars] + '\n\n[Content truncated...]'

    return cleaned_text


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
    html = _fetch_html(url)
    return _clean_html(html)
