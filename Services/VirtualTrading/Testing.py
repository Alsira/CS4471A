from cloudant.client import Cloudant
import requests
import json

API_USER = "3fdf89c0-70ae-421c-8a5c-f3f07abc3988-bluemix"
API_KEY = "IGzHN-SnHoE7X-Xn_wlCK0ogL62UusTafB2ZO8CZeXub"

def test_create():
    """
    This tests if the add mechanic of the service works
    """
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    database = client["virtualcurrency"]
    token_d = client["tokens"]
    
    # Delete if they exist
    if "test" in database:
        database["test"].delete()
        
    # Add a fake token
    if "token123" in token_d:
        token_d["token123"].delete()
        
    token_d.create_document({
        "_id": "token123",
        "username": "test"
        })
    
    response = requests.post("http://127.0.0.1:5000/virtual/add/token123")
    
    if response.status_code != 200:
        return False
    else: 
        return True

    # Check if they are in the database
    if "test" not in database:
        return False
    
    print(database["test"])
    
    
def test_exists():
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    database = client["virtualcurrency"]
    token_d = client["tokens"]
    
    # Delete if they exist
    if "test" in database:
        database["test"].delete()
        
    # Ask if test is in the database
    response = requests.get("http://127.0.0.1:5000/virtual/exists/test")
    
    if json.loads(response.text)["result"] == True:
        return False
    
    doc = {"_id": "test", "username": "test"}
    
    database.create_document(doc)
    
    # Ask if test is in the database
    response = requests.get("http://127.0.0.1:5000/virtual/exists/test")
    
    if len(response.text) > 0 and json.loads(response.text)["result"] == False:
        return False
    
    return True

def test_getStock():
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    database = client["virtualcurrency"]
    token_d = client["tokens"]
    
    # Delete if they exist
    if "test" in database:
        database["test"].delete()
        
    # Add a fake token
    if "token123" in token_d:
        token_d["token123"].delete()
        
    token_d.create_document({
        "_id": "token123",
        "username": "test"
        })
    
        
    doc = {"_id": "test",
           "username": "test",
           "stock": {
               "APPL": {
                   "buy": [{"share": 5, "amount": 12.23, "date": "25/12/2023"}],
                   "sell": []
                   }
               },
            "currency": 1200
            }
               
    database.create_document(doc)
    
    response = requests.get("http://127.0.0.1:5000/virtual/get/token123")
    js = json.loads(response.text)
    del js["_rev"]
    
    if len(response.text) and doc == js:
        return True
    
    else:
        print("ERROR : ")
        print(response.text)
        return False
    
def test_tradeVirtual():
    
    client = Cloudant.iam(API_USER, API_KEY, connect=True)
    
    database = client["virtualcurrency"]
    token_d = client["tokens"]
    
    # Delete if they exist
    if "test" in database:
        database["test"].delete()
        
    # Add a fake token
    if "token123" in token_d:
        token_d["token123"].delete()
        
    token_d.create_document({
        "_id": "token123",
        "username": "test"
        })
    
    
    doc = {"_id": "test",
           "username": "test",
           "stock": {
               "APPL": {
                   "buy": [{"share": 5, "amount": 12.23, "date": "25/12/2023"}],
                   "sell": []
                   }
               },
            "currency": 1200
            }
               
    # Add the document
    database.create_document(doc)

    # Check response
    response = requests.post("http://127.0.0.1:5000/virtual/trade/token123", data=json.dumps({"symbol": "APL", "shares": 5, "worth": 12.23, "type": "buy"}), headers={"Content-Type": "application/json"})
    
    # Output 
    
    return response.status_code == 200
    
    
    
if __name__ == "__main__":
    
    print("Attempting Test 1 - Testing Creation of Account")
    
    result = test_create()
    
    if result:
        print("PASSED", end="\n\n")
    else:
        print("FAILED", end="\n\n")
        
    print("Attempting Test 2 - Testing Account Existance")
    
    result = test_exists()
    
    if result:
        print("PASSED", end="\n\n")
    else:
        print("FAILED", end="\n\n")
        
    print("Attempting Test 3 - Testing Get Stock Functionality")
    
    result = test_getStock()
    
    if result:
        print("PASSED", end="\n\n")
    else:
        print("FAILED", end="\n\n")
        
    print("Attempting Test 4 - Testing Virtual Trading Functionality")
    
    result = test_tradeVirtual()
    
    if result:
        print("PASSED", end="\n\n")
    else:
        print("FAILED", end="\n\n")
    
    exit(0)
    
    
