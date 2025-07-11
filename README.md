![AlertTrack](images/pills.png)

# AlertTrack Project Plan

This document outlines the plan for developing the AlertTrack application, which involves scraping UK medical alert websites, storing data in Supabase, managing surgery comments via a Streamlit app, and sending Telegram notifications for new alerts.

## Project Structure

The project will maintain the current structure and add new modules:

```
project-AlertTrack/
├── alerttrack/
│   ├── __init__.py
│   ├── app.py          # Streamlit app for surgery comments
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── scraper.py  # Web scraping logic
│   ├── database.py     # Supabase interaction logic
│   ├── notifications.py # Telegram notification logic
│   └── models.py       # Data models (e.g., Alert class)
├── main.py             # Main script for automated scraping and processing
├── requirements.txt    # Project dependencies
├── setup.py            # Package setup
├── Makefile            # (Existing)
└── PLAN.md             # This plan document
```

## Components and Implementation Steps

1.  **`alerttrack/scraper/scraper.py`:**
    *   Implement specific scraping functions for:
        *   `https://www.gov.uk/drug-device-alerts`
        *   `https://www.gov.uk/drug-safety-update`
        *   `https://www.cas.mhra.gov.uk/home.aspx`
    *   Functions will scrape listing pages for basic info and links, then scrape detailed pages for comprehensive data (description, drug, alert ID, agencies affected, info for patients/healthcare professionals, etc.).
    *   Scraped data will be structured (e.g., list of dictionaries).

2.  **`alerttrack/models.py`:**
    *   Define a Python class (e.g., `Alert`) to represent a medical alert object, holding the structured scraped data.

3.  **`alerttrack/database.py`:**
    *   Handle Supabase interactions.
    *   Functions for:
        *   Connecting to Supabase (using environment variables).
        *   Checking for existing alerts in the main table.
        *   Inserting new, unique alerts into the main table.
        *   Inserting surgery comments (Surgery Name, Surgery ID, Alert ID, Number of Patients Affected, Action Taken) into a separate table, linked by Alert ID.
        *   Retrieving alerts and comments for the Streamlit app.

4.  **`alerttrack/notifications.py`:**
    *   Implement a function to send Telegram notifications using the Telegram Bot API.
    *   Format messages for new alerts, including a link to the specific alert in the Streamlit app.
    *   Use environment variables for Telegram Bot Token and Chat ID(s).

5.  **`main.py`:**
    *   Entry point for the automated process (to be run via cron/Github Actions).
    *   Orchestrate the workflow:
        *   Call scraping functions.
        *   Process scraped data (deduplication, check against database).
        *   Insert new alerts into Supabase.
        *   Send Telegram notifications for new alerts.

6.  **`alerttrack/app.py` (Streamlit App):**
    *   Enhance the existing app.
    *   Display medical alerts fetched from Supabase.
    *   Allow users (surgeries) to input and save comments (Number of Patients Affected, Action Taken) to the surgery comments table in Supabase.
    *   Display existing comments.

7.  **Dependencies (`requirements.txt`):**
    *   Add necessary libraries: `requests` or `beautifulsoup4` (or `scrapy`), `supabase-py`, `streamlit`, `python-telegram-bot`.

8.  **Configuration:**
    *   Define environment variables for Supabase URL, Supabase Key, Telegram Bot Token, Telegram Chat ID(s).

## Automated Workflow (Cron/Github Actions)

1.  Cron job or Github Action triggers `main.py`.
2.  `main.py` executes scraping.
3.  Scraped data is processed and new alerts are identified.
4.  New alerts are inserted into Supabase.
5.  Telegram notifications are sent for new alerts.
