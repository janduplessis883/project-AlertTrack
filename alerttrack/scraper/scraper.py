import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin
import pandas as pd
from firecrawl import FirecrawlApp, JsonConfig
from pydantic import BaseModel, Field
from typing import Optional
import os
from tqdm import tqdm
import time

# It's recommended to set the API key as an environment variable
# For this example, we'll use the provided key directly, but this is not best practice
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
# Initialize FirecrawlApp
# It will automatically use the FIRECRAWL_API_KEY environment variable if set,
# otherwise you can pass it as an argument: FirecrawlApp(api_key="YOUR_API_KEY")
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

BASE_URL_DRUG_SAFETY = "https://www.gov.uk/drug-safety-update"

def scrape_drug_safety_updates():
    """
    Scrapes the list of drug safety updates, including dates, and then each linked page for detailed info using Firecrawl.
    Returns a pandas DataFrame.
    """
    listing_data = []

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
            title = link.get_text(strip=True)
            href_attr = link.get('href')
            full_url = None
            if href_attr and isinstance(href_attr, str): # Ensure href_attr is a string
                full_url = urljoin(BASE_URL_DRUG_SAFETY, href_attr)

            # Find the time tag within the current list item
            time_tag = li.find('time')
            published_date = None
            if time_tag and isinstance(time_tag, Tag) and time_tag.get('datetime'):
                date_str = time_tag.get('datetime')
                if isinstance(date_str, str): # Ensure date_str is a string
                    published_date = pd.to_datetime(date_str, errors='coerce')

            if published_date is not None and full_url is not None:
                alerts.append({'publish_date': published_date, 'title': title, 'url': full_url})
    listing_data = alerts

    print(listing_data)
    df = pd.DataFrame(listing_data)
    return df

class AlertExtractSchema(BaseModel):
    document_download_url: Optional[str] = Field(
        None,
        description="The full URL for the 'Download Document' link on the page. It should end with .pdf"
    )

def scrape_pdf_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scrapes each URL in the DataFrame to extract the 'Document Download' URL using Firecrawl's LLM extraction.
    """
    print("Extracting PDF URLs for each alert using Firecrawl...")
    pdf_urls = []

    json_config = JsonConfig(
        schema=AlertExtractSchema,
        prompt="Extract the URL for the 'Download Document' link from the page content."
    )

    global app
    if 'app' not in globals() or app is None:
        app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

    for index, row in tqdm(df.iterrows(), total=len(df)):
        url = row['url']
        try:
            llm_extraction_result = app.scrape_url(
                url,
                formats=["json"],
                json_options=json_config,
                only_main_content=False, # Search the whole page
                timeout=120000
            )
            pdf_url = llm_extraction_result.json.get('document_download_url') if llm_extraction_result.json else None
            pdf_urls.append(pdf_url)
        except Exception as e:
            print(f"Error extracting from {url}: {e}")
            pdf_urls.append(None)
        time.sleep(2) # Add a small delay to be mindful of rate limits

    df['alert_pdf'] = pdf_urls
    return df


if __name__ == "__main__":
    # Scrape the drug safety updates and create the initial DataFrame
    df = scrape_drug_safety_updates()

    # Extract PDF URLs for each alert
    df = scrape_pdf_urls(df)

    # Save the resulting DataFrame to CSV
    output_path = "data/data.csv"

    # We don't need the 'detail' column anymore, so let's select the ones we want
    columns_to_save = ['publish_date', 'title', 'url', 'alert_pdf']
    df_to_save = df[columns_to_save]

    df_to_save.to_csv(output_path, index=False)

    print(f"DataFrame saved to {output_path}")
    print(df.head())
