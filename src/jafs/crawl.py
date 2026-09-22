import aiohttp
import asyncio

from bs4 import BeautifulSoup, Tag
from typing import TypedDict
from urllib.parse import urljoin, urlsplit

class AsyncCrawler():
    def __init__(self: AsyncCrawler, url: str, max_concurrency: int = 1, max_pages: int = 30) -> None:
		self.base_url = url
		self.base_domain = get_base_domain(self.base_url)
		self.page_data = {}
		self.max_pages = max_pages
		self.should_stop = False
		self.all_tasks = set()
		self.lock = asyncio.Lock()
		self.max_concurrency = max_concurrency
		self.semaphore = asyncio.Semaphore(self.max_concurrency)
		self.session = None

	async def __aenter__(self):
		self.session = aiohttp.ClientSession()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.session.close()

    async def add_page_visit(self: AsyncCrawler, normalized_url: str) -> bool:
		if self.should_stop:
			return False
		if len(self.page_data) >= self.max_pages:
			self.should_stop = True
			print("Reached maximum number of pages to crawl.")
			return False
		# default is no fetching or processing
		result = False
		# acquire the lock to proceed
		async with self.lock:
			# we visit when we do NOT find
			result = normalized_url not in self.page_data
			# if we visit we earmark while we have the lock
			if result:
				self.page_data[normalized_url] = {}
		return result

	async def get_html(self, url):
		try:
			headers = {
				"User-Agent": "BootCrawler/1.0",
			}
			async with self.session.get(url, headers=headers) as response:
				if response.status >= 400:
					raise Exception(f"HTTP error status: {response.status} {response.reason}")
				if "content-type" not in response.headers:
					raise Exception("Content-Type header missing from response")
				if "text/html" not in response.headers.get("content-type", ""):
					raise Exception(f'incorrect Content-Type: {response.headers.get("content-type", "")}')
				# print(f"Fetched page: {url}")
				return await response.text()
		except Exception as exc:
			print(f"Exception caught in get_html(): {exc}")
			raise

	async def crawl_page(self, current_url: str = None):
		if self.should_stop:
			return
		# print(f"{__name__}, {self.base_domain}, {current_url}")
		if current_url is None:
			# print("ODD: current_url is None")
			return
		if not get_base_domain(current_url) == self.base_domain:
			#print(f"SKIP: {get_base_domain(current_url)} not in {self.base_domain}")
			return
        
		normalized_url = normalize_url(current_url)
		if not await self.add_page_visit(normalized_url):
			return

			async with self.semaphore:
				try:
					html = await self.get_html(current_url)
				except asyncio.CancelledError:
					raise
			if html is None:
				return
			page_data = extract_page_data(html, current_url)
			print(f"data extracted for {normalize_url(current_url)}")
			async with self.lock:
				self.page_data[normalized_url] = page_data
			for url in page_data["outgoing_links"]:
				async with self.lock:
					task = asyncio.create_task(self.crawl_page(url))
					self.all_tasks.add(task)
		except asyncio.CancelledError:
			# if task cancelled, remove empty entry
			#   -> no PageData => remove page entry in site data
			async with self.lock:
				if self.site_data[normalized_url] == {}:
					del self.site_data[normalized_url]
				raise

	async def crawl(self):
		await self.crawl_page(self.base_url)
		await asyncio.gather(*self.all_tasks)
		return self.site_data


async def crawl_site_async(url, max_concurrency, max_pages):
	async with AsyncCrawler(url, max_concurrency, max_pages) as crawler:
		return await crawler.crawl()


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


def normalize_url(url: str) -> str:
	url_obj = urlsplit(url)
	return url_obj.netloc + url_obj.path.rstrip('/')


def get_base_domain(url: str) -> str:
	# assumption: valid url has been provided
	return urlsplit(url).netloc


def get_base_domain_url(url: str) -> str:
	obj = urlsplit(url)
	return obj.scheme + obj.netloc


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


def get_images_from_html(html: str, url: str) -> list[str]:
	return [urljoin(url, image["src"]) for image in BeautifulSoup(html, 'html.parser').find_all('img')]


def get_urls_from_html(html: str, url: str) -> list[str]:
	return [urljoin(url, link["href"]) for link in BeautifulSoup(html, 'html.parser').find_all('a')]
