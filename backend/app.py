import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security: Configure CSRF protection
# For API-only applications, we need to configure it properly
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Prometheus WITH endpoint configuration
metrics = PrometheusMetrics(app, defaults_prefix='currency_converter')
metrics.info('app_info', 'Currency Converter API', version='1.0.0')

# Security: Get API key from environment variable - NO HARDCODED DEFAULT
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
if EXCHANGE_API_KEY is None:
    print("⚠️ WARNING: EXCHANGE_API_KEY environment variable is not set. API will not work without it.")

# Configure CORS with security settings
CORS(app, resources={r"/*": {"origins": "*"}})  # In production, restrict origins

# Custom metric for tracking conversions
conversion_counter = metrics.counter(
    'conversions_total',
    'Total currency conversion requests',
    labels={'status': lambda resp: resp.status_code}
)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "currency-converter-api",
        "endpoints": {
            "rates": "/rates",
            "health": "/health",
            "metrics": "/metrics"
        },
        "security": {
            "csrf_enabled": app.config['WTF_CSRF_ENABLED'],
            "environment": os.getenv('FLASK_ENV', 'development'),
            "api_key_configured": EXCHANGE_API_KEY is not None
        }
    }), 200

@app.route('/rates')
@conversion_counter
def get_rates():
    """Get currency exchange rates - GET endpoint, CSRF exempt by default"""
    if EXCHANGE_API_KEY is None:
        return jsonify({"status": "error", "message": "API key not configured. Set EXCHANGE_API_KEY environment variable."}), 503
    try:
        # Security: API key comes from environment variable
        api_key = EXCHANGE_API_KEY
        base = request.args.get('base', 'USD')
        
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

@app.route('/convert')
@conversion_counter
def convert():
    """Convert currency - GET endpoint, CSRF exempt by default"""
    if EXCHANGE_API_KEY is None:
        return jsonify({"status": "error", "message": "API key not configured. Set EXCHANGE_API_KEY environment variable."}), 503
    try:
        from_curr = request.args.get('from', 'USD')
        to_curr = request.args.get('to', 'EUR')
        amount = float(request.args.get('amount', 1))
        
        # Security: API key comes from environment variable
        api_key = EXCHANGE_API_KEY
        
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}",
            timeout=5
        )
        data = response.json()
        
        return jsonify({
            "status": "success",
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "converted": data.get("conversion_result"),
            "rate": data.get("conversion_rate")
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from flask import Response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Export application for PythonAnywhere
application = app

if __name__ == '__main__':
    # Security note: For production, use a proper secret key
    if os.getenv('FLASK_ENV') == 'production':
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
        if not app.config['SECRET_KEY']:
            raise ValueError("FLASK_SECRET_KEY must be set in production")
    
    app.run(host='0.0.0.0', port=5000, debug=False)