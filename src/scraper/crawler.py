import aiohttp
import asyncio

from urllib.parse import urljoin, urlsplit


class AsyncCrawler():
    def __init__(self: AsyncCrawler, url: str, max_concurrency: int = 1, max_pages: int = 30) -> None:
		self.base_url = url
		self.base_domain = get_base_domain(self.base_url)
		self.page_data = {}
		if max_pages < 1:
			raise ValueError(f"tried setting max_pages to {max_pages}... think you are funny?!")
		self.max_pages = max_pages
		self.should_stop = False
		self.all_tasks = set()
		self.lock = asyncio.Lock()
		if max_concurrency < 1:
			raise ValueError(f"tried setting the maximum number of concurrent tasks to {max_concurrency}...have an exception...")
		self.max_concurrency = max_concurrency
		self.semaphore = asyncio.Semaphore(self.max_concurrency)
		self.session = None

	async def __aenter__(self):
		self.session = aiohttp.ClientSession()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.session.close()

    async def add_page_visit(self: AsyncCrawler, normalized_url: str) -> bool:
    	# do NOT add a page visit if:
    	#   - self.should_stop is True
    	#   - we have already added AT LEAST max_pages entries to self.page_data
		if self.should_stop:
			print("should_stop is True...no add")
			return False
		if len(self.page_data) >= self.max_pages:
			self.should_stop = True
			print(f"self.page_data has {len(self.page_data)} entries with a soft limit of {self.max_pages} entries")
			return False
		if normalized_url is None:
			raise ValueError("crawl_page: target url for crawl cannot be None")
		if not get_base_domain(current_url) == self.base_domain:
			print(f"crawl_page: skipping {current_url} - {get_base_domain(current_url)} not in {self.base_domain}")
			return
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

	async def crawl_page(self, current_url: str = None) -> None:
		normalized_url = normalize_url(current_url)
		if not await self.add_page_visit(normalized_url):
			return

		async with self.semaphore:
			try:
				html = await self.get_html(current_url)
			except:
				raise
			
			if html is None:
				raise ValueError(f"crawl_page - failed to get HTML for {current_url}")

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


def get_base_domain(url: str) -> str:
	# assumption: valid url has been provided
	return urlsplit(url).netloc


def get_base_domain_url(url: str) -> str:
	obj = urlsplit(url)
	return obj.scheme + obj.netloc


def normalize_url(url: str) -> str:
	url_obj = urlsplit(url)
	return url_obj.netloc + url_obj.path.rstrip('/')

