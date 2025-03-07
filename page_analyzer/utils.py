from urllib.parse import urlparse

import validators
from bs4 import BeautifulSoup


def normalize_url(url):
    """Normalizes a URL by removing path and query parameters."""
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def validate(url):
    """
    Validate a URL.

    Args:
        url (str): URL to validate.

    Returns:
        str: Error message if URL is invalid, otherwise None.
    """
    if len(url) > 255:
        return 'URL превышает 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'


def strip_and_truncate_text(text, length=255):
    """Strip whitespace and truncate text to a specified length."""
    return text.strip()[:length]


def parse_html_metadata(html_content):
    """
    Parse HTML content and extract metadata (h1, title, description).

    Args:
        html_content (str): HTML content to parse.

    Returns:
        tuple: (h1, title, description) as stripped and truncated strings.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    h1_tag = soup.find("h1")
    title_tag = soup.title
    meta_desc = soup.find("meta", attrs={"name": "description"})

    h1 = strip_and_truncate_text(h1_tag.text if h1_tag else "")
    title = strip_and_truncate_text(title_tag.text if title_tag else "")
    description = strip_and_truncate_text(
        meta_desc["content"] if
        meta_desc and "content" in meta_desc.attrs
        else ""
    )

    return h1, title, description
