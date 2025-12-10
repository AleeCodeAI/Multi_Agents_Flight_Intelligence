# ------------------------ IMPORTING LIBRARIES ------------------------

import os
from dotenv import load_dotenv
from openai import OpenAI
import json 
from search_functions import flight_search_router
from IPython.display import display, Markdown

# ------------------------ LOADING ENV VARIABLES ------------------------

load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = "https://openrouter.ai/api/v1"

# gemini_api_key = os.getenv("GEMINI_API_KEY")
# gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

# ------------------------ DEFINING CLIENTS ----------------------------

openrouter = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)
#gemini = OpenAI(api_key=gemini_api_key, base_url=gemini_url)

# ------------------------ DEFINING MODELS ----------------------------
model_deepseek = os.getenv("DEEPSEEK_MODEL")
model_gemini = os.getenv("GEMINI_MODEL")

# ======================== MAKING THE QUERY GENERATOR ========================

# System Prompt for Query Generator:
system_prompt_query = """ 
You are a flight search query generator. Convert user queries into a valid JSON dictionary
matching the database fields below. Output ONLY the dictionary.

VALID FIELDS:
- flight_number
- airline
- from_city, to_city
- departure_datetime, arrival_datetime
- price_economy, price_business, price_first
- stops
- duration_minutes
- departure_airport, arrival_airport
- baggage_allowance
- meal_available
- wifi_available
- aircraft_type
- operating_days
- flight_status

RULES:
1. Use exact field names only.
2. If the user mentions ANY value that matches ANY field above, return a dictionary using
   ONLY those fields (single-field searches are allowed).
3. Do NOT require from_city or to_city unless the user explicitly includes them.
4. Cities and airlines must be Title Case.
5. Prices and durations must be numeric.
6. Dates must use “YYYY-MM-DD” (partial dates allowed: “2025-11”).
7. If nothing matches the schema, return {}.
8. No explanations—return only a JSON dictionary.

EXAMPLES:
"Emirates flights" → {"airline": "Emirates"}
"Flights to London under 400" → {"to_city": "London", "price_economy": 400}
"Direct wifi flights" → {"stops": 0, "wifi_available": "Yes"}

NOTE: RETURN ONLY THE DICTIONARY. NO ADDITIONAL TEXT, EXPLANATIONS, OR FORMATTING.
"""

# Defining the LLM for Query Generator:
def llm1(user_input):
    response = openrouter.chat.completions.create(
        model=model_deepseek,
        messages=[
            {"role": "system", "content": system_prompt_query},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# Making the Response Parser:
def parse_llm_response(llm_output: str, original_query: str) -> dict | str:
    """Convert LLM output or return clarification request"""
    try:
        cleaned_output = llm_output.strip()
        criteria_dict = json.loads(cleaned_output)
        return criteria_dict
    except (json.JSONDecodeError, TypeError) as e:
        error_msg = f"I couldn't process your request for '{original_query}'. "
        error_msg += "Please specify with more specific information"
        return error_msg
    
# Making the Search Query Generator:
def generate_search_query(user_input):
    llm_output = llm1(user_input)
    criteria = parse_llm_response(llm_output, user_input)
    return criteria

# ======================== MAKING THE RESPONSE GENERATOR ========================

# System Prompt for Response Generator:
system_prompt_main = """
You are a highly professional and friendly flight information assistant. Your goal is to provide users with clear, detailed, and 
easy-to-understand flight options.
Use the flight search results and search criteria provided to generate responses that include:

- Flight number, airline, and route
- Departure and arrival airports and times
- Duration and number of stops
- Aircraft type and flight status
- Prices for Economy, Business, and First class
- Amenities (baggage allowance, meals, WiFi)
- Operating days

Present the information in a natural, human-like tone that is helpful and approachable. 
If no flights match the user's criteria, politely inform them and, if possible, suggest alternatives or ways to refine their search. 
Always be professional, concise, and courteous.

Also, inform the users about the flight status, whther the flighst are concalled, delayed or on time.
"""

# Defining the LLM for Response Generator:
def response_generator(user_input, flight_data):
    # Create a more structured prompt for the LLM
    prompt = f"""
USER QUERY: {user_input}

FLIGHT DATA:
{flight_data}

ANALYZE the flight data above and respond to the user query. Focus on:
1. Which flights match the user's request
2. Key details about matching flights
3. If no flights match, state this clearly
"""
    
    response = openrouter.chat.completions.create(
        model=model_deepseek,
        messages=[
            {"role": "system", "content": system_prompt_main},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

# ======================== FINAL FLIGHT INFO FUNCTION ========================

def fetch_flight_info(user_input):
    criteria = generate_search_query(user_input)
    if isinstance(criteria, dict):
        flight_data = flight_search_router(criteria)
    else:
        flight_data = None   # <--- FIX
    response = response_generator(user_input, flight_data)
    return response

# query = input("Enter your flight query: ")
# result = fetch_flight_info(query)
# print(result)
