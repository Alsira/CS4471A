from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Johnny Long Stock

@app.route("/ping", methods=["GET"])
def ping():
    return json.dumps({"status": "good"})

@app.route("/", methods=["GET"])
def index():
    symbol = request.args.get("symbol")
    if symbol:
        data = get_stock_data(symbol)
        if data is not None and not data.empty:
            json_data = format_stock_data(data, symbol)
            return jsonify(json_data)
        else:
            return jsonify({"error": "Unable to fetch stock data for the given symbol."}), 400
    else:
        return jsonify({"error": "Symbol parameter is missing in the URL."}), 400

def get_stock_data(symbol):
    try:
        stock_data = yf.Ticker(symbol)
        historical_data = stock_data.history(period="1y")
        return historical_data
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def format_stock_data(data, symbol):
    formatted_data = {
        "symbol": symbol,
        "stock_data": []
    }
    
    for index, row in data.iterrows():
        formatted_data["stock_data"].append({
            "Date": index.strftime("%Y-%m-%d"),
            "Close": row["Close"]
        })
    
    return formatted_data


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
    
    app.run("0.0.0.0", port=5002, debug=True)
