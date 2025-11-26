import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import aiplatform

app = Flask(__name__)
CORS(app, resources={r"/vision": {"origins": "http://www.zudduz.com"}})

@app.route("/")
def hello_world():
    """Example endpoint."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

@app.route("/vision", methods=["POST"])
def create_vision():
    """
    Endpoint to trigger the AI to produce a new vision for the UI.
    Accepts a POST request without a body.
    """
    if request.get_data():
        return jsonify({"error": "Request body is not permitted for this endpoint."}), 400

    method = request.args.get("method", "basic")

    print(f"Vision creation triggered with method: {method}")

    if method == "live":
        try:
            # Initialize the Vertex AI client
            aiplatform.init(project="sandbox-456821", location="us-central1")

            # Get a reference to the an Endpoint
            endpoint = aiplatform.Endpoint("1352192593978458112")

            # The `predict` method requires a list of instances.
            instances = [{"input": "Please grant me a vision."}]

            # Send the prediction request
            prediction = endpoint.predict(instances=instances)

            # Extract the prediction from the response
            # The response format may vary, adjust if necessary
            response_data = prediction.predictions[0]


            return jsonify(response_data), 200

        except Exception as e:
            # Return the actual exception for debugging
            return jsonify({"error": f"An error occurred: {e}"}), 500

    # Default is to return a mock response
    response_data = {
        "text": "You walk down the linguini stairs to realize you are face to face with a tiger",
        "image": "https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg",
    }
    return jsonify(response_data), 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
