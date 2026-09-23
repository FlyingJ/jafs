import unittest

import scraper.parsing as sp


get_heading_from_html_test_cases = [
    ("""<html><body><h1>Welcome to Boot.dev</h1><main><p>Learn to code by building real projects.</p><p>This is the second paragraph.</p></main></body></html>""", "Welcome to Boot.dev"),
    ("""<html><body><h1>Test Title</h1></body></html>""", "Test Title"),
    ("""<html><body><p>Some text</p><h2>Test Title</h2></body></html>""", "Test Title"),
    ("""<html><body></body></html>""", ""),
    ("""<html><body><p>text</p></body></html>""", ""),
]

get_first_paragraph_from_html_test_cases = [
    ("""<html><body><p>A</p></body></html>""", "A"),
    ("""<html><body><p>A</p><main><p>B</p></main></body></html>""", "B"),
    ("""<html><body><p>Outside paragraph.</p><main><p>Main paragraph.</p></main></body></html>""", "Main paragraph."),
    ("""<html><body></body></html>""", ""),
]

get_urls_from_html_test_cases = [
    (("""<html><body></body></html>""", "https://www.example.com/"), []),
    (("""<html><body></body></html>""", ""), []),
    (("""""", "https://www.example.com/"), []),
    (("""""", ""), []),
    (("""<html><body><a href="https://crawler-test.com">Go to Boot.dev</a><img src="/logo.png" alt="Boot.dev Logo" /></body></html>""", "https://example.com/"), ["https://crawler-test.com", ]),
    (("""<html><body><h1>Test Title</h1><p>This is the first paragraph.</p><a href="/link1">Link 1</a> <img src="/image1.jpg" alt="Image 1"> </body></html>""", "https://crawler-test.com"), ["https://crawler-test.com/link1", ]),
    (("""<html><body><h1>Test Title</h1><p>This is the first paragraph.</p><a href="http://some.ai/thingy-for-the-masses/">Link 1</a> <img src="/image1.jpg" alt="Image 1"> </body></html>""", "https://crawler-test.com"), ["http://some.ai/thingy-for-the-masses/", ]),
    (("""<html><body><h1>Test Title</h1><p>This is the first paragraph.</p><a href="http://some.ai/thingy-for-the-masses/">AI Link 1</a><a href="/Link1.html">Link 1</a> <img src="/image1.jpg" alt="Image 1"> </body></html>""", "https://crawler-test.com"), ["http://some.ai/thingy-for-the-masses/", "https://crawler-test.com/Link1.html", ]),
]

get_images_from_html_test_cases = [
    (("""<html><body></body></html>""", "https://www.example.com/"), []),
    (("""<html><body></body></html>""", ""), []),
    (("""""", "https://www.example.com/"), []),
    (("""""", ""), []),
    (("""<html><body><a href="https://crawler-test.com">Go to Boot.dev</a><img src="/logo.png" alt="Boot.dev Logo" /></body></html>""", "https://example.com/"), ["https://example.com/logo.png"]),
]

