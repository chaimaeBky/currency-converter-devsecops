import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Initialize Prometheus WITH endpoint configuration
metrics = PrometheusMetrics(app, defaults_prefix='currency_converter')
metrics.info('app_info', 'Currency Converter API', version='1.0.0')

CORS(app)

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
            "metrics": "/metrics"  # This will exist
        }
    }), 200

@app.route('/rates')
@conversion_counter  # Track this endpoint
def get_rates():
    """Get currency exchange rates"""
    try:
        api_key = "97f9dc6126138480ee6da5fb"
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

# Export application for PythonAnywhere
application = app

if __name__ == '__main__':
    # Enable metrics collection
    metrics.start_http_server(port=5001)  # Metrics on port 5001
    app.run(host='0.0.0.0', port=5000, debug=False)