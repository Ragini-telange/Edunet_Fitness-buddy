from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# === CONFIGURATION ===
API_KEY = "psOjRjXctlwwMO-u8pNIMZdI5XCXdd3ixnkYseHGScgI"  # 🔐 Replace this with your real API Key
PROJECT_ID = "7543c856-b01e-4bcd-b80e-111b849c67ac"
REGION = "eu-gb"  # Watsonx region from your URL

# === IBM Cloud IAM Token URL ===
IAM_URL = f"https://iam.cloud.ibm.com/identity/token"

# === Watsonx Inference URL ===
WATSONX_URL = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

# === Get IAM Token from API key ===
def get_access_token(api_key):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"
    response = requests.post(IAM_URL, headers=headers, data=data)
    token = response.json().get("access_token")
    return token

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    access_token = get_access_token(API_KEY)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": "meta-llama/llama-2-13b-chat",
        "input": user_input,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200
        },
        "project_id": PROJECT_ID
    }

    response = requests.post(WATSONX_URL, headers=headers, json=payload)

    # ✅ Print full Watsonx response for debugging
    print("🔁 Watsonx response:", response.text)

    try:
        generated_text = response.json()["results"][0]["generated_text"]
    except Exception as e:
        print("⚠️ Failed to get response:", e)
        return jsonify({"response": "⚠️ Sorry, Watsonx didn't return a response."})

    return jsonify({"response": generated_text})

if __name__ == "__main__":
    app.run(debug=True)
