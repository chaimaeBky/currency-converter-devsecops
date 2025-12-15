import os
from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS - PythonAnywhere requires specific setup
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://your-frontend-domain.vercel.app",  # Will update after Vercel deploy
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "currency-converter-api"}), 200

# Root endpoint
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Currency Converter API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "rates": "/rates",
            "health": "/health"
        }
    }), 200

# Rates endpoint (updated for PythonAnywhere)
@app.route('/rates', methods=['GET'])
def get_rates():
    """Fetch currency conversion rates from external API"""
    # Get API key from environment or use default (for testing)
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "97f9dc6126138480ee6da5fb")
    base_currency = request.args.get('base', 'USD')
    
    try:
        # PythonAnywhere allows requests to this API
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success":
            return jsonify({
                "status": "success",
                "base": data.get("base_code", "USD"),
                "conversion_rates": data.get("conversion_rates", {})
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "External API error"
            }), 502

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# PythonAnywhere requires this
application = app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)