extract_page_data_test_cases = [
    (
        ('''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>''',
        "https://crawler-test.com"),
        {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"]
        }
    ),
    (
        ('''

<!DOCTYPE html>

<html lang="en" data-theme="system">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="manifest" href="/manifest.json">
    
    <title>The Brutalist Report - about</title>
    <meta name="description" content="The day's headlines delivered to you without bullshit. - about">
    
    <title>The Brutalist Report</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <meta name="keywords" content="brutalist, news, brutalism, report, cyrus">
    <meta name="description" content="The day's headlines delivered to you without bullshit.">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            overflow-wrap: break-word;
            word-break: break-word;
        }
        div.banner a:visited, a:link {
            text-decoration: none;
            color: black;
        }
        nav a:visited, a:link {
            text-decoration: none;
            color: blue;
        }
       .brutal-grid {
            display: grid;
            grid-auto-flow: row;
            grid-template-columns: repeat(3, 1fr);
        }
        div.about {
            max-width: 75%;
            margin-right: auto;
        }
        .separator {
            margin: 20px 0;
            border-top: 1px solid #ccc;
        }

        li {
            padding-bottom: 0.5rem;
        }

        .login-link {
            position: absolute;
            top: 0;
            right: 0;
            margin: 1em;
        }

        .theme-toggle {
            position: absolute;
            top: 2.2em;
            right: 0;
            margin: 1em;
            font-size: 0.85em;
        }
        .theme-toggle form { display: inline; }
        .theme-toggle button {
            background: none;
            border: none;
            border-radius: 0;
            padding: 0;
            margin: 0;
            font: inherit;
            font-size: inherit;
            cursor: pointer;
            color: blue;
            text-decoration: none;
        }

        @media (max-width: 800px) {
            .brutal-grid {
                display: grid;
                grid-auto-flow: row;
                grid-template-columns: repeat(1, 1fr);
            }
            div.about {
                max-width: 100%;
                margin: auto;
            }
            .banner {
                padding-top: 3em;
            }
            .theme-toggle {
                top: 1.8em;
            }
        }
        @media (prefers-color-scheme: dark) {
            html[data-theme="system"] body { background-color: #000; color: #e8e6e3; }
            html[data-theme="system"] div.banner a:visited, html[data-theme="system"] a:link { text-decoration: none; color: white; }
            html[data-theme="system"] nav a:visited, html[data-theme="system"] a:link { text-decoration: none; color: #3391ff; }
            html[data-theme="system"] a:link { color: #3391ff; }
            html[data-theme="system"] a:visited { color: #ba55d3; }
            html[data-theme="system"] .theme-toggle button { color: #3391ff; }
        }

        html[data-theme="dark"] body { background-color: #000; color: #e8e6e3; }
        html[data-theme="dark"] div.banner a:visited, html[data-theme="dark"] a:link { text-decoration: none; color: white; }
        html[data-theme="dark"] nav a:visited, html[data-theme="dark"] a:link { text-decoration: none; color: #3391ff; }
        html[data-theme="dark"] a:link { color: #3391ff; }
        html[data-theme="dark"] a:visited { color: #ba55d3; }
        html[data-theme="dark"] .theme-toggle button { color: #3391ff; }

        html[data-theme="light"] body { background-color: #fff; color: #000; }
        html[data-theme="light"] div.banner a:visited, html[data-theme="light"] a:link { text-decoration: none; color: black; }
        html[data-theme="light"] nav a:visited, html[data-theme="light"] a:link { text-decoration: none; color: blue; }
        html[data-theme="light"] a:link { color: blue; }
        html[data-theme="light"] a:visited { color: purple; }
        html[data-theme="light"] .theme-toggle button { color: blue; }

        .box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
            position: relative;
            float: left;
            margin-bottom: 50px;
        }

        ul {
            margin: 0;
            padding: 10px;
            list-style: none;
            padding-bottom: 40px;
            list-style-type: disc;
            margin-top: 80px;  
        }

        ul li {
            margin-bottom: 10px;
        }

        .purchase {
            position: absolute;
            bottom: 20px;
            right: 20px;
        }

        button {
            background-color: #333;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }

        .cancel-text {
            position: absolute;
            bottom: 0px;
            left: 20px;
            font-style: italic;
        }

        .header {
            font-size: 36px;
            color: white;
            position: absolute;
            top: 0px;
            left: 10px;
            margin-top: 20px;  
        }

    </style>
</head>

<body>
<header>
    <div class="banner"><h1><a href="/">The Brutalist Report</a></h1></div>
    <aside>The day's headlines delivered to you without bullshit. Last updated Tuesday, July 21, 2026 9:38 AM (PT).</aside>
    
        <div class="login-link"><a href="/login">login</a></div>
    
    <div class="theme-toggle">
        <b>system</b> |
        <form method="POST" action="/theme"><input type="hidden" name="_csrf" value="NXrglwPShUm_mycyNdBBNprBf14="><input type="hidden" name="theme" value="light"><button type="submit">light</button></form> |
        <form method="POST" action="/theme"><input type="hidden" name="_csrf" value="NXrglwPShUm_mycyNdBBNprBf14="><input type="hidden" name="theme" value="dark"><button type="submit">dark</button></form>
    </div>
</header>
<br>

<nav>
    <a href="/">Home</a> |
    <a href="/topic/all">All</a> |
    
    <a href="/topic/tech?">Tech</a> |
    
    <a href="/topic/news?">News</a> |
    
    <a href="/topic/business?">Business</a> |
    
    <a href="/topic/science?">Science</a> |
    
    <a href="/topic/gaming?">Gaming</a> |
    
    <a href="/topic/culture?">Culture</a> |
    
    <a href="/topic/politics?">Politics</a> |
    
    <a href="/topic/sports?">Sports</a> |
    
    <a href="/wordcloud?">WordCloud</a> |
    <a href="/summary">Summarizer</a> |
    
    <a href="/premium">Premium</a> |
    
    <a href="https://apps.apple.com/app/brutalist-report/id6756546583">iOS App</a> |
    <img src="/public/new.gif" alt="New Icon"/><a href="https://brutalist.mov">Live</a> |
    <a href="/about">About</a>
</nav>

<br><br>


<div class="about">
    <p>Do you feel it too? There's something wrong with the web.</p>

    <p><a href="https://brutalist.network">The Brutalist Network</a> is a response to that feeling. It's for people who want a simple, reliable, and performant online experience. <a href="https://benhoyt.com/writings/the-small-web-is-beautiful/">Small web</a> services that are built using simple HTML and CSS with no JavaScript or complex client-side processing.</p>
    <p>It won't be for everyone. Some will deem it too spartan. Too rigid and stuck in the 90s. That's okay. This isn't for them. It is for those of us who long for a return to the uncomplicated elegance of the early web. For those who believe that less is more.</p>
    <br>
</div>

</body>

<footer>
<hr>
    <p style="text-align:center">a <a href="https://brutalist.network">Brutalist Network</a> snafu</p>
</footer>
</html>
''',
            "https://brutalist.report/about"
        ),
        {
            "url": "https://brutalist.report/about",
            "heading": "The Brutalist Report",
            "first_paragraph": "Do you feel it too? There's something wrong with the web.",
            "outgoing_links": [
                'https://brutalist.report/',
                'https://brutalist.report/login',
                'https://brutalist.report/',
                'https://brutalist.report/topic/all',
                'https://brutalist.report/topic/tech',
                'https://brutalist.report/topic/news',
                'https://brutalist.report/topic/business',
                'https://brutalist.report/topic/science',
                'https://brutalist.report/topic/gaming',
                'https://brutalist.report/topic/culture',
                'https://brutalist.report/topic/politics',
                'https://brutalist.report/topic/sports',
                'https://brutalist.report/wordcloud',
                'https://brutalist.report/summary',
                'https://brutalist.report/premium',
                'https://apps.apple.com/app/brutalist-report/id6756546583',
                'https://brutalist.mov',
                'https://brutalist.report/about',
                'https://brutalist.network',
                'https://benhoyt.com/writings/the-small-web-is-beautiful/',
                'https://brutalist.network',
            ],
            "image_urls": [
                "https://brutalist.report/public/new.gif",
            ],
        }
    )
]


