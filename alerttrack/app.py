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
                    "content": f"Summarize the following text concisely: {text}",
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error summarizing: {e}"

def main():
    st.set_page_config(page_title="AlertTrack", layout="centered")
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
        df = pd.read_csv("data/data.csv")
        st.write("Data loaded successfully!")

        # Display alerts with expanders
        for index, row in df.iterrows():
            published_date = pd.to_datetime(row['publish_date']).strftime('%d-%m-%Y')
            with st.expander(f"**{published_date}** - :material/pill: {row['title']})"):
                st.write(row['detail'])
                col1, col2 = st.columns(2)
                with col1:
                    if 'detail' in row and pd.notna(row['detail']):
                        if st.button("AI Summary", key=f"summary_{index}"):
                            st.write("Generating summary...")
                            summary = summarize_text(row['detail'])
                            st.markdown(summary)
                    else:
                        st.write("No detail available for summary.")
                with col2:
                    if 'detail' in row and pd.notna(row['detail']):
                        st.write("Full Text: ", row['detail'])
                    else:
                        st.write("No full text available.")
    except FileNotFoundError:
        st.error("Error: data.csv not found. Please ensure the file is in the 'notebooks/' directory.")
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")

if __name__ == "__main__":
    main()
