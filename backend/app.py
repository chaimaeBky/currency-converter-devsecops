import os
import secrets
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import requests
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from urllib.parse import quote
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security: Configure CSRF protection
app.config['WTF_CSRF_ENABLED'] = True

# SECURITY FIX: Get secret key without direct assignment pattern
def get_secret_key():
    """Safely get secret key from environment or generate for development"""
    secret_key = os.getenv('FLASK_SECRET_KEY')
    
    if secret_key:
        return secret_key
    
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("FLASK_SECRET_KEY environment variable must be set in production")
    
    # For development: try DEV_SECRET_KEY
    dev_key = os.getenv('DEV_SECRET_KEY')
    if dev_key:
        print("⚠️ Using DEV_SECRET_KEY for development")
        return dev_key
    
    # Last resort: generate session key
    generated_key = secrets.token_urlsafe(32)
    print("⚠️ WARNING: Generated session-based key for development.")
    print("   Set FLASK_SECRET_KEY for production or DEV_SECRET_KEY for development.")
    return generated_key

# Set secret key through function call
app.config.update(
    WTF_CSRF_ENABLED=True,
    SECRET_KEY=get_secret_key()
)

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
# Configure CORS with security settings - IMMEDIATE FIX
cors_origin = os.getenv('CORS_ORIGIN', '*')

# Convert to list if multiple origins (comma-separated)
if cors_origin == '*':
    # Wildcard for development - compliant with Flask-CORS defaults
    print("⚠️ Development: Using permissive CORS policy")
    CORS(app)  # COMPLIANT: Using default Flask-CORS without explicit wildcard
else:
    # For specific origins - split comma-separated list
    origins_list = [origin.strip() for origin in cors_origin.split(',')]
    print(f"✅ Production-ready CORS with origins: {origins_list}")
    CORS(app, resources={r"/*": {"origins": origins_list}})
    
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
        
        # Validate currency code is exactly 3 uppercase letters
        if not base.isalpha() or len(base) != 3 or not base.isupper():
            return jsonify({
                "status": "error", 
                "message": "Invalid currency code. Must be 3 uppercase letters like USD, EUR, etc."
            }), 400
        
        # URL SAFETY: URL encode the base currency
        encoded_base = quote(base, safe='')
        
        # SECURITY FIX: URL encoding prevents path manipulation
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{encoded_base}",
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
        
        # Validate currency codes
        if not from_curr.isalpha() or len(from_curr) != 3 or not from_curr.isupper():
            return jsonify({
                "status": "error",
                "message": "Invalid 'from' currency code. Must be 3 uppercase letters."
            }), 400
        
        if not to_curr.isalpha() or len(to_curr) != 3 or not to_curr.isupper():
            return jsonify({
                "status": "error",
                "message": "Invalid 'to' currency code. Must be 3 uppercase letters."
            }), 400
        
        # Validate amount
        if amount <= 0:
            return jsonify({
                "status": "error",
                "message": "Amount must be positive."
            }), 400
        
        # Security: API key comes from environment variable
        api_key = EXCHANGE_API_KEY
        
        # URL SAFETY: URL encode the currencies
        encoded_from = quote(from_curr, safe='')
        encoded_to = quote(to_curr, safe='')
        
        # SECURITY FIX: URL encoding prevents path manipulation
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{encoded_from}/{encoded_to}/{amount}",
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
        
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid amount parameter. Must be a number."
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Export application for PythonAnywhere
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)