class TestParsing(unittest.TestCase):
    def test_NAME(self):
        for TEST_CASE in TEST_CASES:
            result = NAME(args)
            self.assertEqual(result, expectation)


    def test_normalize_url(self):
        for text, expectation in normalize_url_test_cases: 
            result = crawl.normalize_url(text)
            self.assertEqual(result, expectation)


    def test_get_heading_from_html(self):
        for html, expectation in get_heading_from_html_test_cases:
            result = crawl.get_heading_from_html(html)
            self.assertEqual(result, expectation)


    def test_get_first_paragraph_from_html(self):
        for html, expectation in get_first_paragraph_from_html_test_cases:
            result = crawl.get_first_paragraph_from_html(html)
            self.assertEqual(result, expectation)


    def test_get_urls_from_html(self):
        for ((html, url), expectation) in get_urls_from_html_test_cases:
            result = crawl.get_urls_from_html(html, url)
            self.assertEqual(result, expectation)


    def test_get_images_from_html(self):
        for ((html, url), expectation) in get_images_from_html_test_cases:
            result = crawl.get_images_from_html(html, url)
            self.assertEqual(result, expectation)


    def test_extract_page_data(self):
        for ((html, url), expectation) in extract_page_data_test_cases:
            result = crawl.extract_page_data(html, url)
            self.assertEqual(result, expectation)



if __name__ == "__main__":
    unittest.main()

