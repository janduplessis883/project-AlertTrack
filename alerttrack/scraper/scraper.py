import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    Scrapes content from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Extract all paragraph text
        paragraphs = soup.find_all('p')
        scraped_text = "\n".join([p.get_text() for p in paragraphs])

        return scraped_text

    except requests.exceptions.RequestException as e:
        return f"Error during request: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.example.com"
    content = scrape_website(test_url)
    print(f"Scraped content from {test_url}:\n{content}")
