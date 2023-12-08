'''
Documentation, License etc.

@package VirtualTrading
'''

from flask import Flask, request
import json
import sys
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
    

@app.route("/virtual/get/<string:token>", methods=["GET"])
def getUserStock(token: str):
    
    # Find out who is asking
    try:
        
        # Get the person from the tokens
        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        
        try:
            token_database = client["tokens"]
        
            # Get the username from the token
            user_token = token_database[token]
            username = user_token["username"]
        
        except KeyError as e:
            return json.dumps({"error": str(e)}), 400
        
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
                "stock": {}
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


@app.route("/virtual/trade/<string:token>", methods=["PUT", "POST"])
def tradeVirtual(token: str):
    
    # Get the request data
    data = request.get_json(force = True)
    
    try:
    
        # Get the username from the token
        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        token_database = client["tokens"]
        virt_database = client["virtualcurrency"]
        
        if token not in token_database:
            return json.dumps({"error": "token does not exist - " + token}), 400
        
        # Get the username
        username = token_database[token]["username"]
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
        if symbol not in virt_info["stock"]:
                virt_info["stock"][symbol] = {}
                virt_info["stock"][symbol]["sell"] = list()
                virt_info["stock"][symbol]["buy"] = list()
                
                
        virt_info["stock"][symbol][type_of_request].append({"shares": stocks, "worth": cost, "date": date})
        
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
    
    
@app.route("/virtual/add/<string:token>", methods=["POST", "PUT"])
def createUser(token: str):
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    # Databases
    token_database = client["tokens"]
    virt_database = client["virtualcurrency"]
    
    try:
        
        if token in token_database:
            
            # Add the user
            username = token_database[token]["username"]
            
            # Add the user to the database
            result = add_user(username)
            
            if not result:
                return json.dumps({"error": "Cannot add user"}), 400
            
            return ""
        
        else:
            
            return json.dumps({"error": "token " + str(token) + " does not exist"}), 400

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
    url = sys.argv[1]
    this_url = sys.argv[2]
    
    response = True
    
    while not response:

        try:
            register(url, "virtual_trader", this_url)
            response = True
        except:
      
            sleep(5)
        
        
    app.run("0.0.0.0", port=5000, debug=True)
