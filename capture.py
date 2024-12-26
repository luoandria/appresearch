import json
from urllib.parse import urlparse, parse_qs

def parse_har_and_search_string(har_file, search_string):
    try:
        # Open and load the HAR file
        with open(har_file, 'r', encoding='utf-8') as file:
            har_data = json.load(file)

        # Verify the structure of HAR file
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return "Invalid HAR file structure"

        entries = har_data['log']['entries']

        # Define a list of ad-related domains to exclude
        ad_domains = [
            "doubleclick.net",
            "googleads.g.doubleclick.net",
            "googleadservices.com",
            "googlesyndication.com",
            "google-analytics.com",
            "ads.linkedin.com",
            "facebook.com",
            "twitter.com"
        ]

        # Search for the string in the entire request and response
        results = []
        for idx, entry in enumerate(entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', 'UNKNOWN')

            # Only process POST requests
            if method != 'POST':
                continue

            headers = request.get('headers', [])
            request_post_data = request.get('postData', {}).get('text', '')
            response_content = response.get('content', {}).get('text', '')
            content_type = response.get('content', {}).get('mimeType', 'UNKNOWN')

            # Parse URL to check for matches in query parameters
            parsed_url = urlparse(url)
            query = parsed_url.query
            domain = parsed_url.netloc

            # Skip requests to ad-related domains
            if any(ad_domain in domain for ad_domain in ad_domains):
                continue

            # Check for matches in the request and response
            match_sources = []
            if search_string in query:
                match_sources.append("Request Query Parameter")
            if any(search_string in header.get('name', '') or search_string in header.get('value', '') for header in headers):
                match_sources.append("Request Header")
            if search_string in request_post_data:
                match_sources.append("Request Body")
            if search_string in response_content:
                match_sources.append("Response Content")

            # Skip if no match source is identified
            if not match_sources:
                continue

            # Append matching transaction details
            status = response.get('status', None)
            started_date_time = entry.get('startedDateTime', 'UNKNOWN')
            time_taken = entry.get('time', 'UNKNOWN')

            results.append({
                "Packet Number": idx + 1,
                "URL": url,
                "Method": method,
                "Status": status,
                "Start Time": started_date_time,
                "Time Taken (ms)": time_taken,
                "Match Sources": ", ".join(match_sources),
                "Transaction Type": content_type
            })

        # Only include transactions where the search string explicitly matches
        return results if results else "No matching POST transactions found in the request, response, or query."

    except FileNotFoundError:
        return f"Error: File '{har_file}' not found."
    except json.JSONDecodeError:
        return "Error: Failed to parse HAR file. Make sure it is a valid JSON."

if __name__ == "__main__":
    # Input HAR file path and search string
    har_file = input("Enter the HAR file path: ").strip()
    har_path = "/Users/aluo/Desktop/har_files/" + har_file + ".har"
    search_string = "tell me a joke"

    # Parse the HAR file and search for the string
    results = parse_har_and_search_string(har_path, search_string)
    if isinstance(results, list):
        for result in results:
            print("Match Found:")
            for key, value in result.items():
                print(f"{key}: {value}")
            print("\n")
    else:
        print(results)
