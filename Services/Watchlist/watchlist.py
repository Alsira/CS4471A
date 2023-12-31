from flask import Flask, jsonify, request
from cloudant.client import Cloudant

from time import sleep
import os
import sys
import json
import requests
import threading

app = Flask(__name__)

# Cloudant credentials (replace with your actual credentials)
API_USER = "3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix"
API_KEY = "IGzHN-SnHoE7X-Xn_wlCK0ogL62UusTafB2ZO8CZeXub"

# Establish a connection to the Cloudant database
client = Cloudant.iam(API_USER, API_KEY, connect=True)
database = client["watchlist"]

@app.route("/ping", methods=["GET"])
def ping():
    return json.dumps({"status": "good"})

@app.route('/user_watchlist', methods=['GET'])
def get_user_watchlist():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Fetch the watchlist for the given user ID
    try:
        for document in database:
            if document.get('_id') == user_id:
                # Extract stock symbols from the list of stock dictionaries
                stocks = [stock['stock'] for stock in document.get('stocks', [])]
                return jsonify(stocks)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def register(registry_url: str, name: str, service_url: str) -> bool:
        
    while True:
        
        try:    
            # Send the request
            data = {
                "name": name,
                "url": service_url
                }    
                
            response = requests.post(registry_url + "/register", data=json.dumps(data), headers={"Content-Type": "application/json"})
            sleep(20)
            
        except:
            sleep(5)

if __name__ == "__main__":
    
    # register
    response = False
    try:
        url = os.environ["REGISTRY"]
        this_url = os.environ["HERE"]
    
        t = threading.Thread(target=register, args=(url, "watchlist", this_url))
        t.start()
        
    except Exception as e:
        raise Exception(str(e))
    
    print(url)
    print(this_url)
    exit()
    
    app.run("0.0.0.0", port=5002, debug=False)
