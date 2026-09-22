import json

from crawl import PageData


def write_json_report(
    page_data: dict[str, PageData],
    filename: str = "report.json"
    ) -> bool:
    try:
        data = sorted(page_data.values(), key=lambda p: p["url"])
    except Exception as e:
        print(f"list sort fail: {e}")
        return False

    try:
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except Exception as e:
        print(f"file write fail: {e}")
        return False

    return True