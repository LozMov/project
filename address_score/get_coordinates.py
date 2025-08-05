import pandas as pd
import requests
import time
import json
import os
from dotenv import load_dotenv
from typing import Tuple, Optional


def geocode_address(address: str, api_key: str, region: str = "CA") -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an address using Google Maps Geocoding API.

    Args:
        address (str): The address to geocode
        api_key (str): Google Maps API key
        region (str): Region code for biasing results (default: "CA" for Canada)

    Returns:
        Tuple[Optional[float], Optional[float]]: (latitude, longitude) or (None, None) if failed
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"

    # Add Vancouver, BC to the address for better accuracy
    full_address = f"{address}, Vancouver, BC, Canada"

    params = {
        'address': full_address,
        'key': api_key,
        'region': region
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        if data['status'] == 'OK' and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(
                f"Geocoding failed for address: {address} - Status: {data['status']}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Request failed for address: {address} - Error: {e}")
        return None, None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing response for address: {address} - Error: {e}")
        return None, None


def geocode_vancouver_houses(input_file: str, output_file: str, api_key: str, delay: float = 0.1):
    """
    Read Vancouver house data, geocode addresses, and save results.

    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        api_key (str): Google Maps API key
        delay (float): Delay between requests in seconds (default: 0.1)
    """
    print(f"Reading data from {input_file}...")

    # Read the CSV file
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"Successfully loaded {len(df)} records")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Check if required columns exist
    if 'Address' not in df.columns:
        print("Error: 'Address' column not found in the CSV file")
        return

    # Initialize new columns for coordinates
    df['Latitude'] = None
    df['Longitude'] = None

    # Counter for progress tracking
    total_addresses = len(df)
    geocoded_count = 0
    failed_count = 0

    print(f"Starting geocoding process for {total_addresses} addresses...")
    print("This may take a while due to API rate limiting...")

    # Process each address
    for index, row in df.iterrows():
        address = row['Address']

        if pd.isna(address) or address == '':
            print(f"Row {index + 1}: Skipping empty address")
            failed_count += 1
            continue

        print(f"Processing {index + 1}/{total_addresses}: {address}")

        # Geocode the address
        lat, lng = geocode_address(address, api_key)

        # Update the dataframe
        df.at[index, 'Latitude'] = lat
        df.at[index, 'Longitude'] = lng

        if lat is not None and lng is not None:
            geocoded_count += 1
            print(f"  ✓ Success: ({lat:.6f}, {lng:.6f})")
        else:
            failed_count += 1
            print(f"  ✗ Failed to geocode")

        # Add delay to respect rate limits
        time.sleep(delay)

        # Progress update every 50 addresses
        if (index + 1) % 50 == 0:
            success_rate = (geocoded_count / (index + 1)) * 100
            print(
                f"\nProgress: {index + 1}/{total_addresses} ({success_rate:.1f}% success rate)")
            print("-" * 50)

    # Final statistics
    print(f"\nGeocoding completed!")
    print(f"Total addresses: {total_addresses}")
    print(f"Successfully geocoded: {geocoded_count}")
    print(f"Failed to geocode: {failed_count}")
    print(f"Success rate: {(geocoded_count/total_addresses)*100:.1f}%")

    # Save the results
    print(f"\nSaving results to {output_file}...")
    try:
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✓ Results saved successfully to {output_file}")

        # Show sample of results
        print("\nSample of geocoded data:")
        sample_df = df[['Address', 'Latitude', 'Longitude']].head(3)
        print(sample_df.to_string(index=False))

    except Exception as e:
        print(f"Error saving CSV file: {e}")


def main():
    """
    Main function to run the geocoding process.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Configuration
    INPUT_FILE = "House sale data Vancouver.csv"
    OUTPUT_FILE = "House_with_coords.csv"

    # Get API key from environment variable
    API_KEY = os.getenv('GOOGLE_API_KEY')

    # Delay between requests (seconds) - adjust as needed
    DELAY = 0.1  # 100ms delay = max 10 requests per second

    # Validate API key
    if not API_KEY:
        print("ERROR: Google Maps API key not found!")
        print("Please make sure you have a .env file with GOOGLE_API_KEY=your_api_key_here")
        print("You can get an API key from: https://developers.google.com/maps/documentation/geocoding/get-api-key")
        return

    print(f"✓ API key loaded from .env file")

    # Run the geocoding process
    geocode_vancouver_houses(INPUT_FILE, OUTPUT_FILE, API_KEY, DELAY)


if __name__ == "__main__":
    main()
