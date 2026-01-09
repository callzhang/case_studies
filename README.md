# Feishu Case Study Scraper

This project automates the extraction of customer case studies from the [Feishu Customers Page](https://www.feishu.cn/customers). It effectively handles the dynamic content loading, navigates through all categories, and saves each case study as a clean Markdown file.

## Features

-   **Full Site Crawling**: Automatically expands the main list to discover over 500+ case studies.
-   **Robust Navigation**: Bypasses UI interaction flakiness by extracting direct URLs.
-   **Content Cleaning**: Converts HTML to Markdown and strips out irrelevant sections like "Related Recommendations".
-   **Rate Limiting**: Includes built-in delays to respect the server and avoid blocking.

## Prerequisites

-   Python 3.8+
-   Playwright
-   HTML2Text

## Installation

1.  **Clone the repository** (if applicable).
2.  **Install Python dependencies**:
    ```bash
    pip install playwright html2text
    ```
3.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

## Usage

Run the main scraper script:

```bash
python3 feishu_scraper.py
```

The script will:
1.  Launch a headless browser.
2.  Navigate to the Feishu customers page.
3.  Expand the list to find all case study URLs.
4.  Iterate through each URL, extracting and saving the content.

## Output

Scraped case studies are saved in the `case_studies/` directory.
Each file is named based on the case title (e.g., `Xiaomi_Use_Feishu.md`) and contains:
-   **Title**: The case study headline.
-   **URL**: The source link.
-   **Content**: The full text and images in Markdown format.

## Validation

To verify the quality of the scraped files (checking for empty or error pages), run:

```bash
python3 validate_cases.py
```
