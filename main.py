import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud.aiplatform.gapic import ReasoningEngineServiceClient
from google.cloud.aiplatform_v1.types import ReasoningEngineSpec

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
            # The full resource name of the reasoning engine
            engine_name = "projects/sandbox-456821/locations/us-central1/reasoningEngines/1352192593978458112"

            # Create a client for the Reasoning Engine Service
            client = ReasoningEngineServiceClient(
                api_endpoint="us-central1-aiplatform.googleapis.com"
            )

            # Prepare the request
            request_payload = {
                "input": "I seek a vision for my future."
            }
            
            # The query method requires the name and the input as a dict
            response = client.query_reasoning_engine(
                name=engine_name,
                input=request_payload,
            )
            
            # The response is a Struct, convert it to a dict
            output_dict = dict(response.output)

            return jsonify(output_dict), 200

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
