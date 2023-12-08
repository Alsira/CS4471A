'''
Documentation, License etc.

@package VirtualTrading
'''

from flask import Flask, request
import json
import sys
import os
import requests
from datetime import date
from time import sleep

from cloudant.client import Cloudant

API_USER = "3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix"
API_KEY = "IGzHN-SnHoE7X-Xn_wlCK0ogL62UusTafB2ZO8CZeXub"

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return json.dumps({"status": "good"})

@app.route("/virtual/exists/<string:user>", methods=["GET"])
def user_exists(user: str):
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    # Database
    virt_database = client["virtualcurrency"]
    
    if user in virt_database:
        return json.dumps({"result": True})
    
    else:
        return json.dumps({"result": False})
    

@app.route("/virtual/get/<string:username>", methods=["GET"])
def getUserStock(username: str):
    
    # Find out who is asking
    try:
        
        # Get the person from the tokens
        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        
        # Get the virtual currency datbase
        try:
            virtual_currency = client["virtualcurrency"]
        except KeyError as e:
            return json.dumps({"error": str(e) }), 500
        
        # Get the document belonging to the user
        try:
            
            # Get the users document
            virtual_document = virtual_currency[username]
            
            # Return the cleaned document
            return json.dumps(virtual_document)
       
        # Virtual document issues
        except KeyError as e:
            return json.dumps({"error": str(e)}), 500
       
    # Errors
    except KeyError as e:
        return "{\"error\":" + "\"" + e + "\"" + "}", 400
        
    except Exception as e:
        return json.dumps({"error": str(e)}), 400
    
    
def add_user(username: str, force: bool = True) -> bool:

        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        try:
        
            # Add the user
            virt_database = client["virtualcurrency"]
            
            # Data to enter in the database
            data = {
                "_id": username,
                "username": username,
                "currency": 0,
                "stocks": {}
                }
            
            # Determine if they are a paying customer
            user_database = client["users"]
            user_data = user_database[username]

            if "status" not in user_data or user_data["status"] == False:
                data["currency"] = 2500
            
            else:
                data["currency"] = 100000
            
            # Erase
            if username in virt_database and not force:
                return
            virt_database.create_document(data)
        
            return True
        
        except KeyError:
            return False
        

def getDate():
    return date.today().strftime("%d%m%y")


@app.route("/virtual/trade/<string:username>", methods=["PUT", "POST"])
def tradeVirtual(username: str):
    
    # Get the request data
    data = request.get_json(force = True)
    
    try:
    
        # Get the username from the token
        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        virt_database = client["virtualcurrency"]
        
        virt_info = virt_database[username]
    
        # Get information
        symbol = data["symbol"]
        stocks = data["shares"]
        cost = data["worth"]
        date = getDate()
    
        # Get the request type
        type_of_request = data["type"].lower()
        
        if type_of_request != "buy" and type_of_request != "sell":
            return json.dumps({"error": "Invalid argument. Need buy or sell " - str(data["type"])}), 400
        
        # find where the stock is
        if symbol not in virt_info["stocks"]:
                virt_info["stocks"][symbol] = {}
                virt_info["stocks"][symbol]["sell"] = list()
                virt_info["stocks"][symbol]["buy"] = list()
                
                
        virt_info["stocks"][symbol][type_of_request].append({"shares": stocks, "worth": cost, "date": date})
        
        if type_of_request == "buy":
            virt_info["currency"] -= cost
        else:
            virt_info["currency"] += cost
        
        # Update the document
        virt_info.save()
        
        return ""
            
    except KeyError as e:
        return json.dumps({"error": str(e)}), 400
    
    except Exception as e:
        return json.dumps({"error": str(e)}), 400
    
    
@app.route("/virtual/add/<string:username>", methods=["POST", "PUT"])
def createUser(username: str):
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    # Database
    virt_database = client["virtualcurrency"]
    
    try:
            
        # Add the user to the database
        result = add_user(username)
        
        if not result:
            return json.dumps({"error": "Cannot add user"}), 400
        
        return ""

    except KeyError as e:
        return json.dumps({"error": str(e)}), 400


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
        print("problem")
        response = True
    
    while not response:

        try:
            register(url, "virtual_trader", this_url)
            response = True
        except:
      
            sleep(5)
        
    app.run("0.0.0.0", port=5002, debug=False)
    
    
