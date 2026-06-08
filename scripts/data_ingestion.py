import os
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def fetch_live_nav(scheme_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"[INGESTION] Pinging API for {scheme_name} (Code: {scheme_code})...")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            json_data = response.json()
            if 'data' in json_data:
                df = pd.DataFrame(json_data['data'])
                df['amfi_code'] = scheme_code
                
                # Save structured raw tracking dump
                output_file = os.path.join(RAW_DATA_DIR, f"raw_nav_{scheme_code}.csv")
                df.to_csv(output_file, index=False)
                print(f"[SUCCESS] Saved raw data dump to {output_file}")
            else:
                print(f"[ERROR] No data payload available for scheme: {scheme_code}")
        else:
            print(f"[ERROR] API endpoint hit failed with status code: {response.status_code}")
    except Exception as e:
        print(f"[CRITICAL] Operational failure during API runtime: {str(e)}")

if __name__ == "__main__":
    print("Initiating Ingestion Pipeline Framework...")
    target_schemes = {
        "125497": "HDFC Top 100",
        "119551": "SBI Bluechip",
        "120503": "ICICI Bluechip",
        "118632": "Nippon Large Cap",
        "119092": "Axis Bluechip",
        "120841": "Kotak Bluechip"
    }
    for code, name in target_schemes.items():
        fetch_live_nav(code, name)
        
    print("\n Day 1 Data Ingestion Automation complete. Target files active in data/raw/")