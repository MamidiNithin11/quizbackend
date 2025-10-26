import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

WIKI_DOMAINS = ("en.wikipedia.org", "wikipedia.org")

def is_wikipedia_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return any(d in p.netloc for d in WIKI_DOMAINS)
    except Exception:
        return False

def scrape_wikipedia(url: str) -> tuple:
    """
    Returns (title, cleaned_text)
    Raises requests.HTTPError on network errors.
    """
    if not is_wikipedia_url(url):
        raise ValueError("URL is not a Wikipedia URL")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.5993.90 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    title_tag = soup.find(id="firstHeading")
    title = title_tag.get_text(strip=True) if title_tag else (
        soup.title.string.strip() if soup.title else "No title"
    )

    # Extract main content
    content = soup.find(id="mw-content-text") or soup.find("article") or soup.body
    if not content:
        raise ValueError("Could not find main content on the page")

    # Remove unwanted tags
    for tag in content.find_all(["sup", "table", "style", "script", "aside", "noscript"]):
        tag.decompose()

    for ref in content.find_all(class_=["references", "navbox", "vertical-navbox", "infobox"]):
        ref.decompose()

    # Collect and clean paragraphs
    paragraphs = []
    for p in content.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    cleaned_text = "\n\n".join(paragraphs).strip()
    return title, cleaned_text