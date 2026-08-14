from pathlib import Path
from playwright.sync_api import sync_playwright

html_path = Path("bug_cases_report.html").resolve()
pdf_path = Path("RatioT_SCADA_Bug_Cases.pdf").resolve()

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{html_path}")
    page.pdf(
        path=str(pdf_path),
        format="A4",
        margin={"top": "16mm", "bottom": "16mm", "left": "16mm", "right": "16mm"},
        print_background=True,
        display_header_footer=False,
    )
    browser.close()

print(f"Generated {pdf_path}")
