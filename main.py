import asyncio

from scraper.crawler import crawl_site_async


async def main() -> None:
    page_data = await crawl_site_async(
        "https://learnwebscraping.dev/practice/ecommerce/",
        max_concurrency=5,
        max_pages=30,
    )

    print(f"crawled {len(page_data)} pages")


if __name__ == "__main__":
    asyncio.run(main())
