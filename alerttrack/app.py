import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="AlertTrack", layout="centered")
    st.title("Medical Alerts Dashboard")

    st.write("This is where the list of medical alerts will be displayed.")

    # Load the dataframe
    try:
        df = pd.read_csv("notebooks/data.csv")
        st.write("Data loaded successfully!")

        # Print a list of titles with checkboxes for details
        st.subheader("List of Titles from data.csv")
        for index, row in df.iterrows():
            st.write(f"- {row['title']}")
            if st.checkbox(f"Show details for: {row['title']}", key=f"detail_checkbox_{index}"):
                if 'detail' in row and pd.notna(row['detail']):
                    st.markdown(row['detail'])
                else:
                    st.write("No detail available for this entry.")

    except FileNotFoundError:
        st.error("Error: data.csv not found. Please ensure the file is in the 'notebooks/' directory.")
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")

    button = st.button("Scan for New Alerts")

    # Placeholder for displaying alerts
    st.subheader("Recent Alerts")
    st.write("Alerts will be loaded from the database here.")

    # Placeholder for surgery comments section
    st.subheader("Surgery Comments")
    st.write("This section will allow surgeries to add comments for selected alerts.")

if __name__ == "__main__":
    main()
