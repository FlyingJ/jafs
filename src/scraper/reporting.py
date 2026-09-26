import json

from scraper.parsing import PageData

def write_json_report(
    page_data: dict[str, PageData],
    filename: str = "report.json",
) -> bool:
    try:
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(page_data, handle, indent=2)
    except Exception as exc:
        print(f"file write fail: {exc}")
        return False

    return True
