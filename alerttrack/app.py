import streamlit as st
import pandas as pd
from groq import Groq
import os

@st.cache_resource
def summarize_text(text):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following text for a clinical pharmacist, highlight key actions to be taken: {text}",
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error summarizing: {e}"

def main():
    st.set_page_config(page_title="AlertTrack", layout="wide")
    st.title("Medical Alerts Dashboard")

    # Configure GROQ API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY environment variable not set. Please set it to use the summarization feature.")
        return

    st.sidebar.title("Navigation")
    button = st.sidebar.button("Scan for New Alerts")

    # Load the dataframe
    try:
        df = pd.read_csv("data.csv")
        st.write("Data loaded successfully!")

        # Define the columns to display
        columns_to_display = [col for col in df.columns if col != 'alert_pdf']

        # Display the dataframe
        st.dataframe(df[columns_to_display])

        for index, row in df.iterrows():
            st.subheader(f"Alert {index + 1}: {row['title']}")
            st.write(f"**Publish Date:** {row['publish_date']}")
            with st.popover("Alert Details"):
                st.markdown((f"[Alert URL]({row['url']})"))
                st.write(f"**URL:** {row['url']}")
                st.write(f"**Details:** {row.get('detail', 'No details available.')}")
                if 'pdf_text' in row:
                    st.write(f"**PDF Text:** {row['pdf_text']}")
                if 'pdf' in row:
                    st.markdown(f"[PDF URL]({row['pdf']})")
            with st.popover("PDF Download"):
                st.html(f"<embed src={row['pdf']} type='application/pdf'>")
                st.html("<object data={row['pdf']} type='application/pdf' width='100%'> </object>")


            with st.status('Summary with AI',expanded=True):
                text = row['detail'] if 'detail' in row else "No details available." + row['pdf_text'] if 'pdf_text' in row else "No PDF text available."
                st.write('Text for Alert and PDF loaded')
                if st.button(f"Summarize Alert {index + 1}"):

                    summary = summarize_text(text)
                    st.markdown("**AI Summary:**")
                    st.markdown(summary)

    except FileNotFoundError:
        st.error("Error: data.csv not found. Please ensure the file is in the 'data/' directory.")
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")

if __name__ == "__main__":
    main()
