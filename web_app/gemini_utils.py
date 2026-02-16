# import google.generativeai as genai

# def get_gemini_response(cough_type, api_key):
#     """
#     Sends cough type to Gemini API and returns structured health insights.
#     """
#     try:
#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel("gemini-2.5-flash")

#         prompt = f"""
#         You are a medical AI assistant.
#         The detected cough type is: {cough_type}.

#         Provide a detailed, structured explanation including:
#         - 💬 What this cough type usually indicates.
#         - 🧠 Possible causes or associated illnesses.
#         - 💊 Preventive measures and self-care steps.
#         - 🥦 Dietary and lifestyle recommendations.
#         - 🛡️ Effects on the immune system.
#         - ⚠️ When the patient should see a doctor.
#         """

#         response = model.generate_content(prompt)
#         return response.text

#     except Exception as e:
#         return f"⚠️ Error communicating with Gemini API: {e}"

# def analyze_audio_with_gemini(audio_path, api_key):
#     """
#     Uploads audio to Gemini for direct analysis and identification.
#     """
#     try:
#         genai.configure(api_key=api_key)
#         # Upload the file to Gemini
#         audio_file = genai.upload_file(path=audio_path)
        
#         # Using a more generic or latest alias if the specific version is not found
#         model = genai.GenerativeModel("gemini-2.5-flash")

#         prompt = """
# Analyze the provided audio sample from a cough detection system.

# 1. Determine whether the sound is:
#    - A human cough
#    - Background noise / non-cough sound

# 2. If the sound is a cough:

#    Cough Classification:
#    - Identify the type of cough:
#      (Dry, Wet/Productive, Asthmatic, Smoker's cough, Whooping, Barking/Croup-like, Wheezing-associated, Chronic cough, Acute cough)

#    Description:
#    - Provide a brief explanation of the detected cough type and its typical characteristics.

#    Nutritional Support:
#    - Suggest beneficial nutrient-rich foods or drinks that may help soothe or support recovery.

#    Possible Health Associations:
#    - List common conditions that may be associated with this cough type.
#    (Avoid definitive diagnosis.)

#    Severity Rating:
#    - Estimate cough severity: Mild / Moderate / Severe

# 3. If the sound is NOT a cough:
#    - Clearly describe what the sound appears to be.
#    (e.g., speech, silence, movement, environmental noise)

# Important:
# Provide general wellness guidance only. Do NOT present medical diagnoses. Keep the response clear, structured, and concise.
#         """

#         response = model.generate_content([prompt, audio_file])
#         return response.text

#     except Exception as e:
#         return f"⚠️ Error analyzing audio: {e}"


# -----------------------------------------------------------------------

import google.generativeai as genai


# ---------------- CONFIGURE MODEL ----------------
MODEL_NAME = "gemini-2.5-flash"


# ---------------- MAIN ANALYSIS PROMPT ----------------
ANALYSIS_PROMPT = """
Analyze the provided audio sample from a cough detection system.

🩺 Detection:
First, clearly determine whether the sound is:
- 🤧 Cough
- 🔊 Noise / Non-cough sound

If the sound is 🤧 Cough, provide:

🫁 Cough Type:
Identify the cough category:
(Dry, Wet/Productive, Asthmatic, Whooping, Barking/Croup-like, Wheezing-associated, Chronic cough, Acute cough, COVID-19 cough)

📖 Description:
Briefly describe the characteristics of this cough type.

🥗 Nutrient Support:
Suggest beneficial foods or drinks that may help soothe or support recovery.

⚠️ Possible Health Associations:
List common conditions linked with this cough type.
(Avoid definitive diagnosis.)

📊 Severity Rating:
Estimate severity:
Mild / Moderate / Severe

If the sound is 🔊 Noise / Non-cough:
Describe what the sound appears to be (speech, silence, movement, background noise).

Important:
Provide general wellness guidance only.
Do NOT present medical diagnoses.
Keep the response clear, structured, and concise.
"""


# ---------------- FUNCTION: AUDIO ANALYSIS ----------------
def analyze_audio_with_gemini(audio_path, api_key):
    """
    Uploads an audio file to Gemini and returns structured analysis.
    """

    try:
        genai.configure(api_key=api_key)

        print("Uploading audio to Gemini...")
        audio_file = genai.upload_file(path=audio_path)

        model = genai.GenerativeModel(MODEL_NAME)

        print("Analyzing audio...")
        response = model.generate_content([ANALYSIS_PROMPT, audio_file])

        return response.text

    except Exception as e:
        return f"⚠️ Error analyzing audio: {e}"


# ---------------- FUNCTION: COUGH TYPE EXPLANATION ----------------
def get_gemini_response(cough_type, api_key):
    """
    Sends detected cough type to Gemini for health insights.
    """

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(MODEL_NAME)

        prompt = f"""
The detected cough type is: {cough_type}

Provide structured health insights:

📖 Description:
Explain this cough type.

💬 What It Indicates:
General interpretation.

🧠 Possible Causes:
Common reasons (no diagnosis).

💊 Preventive Measures:
Self-care guidance.

🥗 Nutrient Support:
Helpful foods/drinks.

📊 Severity Insight:
Typical severity pattern.

⚠️ When to See a Doctor:
Safety advice.
"""

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"⚠️ Gemini API Error: {e}"