import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin
import pandas as pd
from firecrawl import FirecrawlApp
import os
import time # Added for rate limiting
from tqdm import tqdm # Added for progress bar

# It's recommended to set the API key as an environment variable
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
# Initialize FirecrawlApp
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)


BASE_URL_DRUG_SAFETY = "https://www.gov.uk/drug-safety-update"

def scrape_detailed_alert_info_with_firecrawl(url):
    """
    Scrapes a detailed alert page using Firecrawl to get markdown content.
    """
    try:
        scraped_data = app.scrape_url(url, params={'pageOptions': {'onlyMainContent': True}})
        if scraped_data and 'markdown' in scraped_data:
            # The detailed title is usually the first line of the markdown
            lines = scraped_data['markdown'].split('\n')
            detailed_title = lines[0].strip('# ') if lines else ""
            detailed_content = scraped_data['markdown']
            return {'detailed_title': detailed_title, 'detailed_content': detailed_content}
        else:
            print(f"Firecrawl failed to return markdown for {url}")
            return {'detailed_title': None, 'detailed_content': None}
    except Exception as e:
        print(f"An error occurred while scraping with Firecrawl for {url}: {e}")
        return {'detailed_title': None, 'detailed_content': None}

def scrape_drug_safety_updates():
    """
    Scrapes the list of drug safety updates, including dates, and then each linked page for detailed info using Firecrawl.
    Returns a pandas DataFrame.
    """
    listing_data = []
    try:
        print(f"Scraping listing page with requests: {BASE_URL_DRUG_SAFETY}")
        response = requests.get(BASE_URL_DRUG_SAFETY)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        alerts = []
        for li in soup.select('ul.gem-c-document-list li'):
            link = li.find('a')
            # Find the date text directly within the list item
            # Only proceed if a link is found
            if link and isinstance(link, Tag): # Ensure link is a Tag object
                date_text = li.get_text(strip=True).replace(link.get_text(strip=True), '').strip()

                if date_text:
                    title = link.get_text(strip=True)
                    href_attr = link.get('href') # Use .get() to safely retrieve attribute
                    if href_attr and isinstance(href_attr, str): # Ensure href_attr is a string
                        full_url = urljoin(BASE_URL_DRUG_SAFETY, href_attr)

                        # Assuming the date format is consistent, you might need to adjust this
                        # if the format varies.
                        published_date = pd.to_datetime(date_text, errors='coerce')

                        alerts.append({'publish_date': published_date, 'title': title, 'url': full_url})
        listing_data = alerts

    except requests.exceptions.RequestException as e:
        print(f"Error during request for listing page {BASE_URL_DRUG_SAFETY}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred during listing scraping: {e}")
        return pd.DataFrame()

    if not listing_data:
        print("No alerts found on the listing page.")
        return pd.DataFrame()

    df = pd.DataFrame(listing_data)
    df['detailed_title'] = None
    df['detailed_content'] = None

    print(f"\nScraping detailed pages with Firecrawl for {len(df)} alerts...")
    for index, row in tqdm(df.iterrows(), total=len(df)): # Using tqdm for progress bar
        url = row['url']
        if url:
            # print(f"Scraping: {url}") # Removed to avoid excessive output with tqdm
            detailed_info = scrape_detailed_alert_info_with_firecrawl(url)
            df.at[index, 'detailed_title'] = detailed_info['detailed_title']
            df.at[index, 'detailed_content'] = detailed_info['detailed_content']
            time.sleep(10) # Added to avoid rate limits
        # else: # Removed to avoid excessive output with tqdm
            # print(f"Skipping detailed scrape for row {index} due to missing URL.")

    df.to_csv('data.csv', index=False) # Save the DataFrame to data.csv
    print("\nSaved scraped data to data.csv")

    return df

if __name__ == "__main__":
    print("Starting drug safety updates scraping...")
    df_scraped = scrape_drug_safety_updates()
    print("\n--- Scraped Drug Safety Updates DataFrame ---")
    if not df_scraped.empty:
        print(df_scraped.head())
    else:
        print("No data was scraped.")
