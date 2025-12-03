import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud.aiplatform.gapic import ReasoningEngineExecutionServiceClient
from google.api_core import client_options

# Initialize Flask App and CORS
app = Flask(__name__)
# Allow requests only from the specified origin for the /vision endpoint
CORS(app, resources={r"/vision": {"origins": "https://www.zudduz.com"}})


def parse_ai_response(response_string: str) -> dict:
    """
    Parses the string response from the AI model, which may contain JSON.
    It looks for the last occurrence of a JSON object in the string,
    parses it, and transforms it into the desired format.
    """
    if not isinstance(response_string, str):
        return {
            "text":
                str(response_string)
                if response_string is not None else "No output"
        }

    # Find the beginning of the last JSON object in the response string
    json_start_index = response_string.rfind('{')
    if json_start_index != -1:
        json_string = response_string[json_start_index:]
        try:
            parsed_json = json.loads(json_string)
            # Transform the parsed JSON to the format expected by the frontend
            return {
                "text": parsed_json.get("vision_text"),
                "image": parsed_json.get("image_url")
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return the original string
            return {"text": response_string}
    else:
        # If no JSON object is found, return the original string
        return {"text": response_string}


def get_ai_vision() -> dict:
    """
    Queries the Reasoning Engine to get a new vision.
    """
    # Get the Reasoning Engine name from an environment variable
    engine_name = os.environ.get("REASONING_ENGINE_NAME")
    if not engine_name:
        raise ValueError("REASONING_ENGINE_NAME environment variable not set.")

    # Configure the API client
    client_options_config = client_options.ClientOptions(
        api_endpoint="us-central1-aiplatform.googleapis.com")
    client = ReasoningEngineExecutionServiceClient(
        client_options=client_options_config)

    # Prepare and send the request to the Reasoning Engine
    request_payload = {"input": "I seek a vision for my future."}
    request_msg = {"name": engine_name, "input": request_payload}

    response = client.query_reasoning_engine(request=request_msg)

    # Extract and parse the output from the response
    raw_output = getattr(response, 'output', None)
    return parse_ai_response(raw_output)


@app.route("/vision", methods=["POST"])
def create_vision():
    """
    Endpoint to trigger the AI to produce a new vision for the UI.
    Supports a 'method' query parameter to switch between 'live' and mock data.
    """
    if request.get_data():
        return jsonify(
            {"error": "Request body is not permitted for this endpoint."}), 400

    method = request.args.get("method", "live")
    print(f"Vision creation triggered with method: {method}")

    if method == "live":
        try:
            output_data = get_ai_vision()
            return jsonify(output_data), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"An error occurred: {e}"}), 500
    else:
        # Provide mock data for testing or development
        mock_response_data = {
            "text":
                "You walk down the linguini stairs to realize you are face to face with a tiger",
            "image":
                "https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg",
        }
        return jsonify(mock_response_data), 202


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
