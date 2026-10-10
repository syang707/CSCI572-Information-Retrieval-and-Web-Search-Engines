from playwright.sync_api import sync_playwright
from time import sleep
from random import randint
from urllib.parse import urlparse, parse_qs, unquote
import json


USER_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/132.0.0.0 Safari/537.36'
}


class SearchEngine:

    @staticmethod
    def search(page, query, sleep_time=True):

        # Random delay between 10 and 100 seconds
        # Required by the assignment
        if sleep_time:
            delay = randint(10, 100)
            print()
            print("Waiting", delay, "seconds before searching...")
            sleep(delay)

        # Create DuckDuckGo search URL
        temp_url = '+'.join(query.split())
        url = 'https://www.duckduckgo.com/html/?q=' + temp_url

        print()
        print("Searching:", query)
        print("URL:", url)

        # Open search page
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        print("Page loaded.")
        print("Page title:", page.title())

        # Wait for the search results to finish loading
        print("Waiting 5 seconds for the page...")
        page.wait_for_timeout(5000)

        # Scrape search results
        results = SearchEngine.scrape_search_result(page)

        print("Number of results:", len(results))

        for i, result in enumerate(results, start=1):
            print(i, result)

        return results

    @staticmethod
    def scrape_search_result(page):

        # Professor's selector for DuckDuckGo
        raw_results = page.locator("a.result__a")

        print("Found:", raw_results.count())

        results = []

        for i in range(min(raw_results.count(), 10)):

            # Get href
            link = raw_results.nth(i).get_attribute("href")

            if link is None:
                continue

            # Extract the real URL from DuckDuckGo redirect URL
            if "uddg=" in link:
                parsed_url = urlparse(link)
                query_parameters = parse_qs(parsed_url.query)

                if "uddg" in query_parameters:
                    link = query_parameters["uddg"][0]
                    link = unquote(link)

            # Remove duplicate URLs
            if link not in results:
                results.append(link)

            # Only need the top 10
            if len(results) == 10:
                break

        return results


def main():

    # Read the 100 queries from the text file
    query_file = "100QueriesSet4.txt"

    with open(
        query_file,
        "r",
        encoding="utf-8"
    ) as file:

        queries = [
            line.strip()
            for line in file
            if line.strip()
        ]

    print("Total queries in file:", len(queries))
    print("Starting scraping of all queries.")

    all_results = {}

    with sync_playwright() as p:

        # Use a visible Chromium browser
        browser = p.chromium.launch(
            headless=False
        )

        # Create one page and reuse it for all queries
        page = browser.new_page(
            user_agent=USER_AGENT['User-Agent']
        )

        # Run all queries
        for number, query in enumerate(queries, start=1):

            print()
            print("=" * 70)
            print("Query", number, "of", len(queries))
            print("=" * 70)

            results = SearchEngine.search(
                page,
                query,
                sleep_time=True
            )

            # Query string is used as the JSON key
            all_results[query] = results

        print()
        print("All queries completed.")
        print("Closing browser...")

        browser.close()

    # Save results to JSON
    with open(
        "results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("Results saved to results.json")


if __name__ == "__main__":
    main()