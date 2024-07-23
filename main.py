import streamlit as st
import requests
import sqlite3
import pandas as pd


# Function to create database
def create_database():
    conn = sqlite3.connect('cat_facts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS facts
                 (id TEXT PRIMARY KEY, text TEXT, created_at TEXT, 
                  updated_at TEXT, verified BOOLEAN, sent_count INTEGER)''')
    conn.commit()
    return conn


# Function to fetch cat facts
def fetch_cat_facts():
    response = requests.get('https://cat-fact.herokuapp.com/facts')
    return response.json()


# Function to save facts to database
def save_facts_to_db(conn, facts):
    c = conn.cursor()
    for fact in facts:
        c.execute('''INSERT OR REPLACE INTO facts 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (fact['_id'],
                   fact['text'],
                   fact['createdAt'],
                   fact['updatedAt'],
                   fact['status']['verified'],
                   fact['status']['sentCount']))
    conn.commit()


# Function to get facts from database
def get_facts_from_db(conn):
    return pd.read_sql_query("SELECT * FROM facts", conn)


# Streamlit app
def main():
    st.title('Cat Facts App')

    # Create database connection
    conn = create_database()

    # Sidebar
    st.sidebar.header('Actions')
    if st.sidebar.button('Fetch New Facts'):
        with st.spinner('Fetching new facts...'):
            facts = fetch_cat_facts()
            save_facts_to_db(conn, facts)
        st.success('New facts fetched and saved!')

    # Main content
    st.header('Stored Cat Facts')
    df = get_facts_from_db(conn)

    # Display facts
    for index, row in df.iterrows():
        with st.expander(f"Fact {index + 1}"):
            st.write(f"**Fact:** {row['text']}")
            st.write(f"**Created at:** {row['created_at']}")
            st.write(f"**Updated at:** {row['updated_at']}")
            st.write(f"**Verified:** {'Yes' if row['verified'] else 'No'}")
            st.write(f"**Sent count:** {row['sent_count']}")

    conn.close()


if __name__ == "__main__":
    main()