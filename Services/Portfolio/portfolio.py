from flask import Flask, jsonify, request
from cloudant.client import Cloudant

import os
import requests
import sys

app = Flask(__name__)

# Cloudant credentials (replace with your actual credentials)
API_USER = "3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix"
API_KEY = "IGzHN-SnHoE7X-Xn_wlCK0ogL62UusTafB2ZO8CZeXub"

client = Cloudant.iam(API_USER, API_KEY, connect=True)
database = client["portfolio"]

@app.route("/ping", methods=["GET"])
def ping():
    return json.dumps({"status": "good"})

@app.route('/user_stocks', methods=['GET'])
def get_user_stocks():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        for document in database:
            if document.get('_id') == user_id:
                stocks = []
                for stock_info in document.get('stocks', []):
                    stock_symbol = stock_info.get('stock')
                    shares = stock_info.get('shares')
                    stocks.append({"stock": stock_symbol, "shares": shares})
                return jsonify(stocks)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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