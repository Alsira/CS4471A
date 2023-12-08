from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
services = {}

@app.route('/register', methods=['POST'])
def register_service():
    data = request.get_json()
    
    service_name = data.get('name')
    service_url = data.get('url')

    if service_name and service_url:
        services[service_name] = service_url
        return jsonify({"message": f"Service '{service_name}' registered successfully."}), 201
    else:
        return jsonify({"error": "Service name and URL are required fields."}), 400

@app.route('/services', methods=['GET'])
def list_services():
    return jsonify(services)

@app.route('/service', methods=['GET'])
def get_service():
    service_name = request.args.get('name')
    if service_name:
        service_url = services.get(service_name)
        if service_url:
            return jsonify({"name": service_name, "url": service_url})
        else:
            return jsonify({"error": f"Service '{service_name}' not found."}), 404
    else:
        return jsonify({"error": "Service name query parameter 'name' is required."}), 400

@app.route('/relay', methods=['POST'])
def relay_message():
    data = request.get_json()
    target_service = data.get('target_service')
    message = data.get('message')

    if not target_service or not message:
        return jsonify({"error": "Both 'target_service' and 'message' fields are required."}), 400

    target_url = services.get(target_service)
    if not target_url:
        return jsonify({"error": f"Service '{target_service}' not found."}), 404

    try:
        response = requests.post(target_url, json={"message": message})
        return response.text, response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error sending message: {str(e)}"}), 500

if __name__ == '__main__':
    services["stock_visualization"] = ""
    services["portfolio_management"] = ""
    services["virtual_trader"] = ""
    services["stock_performance"] = ""

    app.run(host='localhost', port=5000)
