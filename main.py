import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud.aiplatform.gapic import ReasoningEngineExecutionServiceClient
from google.cloud.aiplatform_v1.types import ReasoningEngineSpec
from google.api_core import client_options
import proto

app = Flask(__name__)
CORS(app, resources={r"/vision": {"origins": "http://www.zudduz.com"}})

def parse_ai_response(response_string):
    if not isinstance(response_string, str):
        return {"text": str(response_string) if response_string is not None else "No output"}

    json_start_index = response_string.rfind('{')
    if json_start_index != -1:
        json_string = response_string[json_start_index:]
        try:
            parsed_json = json.loads(json_string)
            return {
                "vision_text": parsed_json.get("vision_text"),
                "image_url": parsed_json.get("image_url")
            }
        except json.JSONDecodeError:
            return {"text": response_string}
    else:
        return {"text": response_string}

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

    method = request.args.get("method", "live")

    print(f"Vision creation triggered with method: {method}")

    if method == "live":
        try:
            engine_name = "projects/sandbox-456821/locations/us-central1/reasoningEngines/1352192593978458112"
            client = ReasoningEngineExecutionServiceClient(
                client_options=client_options.ClientOptions(api_endpoint="us-central1-aiplatform.googleapis.com")
            )
            request_payload = {"input": "I seek a vision for my future."}
            request_msg = {"name": engine_name, "input": request_payload}
            
            response = client.query_reasoning_engine(request=request_msg)
            
            val = getattr(response, 'output', None)
            output_data = parse_ai_response(val)

            return jsonify(output_data), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"An error occurred: {e}"}), 500

    response_data = {
        "text": "You walk down the linguini stairs to realize you are face to face with a tiger",
        "image": "https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg",
    }
    return jsonify(response_data), 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
