import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)

# ENABLE CORS - THIS IS CRITICAL
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "currency-converter-api"
    }), 200

@app.route('/rates')
def get_rates():
    """Get currency exchange rates - WORKING VERSION"""
    try:
        # Hardcoded API key (no os.environ issues)
        api_key = "97f9dc6126138480ee6da5fb"
        base = request.args.get('base', 'USD')
        
        # Call external API
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}",
            timeout=5
        )
        data = response.json()
        
        return jsonify({
            "status": "success",
            "base": data.get("base_code", "USD"),
            "conversion_rates": data.get("conversion_rates", {})
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# PythonAnywhere requirement
application = app

if __name__ == '__main__':
    app.run()
