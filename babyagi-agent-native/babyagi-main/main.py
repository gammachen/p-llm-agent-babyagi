import babyagi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = babyagi.create_app('/dashboard')

print(f"Starting BabyAGI... LLM_PROVIDER={os.getenv('LLM_PROVIDER')} LLM_MODEL={os.getenv('LLM_MODEL')} OPENAI_MODEL={os.getenv('OPENAI_MODEL')}")

# Add OpenAI key to enable automated descriptions and embedding of functions.
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")
babyagi.add_key_wrapper('openai_api_key', openai_api_key)


@app.route('/')
def home():
    return f"Welcome to the main app. Visit <a href=\"/dashboard\">/dashboard</a> for BabyAGI dashboard."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
