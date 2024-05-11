import requests
from bs4 import BeautifulSoup
import argparse
import os
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json

def fetch_url(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        file_size = len(response.content)

        # Check if the URL points to a sensitive file
        if wordlist:
            for sensitive_file in wordlist:
                if url.endswith(sensitive_file):
                    print(f"\033[91mVulnerable URL: {url} - Status Code: {status_code} - File Size: {file_size} bytes\033[0m")
                    return
        print(f"\033[92mURL: {url} - Status Code: {status_code} - File Size: {file_size} bytes\033[0m")
    except Exception as e:
        print(f"Error accessing URL: {url} - {e}")

def get_wayback_urls(domain):
    try:
        archive_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey"
        response = requests.get(archive_url)
        if response.status_code == 200:
            data = json.loads(response.text)
            urls = set([url[2] for url in data[1:]])
            return urls
        else:
            print(f"Failed to fetch Wayback Machine archive for {domain}. Status code: {response.status_code}")
            return set()
    except Exception as e:
        print(f"Error fetching Wayback Machine archive for {domain}: {e}")
        return set()

def main():
    global wordlist

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="URL Fetcher Tool")
    parser.add_argument("target_domain", nargs='?', help="Target domain to fetch URLs from Wayback Machine")
    parser.add_argument("-w", "--wordlist", default="wordlist.txt", help="Path to the wordlist file")
    args = parser.parse_args()

    if args.wordlist:
        with open(args.wordlist, 'r') as file:
            wordlist = [line.strip() for line in file]
    else:
        wordlist = []

    if args.target_domain:
        domains = [args.target_domain]
    else:
        print("Please provide a target domain.")
        return

    # Fetch URLs from Wayback Machine
    urls = set()
    with ThreadPoolExecutor() as executor:
        fetch_wayback_partial = partial(get_wayback_urls)
        results = executor.map(fetch_wayback_partial, domains)
        for result in results:
            urls.update(result)

    # Fetch URLs concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(fetch_url, urls)

if __name__ == "__main__":
    main()

