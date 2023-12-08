from flask import Flask, jsonify
import yfinance as yf
import requests.exceptions
import requests
import json
import sys
import os
from time import sleep

app = Flask(__name__)

def add_to_json_array(ticker, file_path="valid_symbols.json"):
    # Load existing symbols from the JSON file if it exists
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            valid_symbols = json.load(file)
    else:
        valid_symbols = []

    # Add the ticker to the array if it's not already there
    if ticker not in valid_symbols:
        valid_symbols.append(ticker)

        # Save the updated array back to the JSON file
        with open(file_path, "w") as file:
            json.dump(valid_symbols, file)

    return valid_symbols

def search_stock(ticker):
    stock = yf.Ticker(ticker)

    try:
        # Attempting to fetch the stock information
        info = stock.info

        # Extracting specific details 
        stock_data = {
            "Company Name": info.get("longName"),
            "Current Price": info.get("currentPrice"),
            "Previous Close": info.get("previousClose"),
            "Open Price": info.get("open"),
            "Day's Range": f"{info.get('dayLow')} - {info.get('dayHigh')}",
            "52 Week Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
            "Volume": info.get("volume"),
            "Percent Change": info.get("PercentChange"),
            "Average Volume": info.get("averageVolume"),
            "Market Cap": info.get("marketCap"),
            "P/E Ratio": info.get("trailingPE"),
            "Dividend Yield": info.get("dividendYield") * 100 if info.get("dividendYield") is not None else None
        }

        # Add valid stock symbol to JSON array and get the updated list
        valid_symbols = add_to_json_array(ticker)

        return stock_data, valid_symbols
    except requests.exceptions.HTTPError:
        return f"Invalid stock symbol '{ticker}'. Please enter a valid stock symbol.", []

@app.route('/search_stock/<string:symbol>', methods=['GET'])
def handle_stock_request(symbol):
    if not symbol:
        return jsonify({"error": "No stock symbol provided"}), 400

    stock_info, valid_symbols = search_stock(symbol)
    if isinstance(stock_info, str):  # If the stock_info is an error message
        return jsonify({"error": stock_info}), 404

    return jsonify({"stock_info": stock_info, "valid_symbols": valid_symbols})


def register(registry_url: str, name: str, service_url: str) -> bool:
    
    # Send the request
    data = {
        "name": name,
        "url": service_url
        }    
        
    response = requests.post(registry_url + "/register", data=json.dumps(data), headers={"Content-Type": "application/json"})
    
    if response.status_code > 299 or response.status_code < 200:
        return False
    
    else:
        return True
            
if __name__ == "__main__":
    
    # register
    response = False
    try:
        url = os.environ["REGISTRY"]
        this_url = os.environ["HERE"]
    
    except:
        response = True
    
    while not response:

        try:
            register(url, "virtual_trader", this_url)
            response = True
        except:
      
            sleep(5)
        
    app.run("0.0.0.0", port=5000, debug=True)
