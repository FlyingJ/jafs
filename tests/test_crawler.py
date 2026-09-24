import unittest

import scraper.crawler as sc

normalize_url_test_cases = [
    ("https://www.boot.dev/blog/path", "www.boot.dev/blog/path"),
    ("https://www.boot.dev/blog/path/", "www.boot.dev/blog/path"),
    ("http://www.boot.dev/blog/path", "www.boot.dev/blog/path"),
    ("http://www.boot.dev/blog/path/", "www.boot.dev/blog/path"),
    ("ftp://www.boot.dev/blog/path//", "www.boot.dev/blog/path"),
    ("https://example.com/search?stuff+things", "example.com/search"),
]

class TestCrawer(unittest.TestCase):
    def test_normalize_url(self):
        for url, expectation in normalize_url_test_cases:
            result = sc.normalize_url(url)
            self.assertEqual(result, expectation)

if __name__ == "__main__":
    unittest.main()


