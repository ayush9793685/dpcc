from fastapi import FastAPI
import requests
from datetime import datetime
import json

app = FastAPI()

# CPCB API endpoints
FETCH_API_URL = "https://airquality.cpcb.gov.in/rawDataApi/hourly_concentration"
DECRYPT_API_URL = "https://airquality.cpcb.gov.in/decrypt_service/decrypt"

# API key
API_KEY = "CPCB@CCR@2023"

# Pollutant parameters
PARAMETERS = [
    "PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "SO2", "CO", "Ozone",
    "Benzene", "Toluene", "Xylene", "Eth_Benzene", "MP_Xylene",
    "O_Xylene", "CH4", "THC", "WS", "WD", "AT", "RH", "RF", "SR",
    "Temp", "BP"
]

@app.get("/cpcb_data")
def get_cpcb_data(state: str = "Delhi",
                  from_time: str = "05/08/2025 05:00",
                  to_time: str = "05/08/2025 05:59"):
    """
    Fetch CPCB air quality data, decrypt it, and return as JSON table.
    Date format for from_time/to_time: dd/MM/yyyy HH:mm
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Step 1: Get encrypted data
    payload_record = {
        "state": state,
        "parameters": PARAMETERS,
        "from_time": from_time,
        "to_time": to_time,
        "key": API_KEY
    }

    raw_response = requests.post(FETCH_API_URL, headers=headers, json=payload_record, timeout=30)
    raw_json = raw_response.json()

    if "Data" not in raw_json:
        return {"error": "No 'Data' field in CPCB response", "response": raw_json}

    base64_text = raw_json["Data"]

    # Step 2: Decrypt
    decrypt_payload = {
        "key": API_KEY,
        "encrypted_data": base64_text
    }

    decrypt_response = requests.post(DECRYPT_API_URL, headers=headers, json=decrypt_payload, timeout=30)
    decrypted_json = decrypt_response.json()

    if "Data" not in decrypted_json:
        return {"error": "No 'Data' field in decryption response", "response": decrypted_json}

    return decrypted_json["Data"]
