import requests
import PyPDF2
from io import BytesIO

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """
    Downloads a PDF from a URL, extracts text from it, and returns the text.
    """
    try:
        # Download the PDF content
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Read the content into a BytesIO object
        pdf_file = BytesIO(response.content)

        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from each page
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        return text

    except requests.exceptions.RequestException as e:
        return f"Error downloading the PDF: {e}"
    except Exception as e:
        return f"An error occurred during PDF processing: {e}"

if __name__ == "__main__":
    # Example usage with the provided URL
    example_pdf_url = "https://assets.publishing.service.gov.uk/media/686bb9d3fe1a249e937cbd64/DSU_RSV_vaccine_-_final.pdf"
    extracted_text = extract_text_from_pdf_url(example_pdf_url)

    print("Extracted Text:\n")
    print(extracted_text)
