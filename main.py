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
    # This endpoint is a trigger; it does not accept a request body.
    if request.get_data():
        return jsonify({"error": "Request body is not permitted for this endpoint."}), 400

    method = request.args.get("method", "basic")

    print(f"Vision creation triggered with method: {method}")

    if method == "live":

        try:
            # TODO: Replace with your project ID, location, and endpoint ID
            aiplatform.init(project="sandbox-456821", location="us-east4")
            endpoint = aiplatform.Endpoint("YOUR_ENDPOINT_ID")

            # The instances can be empty if your model does not require any input
            instances = [{}]
            prediction = endpoint.predict(instances=instances)

            # Assuming the model returns a prediction with "text" and "image" fields
            response_data = prediction.predictions[0]
            
            return jsonify(response_data), 200

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": "Failed to generate vision from the AI model."}), 500

    # Default is to return a mock response if method is unspecified or unrecognized
    response_data = {
        "text": "You walk down the spaghetti stairs to realize you are face to face with a tiger",
        "image": "https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg",
    }
    return jsonify(response_data), 202



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))