import json
import csv
from urllib.parse import urlparse


# =========================
# File names
# =========================

SEARCH_ENGINE_FILE = "results.json"
GOOGLE_FILE = "Google_Result4.json"
OUTPUT_FILE = "hw1.csv"


# =========================
# URL normalization
# =========================

def normalize_url(url):
    """
    Normalize URLs according to the assignment FAQ.

    1. http and https are treated as the same
    2. www.example.com and example.com are treated as the same
    3. Remove trailing /
    4. Do NOT convert URLs to lowercase
    """

    url = url.strip()

    parsed = urlparse(url)

    hostname = parsed.hostname

    if hostname is None:
        return url.rstrip("/")

    # Remove www. from hostname
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Reconstruct URL without scheme
    normalized = hostname

    if parsed.port is not None:
        normalized += ":" + str(parsed.port)

    if parsed.path:
        normalized += parsed.path

    if parsed.params:
        normalized += ";" + parsed.params

    if parsed.query:
        normalized += "?" + parsed.query

    # Remove trailing slash
    normalized = normalized.rstrip("/")

    return normalized


# =========================
# Calculate Spearman rho
# =========================

def calculate_spearman(matches):
    """
    matches:
        list of tuples: (google_rank, search_engine_rank)

    Special cases from the FAQ:
        n = 0 -> rho = 0
        n = 1 -> same rank -> 1, different rank -> 0
        n >= 2 -> modified Spearman formula
    """

    n = len(matches)

    if n == 0:
        return 0

    if n == 1:
        google_rank, search_rank = matches[0]
        if google_rank == search_rank:
            return 1
        return 0

    sum_d_squared = 0

    for google_rank, search_rank in matches:
        d = google_rank - search_rank
        sum_d_squared += d * d

    rho = 1 - (6 * sum_d_squared / (n * (n * n - 1)))

    return rho


# =========================
# Find matching URLs
# =========================

def find_matches(google_results, search_results):
    """
    Returns list of (google_rank, search_engine_rank)
    """

    google_normalized = {}

    for rank, url in enumerate(google_results, start=1):
        normalized = normalize_url(url)
        google_normalized[normalized] = rank

    matches = []

    for search_rank, url in enumerate(search_results, start=1):
        normalized = normalize_url(url)
        if normalized in google_normalized:
            google_rank = google_normalized[normalized]
            matches.append((google_rank, search_rank))

    return matches


# =========================
# Main
# =========================

def main():

    # -------------------------
    # Read Task 1 results
    # -------------------------

    with open(SEARCH_ENGINE_FILE, "r", encoding="utf-8") as file:
        search_engine_data = json.load(file)

    # -------------------------
    # Read Google reference data
    # -------------------------

    with open(GOOGLE_FILE, "r", encoding="utf-8") as file:
        google_data = json.load(file)

    print("Search engine queries:", len(search_engine_data))
    print("Google queries:", len(google_data))
    print()
    print("Starting Task 2...")
    print()

    # -------------------------
    # Store CSV rows and stats
    # -------------------------

    rows = []
    all_percent_overlap = []
    all_spearman = []

    # Initialize averages to avoid UnboundLocalError
    average_percent_overlap = 0
    average_spearman = 0

    # -------------------------
    # Process every query
    # -------------------------

    for query_number, query in enumerate(search_engine_data.keys(), start=1):

        print("=" * 70)
        print("Query", query_number)
        print(query)
        print("=" * 70)

        search_results = search_engine_data[query]

        if query not in google_data:
            print("WARNING: Query not found in Google dataset.")
            print()
            continue

        google_results = google_data[query]

        # Find overlapping URLs
        matches = find_matches(google_results, search_results)
        number_of_matches = len(matches)

        # Percent overlap (Google always has 10)
        percent_overlap = (number_of_matches / 10) * 100

        # Spearman coefficient
        rho = calculate_spearman(matches)

        all_percent_overlap.append(percent_overlap)
        all_spearman.append(rho)

        # Print info
        print("Google results:", len(google_results))
        print("Search engine results:", len(search_results))
        print("Number of matches:", number_of_matches)
        print("Percent overlap:", percent_overlap)
        print("Matching ranks:", matches)
        print("Spearman coefficient:", rho)
        print()

        # Add row to CSV
        rows.append([
            "Query " + str(query_number),
            number_of_matches,
            percent_overlap,
            rho
        ])

    # =========================
    # Calculate averages
    # =========================

    if len(all_percent_overlap) > 0:
        average_percent_overlap = sum(all_percent_overlap) / len(all_percent_overlap)
        average_spearman = sum(all_spearman) / len(all_spearman)

    # =========================
    # Add average row
    # =========================

    rows.append([
        "Averages",
        "",
        average_percent_overlap,
        average_spearman
    ])

    # =========================
    # Write CSV
    # =========================

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Queries",
            "Number of Overlapping Results",
            "Percent Overlap",
            "Spearman Coefficient"
        ])

        writer.writerows(rows)

    # =========================
    # Final output
    # =========================

    print("=" * 70)
    print("TASK 2 COMPLETED")
    print("=" * 70)
    print()
    print("Average percent overlap:", average_percent_overlap)
    print("Average Spearman coefficient:", average_spearman)
    print()
    print("CSV saved as:", OUTPUT_FILE)


if __name__ == "__main__":
    main()