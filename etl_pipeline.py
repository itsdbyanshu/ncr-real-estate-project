import os
import time
import random
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Database drivers
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from sqlalchemy import create_engine

# Load credentials from .env
load_dotenv()

# The script will navigate through each city sequentially
NCR_CITIES = ["Noida", "New-Delhi", "Gurgaon", "Ghaziabad", "Faridabad"]

def clean_price(price_str):
    """Converts Indian real estate pricing formats (₹75,000 or 1.4 Lac) to clean integers."""
    try:
        val = price_str.lower().replace('₹', '').replace(',', '').strip()
        if 'lac' in val:
            return int(float(val.replace('lac', '').strip()) * 100000)
        return int(val)
    except Exception:
        return None

def extract_sqft(listing):
    """Iterates through summary tags to find the one actually containing square footage."""
    summaries = listing.find_all('div', class_='mb-srp__card__summary--value')
    for summary in summaries:
        text = summary.text.strip().lower()
        if 'sqft' in text or 'sqm' in text or text.replace(',', '').isdigit():
            nums = ''.join(filter(str.isdigit, text))
            return int(nums) if nums else None
    return None

def main():
    print("Starting NCR-Wide Full Load ETL Pipeline...")
    all_properties = []
    
    # ==========================================
    # 1. EXTRACT (Daily Updates: Page <= 5)
    # ==========================================
    for city in NCR_CITIES:
        print(f"\n=== Fetching Data for {city} ===")
        clean_city = city.replace('-', ' ').title()
        
        page = 1
        while page <= 5:
            print(f"Scraping {city} - Page {page}...")
            url = f"https://www.magicbricks.com/property-for-rent/residential-real-estate?bedroom=1,2,3&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Service-Apartment,Residential-House,Villa&cityName={city}&page={page}"
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed on {city} page {page}. Status: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('div', class_='mb-srp__card')
            
            # AUTO-STOP: Break the while loop if the page returns 0 property cards
            if len(listings) == 0:
                print(f"No more listings found for {city}. Moving to the next city...")
                break
            
            for listing in listings:
                # Core Text Fields
                title_elem = listing.find('h2')
                title = title_elem.text.strip() if title_elem else "N/A"
                
                price_elem = listing.find('div', class_='mb-srp__card__price--amount')
                raw_price = price_elem.text.strip() if price_elem else "0"
                
                # URL Extraction
                url_elem = listing.find('a', href=True)
                property_url = url_elem['href'] if url_elem else "No URL found"
                if property_url.startswith('/'):
                    property_url = "https://www.magicbricks.com" + property_url
                
                # Categorical Extraction
                type_keywords = ['Apartment', 'Builder Floor', 'Villa', 'Independent House', 'Penthouse', 'Studio']
                property_type = next((t for t in type_keywords if t.lower() in title.lower()), 'Other')
                
                furnishing_keywords = ['Fully Furnished', 'Semi-Furnished', 'Unfurnished']
                furnishing_status = next((f for f in furnishing_keywords if f.lower() in listing.text.lower()), 'Unspecified')
                
                all_properties.append({
                    "TITLE": title,
                    "RENT_PRICE": clean_price(raw_price),
                    "SQFT": extract_sqft(listing),
                    "BHK": int(title.split(' ')[0]) if title and title[0].isdigit() else None,
                    "SECTOR": title.split(' in ')[-1] if title and ' in ' in title else None,
                    "CITY": clean_city,
                    "PROPERTY_URL": property_url,
                    "PROPERTY_TYPE": property_type,
                    "FURNISHING_STATUS": furnishing_status,
                    "SCRAPED_AT": datetime.now()
                })
                
            # Random delay to mimic human browsing
            time.sleep(random.uniform(2, 5))
            page += 1 
            
    # ==========================================
    # 2. TRANSFORM
    # ==========================================
    df = pd.DataFrame(all_properties)
    
    # Drop rows missing essential pricing or BHK data
    df = df.dropna(subset=['RENT_PRICE', 'BHK'])
    
    # 1. Impute realistic square footage based on BHK standard sizing (Overrides bad scraped data)
    conditions = [
        df['BHK'] == 1,
        df['BHK'] == 2,
        df['BHK'] == 3,
        df['BHK'] == 4
    ]
    choices = [650, 1150, 1650, 2400]
    
    # Apply conditions, using (BHK * 600) as the fallback for 5+ BHKs
    df['SQFT'] = np.select(conditions, choices, default=df['BHK'] * 600)
    
    # 2. Recalculate clean price_per_sqft
    df = df[df['SQFT'] > 0] # Prevent division by zero
    df['PRICE_PER_SQFT'] = (df['RENT_PRICE'] / df['SQFT']).round(2)
    
    print(f"\nExtracted, cleaned, and transformed {len(df)} properties across NCR.")
    
    # ==========================================
    # 3. LOAD TO SNOWFLAKE
    # ==========================================
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        df.columns = [c.upper() for c in df.columns] 
        write_pandas(conn, df, 'RENTAL_LISTINGS', auto_create_table=False, overwrite=False)
        print("✅ Successfully appended data to Snowflake!")
        conn.close()
    except Exception as e:
        print(f"❌ Snowflake Error: {e}")
        
    # ==========================================
    # 4. LOAD TO NEON (POSTGRESQL)
    # ==========================================
    try:
        neon_url = os.getenv("NEON_DB_URL").replace("postgres://", "postgresql://")
        engine = create_engine(neon_url)
        df.columns = [c.lower() for c in df.columns]
        df.to_sql('rental_listings', engine, if_exists='append', index=False)
        print("✅ Successfully appended data to Neon!")
    except Exception as e:
        print(f"❌ Neon Error: {e}")

if __name__ == "__main__":
    main()