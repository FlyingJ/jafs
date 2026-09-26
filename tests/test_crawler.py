import unittest

import scraper.crawler as sc

get_netloc_test_cases = [
    ("https://www.boot.dev/blog/path", "www.boot.dev"),
    ("https://www.microsoft.com/", "www.microsoft.com"),
    ("ftp://www.boot.dev/blog/path", "www.boot.dev"),
    ("gopher://www.boot.dev/blog/path/", "www.boot.dev"),
    ("ftp://www.boot.dev/blog/path//", "www.boot.dev"),
    ("https://example.com/search?stuff+things", "example.com"),
    ("schleem://some.random.do/and/a/path?with+options", "some.random.do"),
    ("fungus", ""),
]

normalize_url_test_cases = [
    ("https://www.boot.dev/blog/path", "www.boot.dev/blog/path"),
    ("https://www.boot.dev/blog/path/", "www.boot.dev/blog/path"),
    ("http://www.boot.dev/blog/path", "www.boot.dev/blog/path"),
    ("http://www.boot.dev/blog/path/", "www.boot.dev/blog/path"),
    ("ftp://www.boot.dev/blog/path//", "www.boot.dev/blog/path"),
    ("https://example.com/search?stuff+things", "example.com/search"),
]

class TestCrawer(unittest.TestCase):
    def test_get_netloc(self):
        for url, expectation in get_netloc_test_cases:
            result = sc.get_netloc(url)
            self.assertEqual(result, expectation)

    def test_normalize_url(self):
        for url, expectation in normalize_url_test_cases:
            result = sc.normalize_url(url)
            self.assertEqual(result, expectation)


if __name__ == "__main__":
    unittest.main()


