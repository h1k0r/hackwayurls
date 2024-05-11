import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    urls = []
    for link in soup.find_all('a', href=True):
        urls.append(link['href'])
    return urls

def is_internal_ip(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['localhost', '127.0.0.1']:
        return True
    if parsed_url.hostname.startswith('192.168.') or parsed_url.hostname.startswith('10.') or parsed_url.hostname.startswith('172.16.'):
        return True
    return False

def check_for_ssrf(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"URL: {url} - Status: {response.status_code}")
            if is_internal_ip(response.url):
                print("Potential SSRF vulnerability detected: Internal IP address accessed")
            # Additional SSRF vulnerability detection logic can be added here
        else:
            print(f"URL: {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing URL: {url} - {e}")

def main():
    parser = argparse.ArgumentParser(description="SSRF Bug Finder Tool")
    parser.add_argument("target_url", help="URL to scan for SSRF vulnerabilities")
    args = parser.parse_args()

    try:
        response = requests.get(args.target_url, timeout=5)
        if response.status_code == 200:
            urls = extract_urls(response.text)
            for url in urls:
                check_for_ssrf(url)
        else:
            print(f"Failed to fetch target URL: {args.target_url} - Status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing target URL: {args.target_url} - {e}")

if __name__ == "__main__":
    main()
