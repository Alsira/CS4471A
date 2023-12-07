'''
Documentation, License etc.

@package VirtualTrading
'''

from flask import Flask
import json

from cloudant.client import Cloudant

API_USER = "3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix"
API_KEY = "IGzHN-SnHoE7X-Xn_wlCK0ogL62UusTafB2ZO8CZeXub"
DATABASE_URL = "https://3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix.cloudantnosqldb.appdomain.cloud/"

app = Flask(__name__)

@app.route("/virtual/<string:token>", methods=["GET"])
def getUserStock():
    
    # Get the data out of the request
    data = request.get_json(force = True)
    
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
            virtual_document = virtual_currency[username]
            
            # Clean and return the document
            doc = {
                "current worth": virtual_document["current worth"],
                "buy times": virtual_document["buy times"],
                "sell times": virtual_document["sell times"]
                }
            
            # Return the cleaned document
            return json.dumps(doc)
       
        # Virtual document issues
        except KeyError as e:
            return json.dumps({"error": str(e)}), 500
       
    # Errors
    except KeyError as e:
        return "{\"error\":" + "\"" + e + "\"" + "}", 400
        
    except:
        return "{\"error\": \"general failure\"}", 400
    
@app.route("/virtual/<string:token>", methods=["PUT", "POST"])
def changeVirtual():
    
    # Get the request data
    data = request.get_json(force = True)
    
    try:
    
        # Get the username from the token
        client = Cloudant.iam(API_USER, API_KEY, connect=True)
        token_database = client["tokens"]
        
        
    
        # Get the request type
        type_of_request = data["type"]
        
        
        if type_of_request == "buy":
            
            


if __name__ == "__main__":
    app.run("127.0.0.1", 1080)
