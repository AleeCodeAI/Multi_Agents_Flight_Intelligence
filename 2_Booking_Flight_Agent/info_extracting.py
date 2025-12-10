# =============================== IMPORTING LIBRARIES ===============================
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re

# =============================== LOADING ENVIRONMENT VARIABLES ===============================
load_dotenv(override=True)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")

# ============================== IMPORTING MODELS ==============================
claude_model = os.getenv("CLAUDE_MODEL")
gpt_model = os.getenv("GPT_MODEL")
gemini_model = os.getenv("GEMINI_MODEL")
deepseek_model = os.getenv("DEEPSEEK_MODEL")

# =============================== INITIALIZING OPENAI CLIENT ===============================

openrouter = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)

# ============================== MAKING A SAFE JSON FUNCTION ===============================

def safe_json_load(raw_text):
    if not raw_text or raw_text.strip() == "":
        # Instead of raising error, return empty dict
        return {}
    
    # Normalize text
    raw_text = raw_text.strip()
    raw_text = raw_text.replace("“", '"').replace("”", '"')
    
    # Remove triple backticks ```json ... ```
    raw_text = re.sub(r"```.*?```", "", raw_text, flags=re.DOTALL)
    
    # Also remove any markdown code blocks
    raw_text = re.sub(r'```(?:json)?\s*', '', raw_text)
    raw_text = re.sub(r'\s*```$', '', raw_text)
    
    # Find JSON object in text
    match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # If JSON is invalid, try to clean it more
            pass
    
    # Return empty dict as fallback instead of raising error
    return {
        "first_name": "", "last_name": "", "email": "", "phone_number": "",
        "passport_number": "", "date_of_birth": "", "nationality": "",
        "flight_number": "", "operating_airline": "", "from_city": "",
        "to_city": "", "departure_datetime": "", "arrival_datetime": "",
        "seat_number": "", "price_paid": ""
    }
# =============================== MAKING A KEY EXTRCATING FUNCTION ===============================

def extract_key_info(natural_language_input):

    # system prompt
    system_prompt = """
    You are an expert in extracting key values from natural language text.
    You will be given a natural language input and you are responsible for
    extracting the following key values:

    first_name,
    last_name,
    email,
    phone_number,
    passport_number,
    date_of_birth,
    nationality,
    flight_number,
    operating_airline,
    from_city,
    to_city,
    departure_datetime,
    arrival_datetime,
    seat_number,
    price_paid

    You must respond ONLY in JSON format with these exact key–value pairs.
    If a value is missing or not mentioned, return an empty string "".

    Here is an example format you MUST follow exactly:

    {
    "first_name": "Ali",
    "last_name": "Seena",
    "email": "ali@example.com",
    "phone_number": "+923001234567",
    "passport_number": "P9876543",
    "date_of_birth": "2008-05-10",
    "nationality": "Pakistan",
    "flight_number": "EK610",
    "operating_airline": "Emirates",
    "from_city": "Dubai",
    "to_city": "Lahore",
    "departure_datetime": "2025-12-11 09:45",
    "arrival_datetime": "2025-12-11 13:05",
    "seat_number": "17C",
    "price_paid": "520.00"
    }

    NOTE: 
    You must ALWAYS respond with a single valid JSON object only. 
    Do not add any explanations, notes, or extra text.
    Do not add "Here is the data" or any commentary.
    Do not use smart quotes (“ ”), only standard double quotes (").
    Return a valid JSON object that can be parsed directly with json.loads().

    AND IF ANY KEY IS MISSING, RETURN empty strings ""
    """
    response = openrouter.chat.completions.create(
        model = deepseek_model,
        messages= [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language_input}
        ]
    )
    data = response.choices[0].message.content
    return safe_json_load(data)

# ============================== TESTING ===============================

# query = input("> ")
# output = extract_key_info(query)
# print(output)
# 
# 