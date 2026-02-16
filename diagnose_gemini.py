import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

with open("model_diagnosis.txt", "w") as f:
    f.write(f"Diagnosing API Key: {api_key[:5]}...\n")
    try:
        f.write("Attempting to list models...\n")
        models = list(genai.list_models())
        f.write(f"Found {len(models)} models.\n")
        for m in models:
            f.write(f"- Name: {m.name}\n")
            f.write(f"  Methods: {m.supported_generation_methods}\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
