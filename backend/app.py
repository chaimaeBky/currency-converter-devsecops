import os
from flask import Flask, jsonify
import requests
from flask_cors import CORS  

app = Flask(__name__) 

CORS(app, resources={
    r"/*": {
        "origins": [
            "https://react-frontend-unique123.eastus.azurecontainer.io",
            "http://react-frontend-unique123.eastus.azurecontainer.io",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/rates', methods=['GET'])
def getRates():
    try:
        response = requests.get(
            "https://v6.exchangerate-api.com/v6/97f9dc6126138480ee6da5fb/latest/USD"
        )
        response.raise_for_status()

        data = response.json()

        # 🔥 IMPORTANT : les tests veulent EXACTEMENT ce format :
        return jsonify({
            "status": "success",
            "conversion_rates": data.get("conversion_rates", {})
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch conversion rates",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
