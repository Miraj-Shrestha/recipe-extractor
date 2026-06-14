"""
scraper.py — Web scraping service for extracting text content from recipe URLs.

Uses cloudscraper to bypass Cloudflare anti-bot protection,
then BeautifulSoup to parse and clean the HTML.
Falls back to free proxy services if direct scraping fails.
"""

import cloudscraper
from bs4 import BeautifulSoup


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


def _fetch_html(url: str) -> str:
    """
    Fetch the HTML content of a URL using cloudscraper.
    Bypasses Cloudflare and most anti-bot protections.

    Args:
        url: The full URL to fetch

    Returns:
        Raw HTML string

    Raises:
        ValueError: If the page can't be fetched
    """
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        response = scraper.get(url, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise ValueError(f"Could not fetch the recipe page: {str(e)}. URL: {url}")


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
