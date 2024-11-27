import sqlite3
import re
import requests
from googletrans import Translator
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from ..utils.transaction_data_utils import *
import os

# set base variables
cx = os.getenv("GOOGLE_CUSTOMISED_SEARCH_ENGINE_ID") # customised search engine ID 
api_key = os.getenv('GOOGLE_SEARCH_API_KEY') # Google API key
db_path = proj_path / 'input_files' / 'companies.db'

if api_key is None:
    raise KeyError("Please set the GOOGLE_SEARCH_API_KEY environment variable. Use:conda env config vars set GOOGLE_SEARCH_API_KEY=...")

if cx is None:
    raise KeyError("Please set the GOOGLE_CUSTOMISED_SEARCH_ENGINE_ID environment variable. Use:conda env config vars set GOOGLE_CUSTOMISED_SEARCH_ENGINE_ID=...")

# retrieve sample transaction data with details
atd = AugmentTransactionData(proj_path=proj_path)
transaction_with_details = atd.get_transaction_details(remove_sensitive_data=True)


# Function to initialize the database and create the table
def initialize_db(db_path=db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            summary TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert or update company names and summaries in the table
def insert_or_update_company(db_path, company_name, summary):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO companies (name, summary) VALUES (?, ?)
    ''', (company_name, summary))
    conn.commit()
    conn.close()

# Function to check if a company name exists in the table and retrieve its summary
def get_company_summary(db_path, company_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT summary FROM companies WHERE name = ?
    ''', (company_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to look up entity online and store in the database
def lookup_and_store_company_summary(transactions_with_details: pd.DataFrame=transaction_with_details, api_key: str=api_key, cx: str=cx):
    """
    Lookup entity/companies online using Google Custom Search API and store their summaries in the database
    """

    # retrieve companies and locations from transactions
    companies = transactions_with_details['company']
    locations = transactions_with_details['location']

    # Base URL for Google Custom Search API
    url = "https://www.googleapis.com/customsearch/v1"

    n_samples = 5
    for company, location in tqdm(zip(companies[:n_samples], locations[:n_samples]), total=len(companies[:n_samples]), desc='Fetching company summaries'):
        
        # Check if the company already exists in the database
        summary = get_company_summary(db_path, company)
        if summary:
            continue

        if company == 'misc.':
            # if company is not known, use miscellaneous entity
            summary = 'miscellaneous entity, could not use API to gather info.'
        else:
            if location == 'unknown':    
                # query parameter same as company
                query = company
            else:
                # if location is known, add it to the query
                query = company + ' ' + location

            # Remove all numeric string characters from the query
            query = re.sub(r'\d+', '', query)

            # Parameters for the API request
            params = {
                'q': query,       # Search query
                'key': api_key,   # API key
                'cx': cx          # Custom Search Engine ID
            }

            # Make the API request
            response = requests.get(url, params=params)
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # take the first response of the search
                items = data.get('items', [])                                 
            else:
                print(f"Error: {response.status_code} - {response.text}")
                items = []

            # if no items are found, use miscellaneous entity
            if not items:
                summary = 'miscellaneous entity, could not use API to gather info.'
            else:
                # translate summary to English 
                first_result = items[0]['snippet']
                translator = Translator()
                translated_summary = translator.translate(first_result, dest='en')
                summary = translated_summary.text

        # Insert or update company and summary in the database
        insert_or_update_company(db_path, company, summary)

    # Function to print the contents of the database
def print_database_contents(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies')
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        print(row)


if __name__ == "__main__":

    # Initialize the database
    initialize_db(db_path)

    # Look up entity online and store in the database
    lookup_and_store_company_summary()

    print("Completed collecting company summaries. Printing first 5 rows...")

    # check sql data base output
    print_database_contents(db_path)
    
