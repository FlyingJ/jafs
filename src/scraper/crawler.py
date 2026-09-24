import aiohttp
import asyncio

from urllib.parse import urljoin, urlsplit
from scraper.parsing import PageData, extract_page_data


class AsyncCrawler():
    def __init__(self, url: str, max_concurrency: int = 1, max_pages: int = 30) -> None:
        self.base_url = url
        self.base_netloc = get_netloc(self.base_url)
        self.visited: set[str] = set()
        self.page_data: dict[str, PageData] = {}
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
        self.session: aiohttp.ClientSession | None = None


    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()


    async def add_page_visit(self, url: str) -> bool:
        if get_netloc(url) != self.base_netloc:
            return False

        normalized_url = normalize_url(url)
        async with self.lock:
            if self.should_stop:
                return False
            
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                return False

            if normalized_url in self.visited:
                return False

            self.visited.add(normalized_url)
            return True


    async def get_html(self, url: str) -> str:
        if self.session is None:
            raise RuntimeError("crawler session is not open")

        headers = {
            "User-Agent": "BootCrawler/1.0",
        }
            
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP error status: {response.status} {response.reason}")

                if "content-type" not in response.headers:
                    raise Exception("Content-Type header missing from response")

                if "text/html" not in response.headers.get("content-type", ""):
                    raise Exception(f'incorrect Content-Type: {response.headers.get("content-type", "")}')

                return await response.text()

        except Exception as exc:
            print(f"Exception caught in get_html(): {exc}")
            raise


    async def crawl_page(self, url: str) -> None:
        async with self.semaphore:
            html = await self.get_html(url)

        page_data = extract_page_data(html, url)
        async with self.lock:
            self.page_data[normalize_url(url)] = page_data

        await self.spawn_crawls(page_data["outgoing_links"])


    async def spawn_crawls(self, urls: list[str]) -> None:
        for url in urls:
            if await self.add_page_visit(url):
                task = asyncio.create_task(self.crawl_page(url))
                self.all_tasks.add(task)
                task.add_done_callback(self.all_tasks.discard)


    async def crawl(self) -> dict[str, PageData]:
        start_url = self.base_url
        if await self.add_page_visit(start_url):
            await self.crawl_page(start_url)
        # this part is still janky because we may snapshot a still-growing set
        # and cause session closure prematurely
        await asyncio.gather(*self.all_tasks)
        return self.page_data



async def crawl_site_async(url: str, max_concurrency: int, max_pages: int) -> dict[str, PageData]:
    async with AsyncCrawler(url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()


def get_netloc(url: str) -> str:
    return urlsplit(url).netloc


def normalize_url(url: str) -> str:
    url_obj = urlsplit(url)
    return url_obj.netloc + url_obj.path.rstrip('/')

