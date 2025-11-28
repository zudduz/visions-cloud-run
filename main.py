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
            client = ReasoningEngineExecutionServiceClient(
                client_options=client_options.ClientOptions(api_endpoint="us-central1-aiplatform.googleapis.com")
            )

            # Prepare the request payload
            request_payload = {
                "input": "I seek a vision for my future."
            }
            
            # Construct the full request dictionary
            request_msg = {
                "name": engine_name,
                "input": request_payload
            }
            
            response = client.query_reasoning_engine(request=request_msg)
            
            # response.output is typically a google.protobuf.Value
            # However, depending on the client version/implementation, it might be behaving unexpectedly.
            # The previous error "str object has no attribute WhichOneof" suggests that response.output might actually be a plain string?
            # Or perhaps 'val' in the previous code was a string.
            
            # Let's inspect the type or try to just access it directly if it's already a dict or string.
            
            output_data = {}
            if hasattr(response, 'output'):
                val = response.output
                # If it's already a dict
                if isinstance(val, dict):
                    output_data = val
                # If it's a string (maybe JSON string?)
                elif isinstance(val, str):
                    try:
                        output_data = json.loads(val)
                    except:
                         output_data = {"result": val}
                # If it is a proto Value, it should have WhichOneof, unless it's not a generated proto object
                elif hasattr(val, 'WhichOneof'):
                    # It is a protobuf Value
                    kind = val.WhichOneof("kind")
                    if kind == "struct_value":
                        # Convert MapComposite to dict
                        output_data = dict(val.struct_value)
                        # The items in the struct might still be Value objects? 
                        # Usually proto-plus handles this recursiveness, but 'dict()' on a MapComposite is shallow if not careful.
                        # However, for a simple JSON return, this usually works.
                    elif kind == "list_value":
                        output_data = list(val.list_value)
                    elif kind == "string_value":
                         output_data = {"result": val.string_value}
                    else:
                        output_data = {"result": str(val)}
                # If it is a MapComposite (proto-plus)
                elif hasattr(val, 'keys'):
                     output_data = dict(val)
                else:
                    output_data = {"result": str(val), "type": str(type(val))}
            else:
                 output_data = {"error": "Response has no output field", "response": str(response)}

            return jsonify(output_data), 200

        except Exception as e:
            # Return the actual exception for debugging
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"An error occurred: {e}"}), 500

    # Default is to return a mock response
    response_data = {
        "text": "You walk down the linguini stairs to realize you are face to face with a tiger",
        "image": "https://files.worldwildlife.org/wwfcmsprod/images/Tiger_resting_Bandhavgarh_National_Park_India/hero_small/6aofsvaglm_Medium_WW226365.jpg",
    }
    return jsonify(response_data), 202

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
