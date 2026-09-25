from bs4 import BeautifulSoup, Tag
from typing import TypedDict
from urllib.parse import urljoin, urlsplit

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def extract_page_data(html: str, url: str) -> PageData:
    return {
        "url": url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, url),
        "image_urls": get_images_from_html(html, url),
    }


def get_heading_from_html(html: str) -> str:
    # assumption: valid HTML has been provided
    result = "" # default return empty string
    soup = BeautifulSoup(html, 'html.parser')
    # assumption: soup has been provided
    if soup.h1:
        result = soup.h1.string
    elif soup.h2:
        result = soup.h2.string
    return result


def get_first_paragraph_from_html(html: str) -> str:
    # assumption: valid HTML has been provided
    result = "" # default return empty string
    soup = BeautifulSoup(html, 'html.parser')
    # assumption: soup has been provided
    if soup.main and soup.main.p:
        result = soup.main.p.string
    elif soup.p:
        result = soup.p.string
    return result


def get_urls_from_html(html: str, url: str) -> list[str]:
    return [urljoin(url, link["href"]) for link in BeautifulSoup(html, 'html.parser').find_all('a')]


def get_images_from_html(html: str, url: str) -> list[str]:
    return [urljoin(url, image["src"]) for image in BeautifulSoup(html, 'html.parser').find_all('img')]

