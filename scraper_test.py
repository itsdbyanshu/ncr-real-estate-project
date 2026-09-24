import requests
from bs4 import BeautifulSoup
import pandas as pd

# Your exact MagicBricks URL for Noida rentals
TARGET_URL = "https://www.magicbricks.com/property-for-rent/residential-real-estate?bedroom=1,2,3&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Service-Apartment,Residential-House,Villa&cityName=Noida"

# Headers mimic a real browser to prevent the site from blocking us
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

def test_scrape():
    print("Fetching data from MagicBricks...")
    response = requests.get(TARGET_URL, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    # Parse the raw HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # MagicBricks commonly wraps each property in a div with the class 'mb-srp__list' or 'mb-srp__card'
    listings = soup.find_all('div', class_='mb-srp__card')
    if not listings:
        listings = soup.find_all('div', class_='mb-srp__list')

    print(f"Successfully found {len(listings)} property listings on this page.\n")
    
    scraped_data = []

    # Loop through each listing block and extract the text
    for listing in listings:
        try:
            # Extract Title (usually contains BHK and Sector)
            title_elem = listing.find('h2')
            title = title_elem.text.strip() if title_elem else "N/A"
            
            # Extract Rent Price 
            price_elem = listing.find('div', class_='mb-srp__card__price--amount')
            rent_price = price_elem.text.strip() if price_elem else "N/A"
            
            # Extract Square Footage 
            sqft_elem = listing.find('div', class_='mb-srp__card__summary--value')
            sqft = sqft_elem.text.strip() if sqft_elem else "N/A"

            scraped_data.append({
                "Title": title,
                "Rent Price": rent_price,
                "SqFt": sqft
            })
        except Exception as e:
            print(f"Error extracting a listing: {e}")

    # Display the extracted data cleanly
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        print(df.head(10))
    else:
        print("No data extracted. The HTML class names might have changed.")

if __name__ == "__main__":
    test_scrape()