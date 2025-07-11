import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin
import pandas as pd
from firecrawl import FirecrawlApp
import os

# It's recommended to set the API key as an environment variable
# For this example, we'll use the provided key directly, but this is not best practice
FIRECRAWL_API_KEY = "fc-536c6321e8d74768810df817ae07733a"
# Initialize FirecrawlApp
# It will automatically use the FIRECRAWL_API_KEY environment variable if set,
# otherwise you can pass it as an argument: FirecrawlApp(api_key="YOUR_API_KEY")
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
    for index, row in df.iterrows():
        url = row['url']
        if url:
            print(f"Scraping: {url}")
            detailed_info = scrape_detailed_alert_info_with_firecrawl(url)
            df.at[index, 'detailed_title'] = detailed_info['detailed_title']
            df.at[index, 'detailed_content'] = detailed_info['detailed_content']
        else:
            print(f"Skipping detailed scrape for row {index} due to missing URL.")

    return df

def process_single_html_extract(html_extract):
    """
    Processes a single HTML extract to get the title and URL,
    then scrapes the URL with Firecrawl and returns a DataFrame.
    """
    soup = BeautifulSoup(html_extract, 'html.parser')
    link_tag = soup.find('a')

    if link_tag and isinstance(link_tag, Tag):
        title = link_tag.get_text(strip=True)
        href = link_tag.get('href')
        if href and title and isinstance(href, str):
            # Assuming the href is relative to a base URL, let's use a dummy one for this example
            # In a real scenario, you'd use the actual base URL if the link is relative
            full_url = urljoin("https://www.gov.uk", href)

            data = [{
                'title': title,
                'url': full_url,
                'publish_date': None # Not available from the single extract
            }]
            df = pd.DataFrame(data)
            df['detailed_title'] = None
            df['detailed_content'] = None

            print(f"Scraping detailed page with Firecrawl for: {full_url}")
            detailed_info = scrape_detailed_alert_info_with_firecrawl(full_url)
            df.at[0, 'detailed_title'] = detailed_info['detailed_title']
            df.at[0, 'detailed_content'] = detailed_info['detailed_content']
            return df
    return pd.DataFrame()

if __name__ == "__main__":
    html_snippet = """<a data-ga4-ecommerce-path="/drug-safety-update/abrysvov-pfizer-rsv-vaccine-and-arexvyv-gsk-rsv-vaccine-be-alert-to-a-small-risk-of-guillain-barre-syndrome-following-vaccination-in-older-adults" data-ga4-ecommerce-content-id="c76264b0-cd2b-4670-8544-a5d79655f26f" data-ga4-ecommerce-row="1" data-ga4-ecommerce-index="1" class="  govuk-link gem-c-force-print-link-styles govuk-link--no-underline" href="/drug-safety-update/abrysvov-pfizer-rsv-vaccine-and-arexvyv-gsk-rsv-vaccine-be-alert-to-a-small-risk-of-guillain-barre-syndrome-following-vaccination-in-older-adults">Abrysvo▼ (Pfizer RSV vaccine) and Arexvy▼ (GSK RSV vaccine): be alert to a small risk of Guillain-Barré syndrome following vaccination in older adults</a>"""

    single_alert_df = process_single_html_extract(html_snippet)
    print(f"\n--- Processed Single HTML Extract DataFrame ({len(single_alert_df)} rows) ---")
    if not single_alert_df.empty:
        print(single_alert_df.head())
        # Save to CSV for inspection
        single_alert_df.to_csv("single_alert_extract.csv", index=False)
        print("\nSaved extracted and scraped data to single_alert_extract.csv")
    else:
        print("Failed to process the HTML extract.")
