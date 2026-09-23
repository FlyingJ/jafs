import aiohttp
import asyncio

from urllib.parse import urljoin, urlsplit


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

    async def add_page_visit(self, normalized_url: str) -> bool:
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

    async def crawl_page(self, current_url: str = None) -> None:
        if get_netloc(current_url) != self.base_netloc:
            return

        normalized_url = normalize_url(current_url)
        if not await self.add_page_visit(normalized_url):
            return

        # we are still here 
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

    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        await asyncio.gather(*self.all_tasks)
        return self.site_data


async def crawl_site_async(url: str, max_concurrency: int, max_pages: int) -> dict[str, PageData]:
    async with AsyncCrawler(url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()


def get_netloc(url: str) -> str:
    return urlsplit(url).netloc


def normalize_url(url: str) -> str:
    url_obj = urlsplit(url)
    return url_obj.netloc + url_obj.path.rstrip('/')

