import json

from scraper.reporting import write_json_report


def test_write_json_report(tmp_path):
    output_file = tmp_path / "report.json"

    page_data: dict[str, PageData] = {
        "example.com/": {
            "url": "https://example.com/",
            "heading": "Example Domain",
            "first_paragraph": "This domain is for use in illustrative examples.",
            "outgoing_links": [
                "https://example.com/about",
                "https://example.com/contact",
            ],
            "image_urls": [
                "https://example.com/images/logo.png",
            ],
        }
    }

    write_json_report(page_data, output_file)

    assert output_file.exists()

    with output_file.open() as f:
        report = json.load(f)

    assert report == page_data



def test_write_json_report_empty(tmp_path):
    output_file = tmp_path / "report.json"
    page_data: dict[str, PageData] = {}

    write_json_report(page_data, output_file)

    with output_file.open() as f:
        report = json.load(f)

    assert report == {}

