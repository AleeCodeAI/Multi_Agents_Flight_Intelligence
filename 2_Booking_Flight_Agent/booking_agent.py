# =============================== IMPORTING LIBRARIES ===============================
import os
from dotenv import load_dotenv
from openai import OpenAI
from database_creation_data_query import get_user_info, insert_customer_booking
from email_confirmation_sender import send_to_n8n
from info_extracting import extract_key_info
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.agents import Tool, create_tool_calling_agent, AgentExecutor 
from IPython.display import display, Markdown
import gradio as gr
import sys
sys.path.append(r"D:\LangChain Projects\Multi_Agents_Flight_Intelligence\1_Flight_Search_Agent")
from extract_flight_info import fetch_flight_info

# =============================== LOADING ENVIRONMENT VARIABLES ===============================
load_dotenv(override=True)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ============================== IMPORTING MODELS ==============================
claude_model = os.getenv("CLAUDE_MODEL")
gpt_model = os.getenv("GPT_MODEL")
gemini_model = os.getenv("GEMINI_MODEL")
deepseek_model = os.getenv("DEEPSEEK_MODEL")

# =============================== MAKING A CLIENT ===============================
openrouter = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)

# ============================== MAKING A CHAT FOR MEMORY ==============================

gemini_chat = ChatGoogleGenerativeAI(
    model=gemini_model,  
    temperature=0,
    max_output_tokens=2048,  
    google_api_key=gemini_api_key,
    convert_system_message_to_human=True  
)

openrouter_chat = ChatOpenAI(
    model="openai/gpt-oss-120b",  
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
    temperature=0
)

# ============================ MEMORY ==========================================
chat_memory = ConversationBufferMemory(    
    memory_key="chat_history",
    return_messages=True
)

# ===========================================================================================
                         # BUILDING TOOL 1: ask_customer_data_tool 
# ===========================================================================================

# ============================ SYSTEM PROMPT ===================================
system_prompt_tool_1 = """
You are a booking flight assistant. Your job is to collect flight booking details step by step.

CRITICAL INSTRUCTIONS:
1. Ask only one detail at a time.
2. Ask only for missing fields.
3. Do NOT repeat previously collected information.
4. Keep responses concise and natural.
5. When all fields are collected, give a final confirmation message.

Example final confirmation:
"So, to confirm you're Ali Seena Ghulami, your email is aleeexample@gmail.com, phone number 76340926431, passport number ygf234, born on 
October 23, 2007 in Pakistan, making you a Pakistani citizen. Is this correct?"
THE CONFIRMATION PART IS MUST AND SHALL NOT BE NEGLECTED
"""

# ============================ HUMAN PROMPT ====================================
human_prompt = HumanMessagePromptTemplate.from_template("User message: {user_input}")

# =============================== BOOKING ASSISTANT ===============================
def ask_customer_data_func(user_input: str) -> str:
    # ----- 3. Final combined chat prompt -----
    chat_prompt = ChatPromptTemplate.from_messages([
        system_prompt_tool_1,
        MessagesPlaceholder(variable_name="chat_history"),
        human_prompt
    ])

    # ----- 4. Load memory with error handling -----
    try:
        memory_variables = chat_memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        
        formatted_messages = chat_prompt.format_messages(
            user_input=user_input,
            chat_history=chat_history
        )
    except Exception as e:
        print(f"Memory error: {e}")
        # Fallback without memory
        formatted_messages = chat_prompt.format_messages(
            user_input=user_input,
            chat_history=[]
        )

    # ----- 5. Convert messages with better error handling -----
    openrouter_messages = []
    for m in formatted_messages:
        try:
            if isinstance(m, HumanMessage):
                openrouter_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                openrouter_messages.append({"role": "assistant", "content": m.content})
            elif isinstance(m, SystemMessage):
                openrouter_messages.append({"role": "system", "content": m.content})
            else:
                openrouter_messages.append({"role": "user", "content": str(m.content)})
        except Exception as e:
            print(f"Message conversion error: {e}")
            continue

    # ----- 6. API Call with robust error handling -----
    try:
        response = openrouter.chat.completions.create(
            model=gpt_model,
            messages=openrouter_messages,
            temperature=0.7,
            timeout=30
        )
        result = response.choices[0].message.content
        
        if not result or result.strip() == "":
            result = "I apologize, but I didn't get a response. Could you please repeat that?"
            
    except Exception as e:
        print(f"API Error: {e}")
        result = "I'm having trouble processing your request. Could you please try again."

    # ----- 7. Save to memory with error handling -----
    try:
        chat_memory.save_context(
            {"input": user_input},
            {"output": result}
        )
    except Exception as e:
        print(f"Memory save error: {e}")

    return result

# ============================ MAKING TOOL ============================================
ask_customer_data_tool = Tool(
    name="ask_customer_data_tool",
    func=ask_customer_data_func,
    description="""Use this tool to collect general customer data for flight booking:
first name, last name, email, phone number, passport number, date of birth, nationality.
It asks one field at a time and confirms at the end."""
)

# ===========================================================================================
                         # BUILDING TOOL 2: flight_data_retrieval_tool 
# ===========================================================================================

system_prompt_2 = """ 
You are a flight data retrieval assistant. Your main job is take the user query and the relevant flight information to draft a response that 
is clear and concise. 
example:
user: what are the flights from Karachi to London
flight data:
1. Flight XY102 by Pakistan International Airlines
Departure: Karachi (Jinnah Intl) at 06:17 on 2025-11-20
Arrival: London (Heathrow) at 13:23 on 2025-11-20
Duration: 7h 6m with 1 stop
Aircraft: Airbus A320
Status: On-time
Prices: Economy $509, Business $665, First $929
Amenities: Baggage allowance 20kg+6kg carry-on, Vegetarian meal included, No WiFi
Operating Days: Monday, Tuesday, Wednesday, Sunday

Assistant:
For flights directly from Karachi (Jinnah Intl, KHI) to London (Heathrow, LHR), I found one flight option available:

1. Flight XY102 by Pakistan International Airlines
Departure: Karachi (Jinnah Intl) at 06:17 on 2025-11-20
Arrival: London (Heathrow) at 13:23 on 2025-11-20
Duration: 7h 6m with 1 stop
Aircraft: Airbus A320
Status: On-time
Prices: Economy $509, Business $665, First $929
Amenities: Baggage allowance 20kg+6kg carry-on, Vegetarian meal included, No WiFi
Operating Days: Monday, Tuesday, Wednesday, Sunday
The other flights listed involve stops in cities like Istanbul, Dubai, Doha, or New York before reaching London, or flights starting from 
other cities. Some of these connecting flights are delayed or cancelled.

If you prefer a direct flight, the above option is available. Otherwise, I can help you explore flights with connections through Istanbul, 
Dubai, or Doha.

Would you like additional details or assistance with booking?

NOTE:
when the flight is agreed on by the customer, you shall give a confirmation message like. 
So your agreed flight is:
1. Flight XY102 by Pakistan International Airlines
Departure: Karachi (Jinnah Intl) at 06:17 on 2025-11-20
Arrival: London (Heathrow) at 13:23 on 2025-11-20
Duration: 7h 6m with 1 stop
Aircraft: Airbus A320
Status: On-time
Prices: Economy $509, Business $665, First $929
Amenities: Baggage allowance 20kg+6kg carry-on, Vegetarian meal included, No WiFi
Operating Days: Monday, Tuesday, Wednesday, Sunday
"""

# =================================== MAKIG THE TOOL FUNCTION ========================================

def flight_data_retrieval_func(user_input):
    memory_variables = chat_memory.load_memory_variables({})
    chat_history = memory_variables.get("chat_history", [])
    flight_data = fetch_flight_info(user_input)
    user_prompt_2 = f''' 
                    Previous Conversations history: 
                    {chat_history}
                    
                    user message: {user_input},

                    flight data:
                    {flight_data}
                    '''
    result = openrouter.chat.completions.create(
        model = gpt_model,
        messages = [
            {"role": "system", "content": system_prompt_2},
            {"role": "user", "content": user_prompt_2}
        ]
    )
    assistant_reply = result.choices[0].message.content

    chat_memory.save_context(
    {"input": user_input},
    {"output": assistant_reply})

    return assistant_reply

# ====================================== MAKING IT A TOOL ==========================================

flight_data_retrieval_tool = Tool(name="flight_data_retrieval_tool",
                                  func= flight_data_retrieval_func,
                                  description = """
                                Use this tool only after the first tool, 'ask_customer_details_tool', has successfully collected all required personal details. 
                                This tool is responsible for providing and discussing flight information with the user. 
                                It should be used when the user is ready to receive flight options, compare flights, and make a selection.
""")

# ===========================================================================================
                         # BUILDING TOOL 3: summarizing_tool 
# ===========================================================================================

# =============================== MAKING THE TOOL FUNCTION ==================================

def summarizing_func(input_str: str ) -> str:
    """
    Summarizes the chat history to extract booking information.
    
    Args:
        input_str: The input string (not used but required by LangChain)
    
    Returns:
        str: Summary of booking information
    """
    # Load memory
    memory_variables = chat_memory.load_memory_variables({})
    chat_history = memory_variables.get("chat_history", [])

    # Convert messages to readable text
    chat_text = "\n".join([f"{m.type}: {m.content}" for m in chat_history])

    # Prepare prompt
    prompt = f"""
    You are an intelligent assistant that extracts key booking information from a flight agent chat.


    Summarize the booking as in this example:
    "He is Ali Seena Ghulami, his email is aleeexample@gmail.com, phone number 76340926431, passport number ygf234, 
    born on October 23, 2007 in Pakistan, making him a Pakistani citizen. The agreed flight is - Flight Number: XY166 operated 
    by Emirates, going from Karacgi to London, Departure time is November 25, 2025, at 10:50, Arrival is November 25, 2025, at 12:40, Duration
is 1 hour 50 
    minutes (non-stop), Aircraft is Boeing 777, Flight Status is On-time, Prices agreed on Business $838, Amenities is 31 kg 
    checked baggage + 6 kg cabin luggage allowance, no meals or WiFi included, Operating on Monday, Wednesday, Friday, Saturday"

    as seen in the example, you might not be given the seat number, you are free to put one by yourself randomly! but MUST PUT ONE
    Here is the chat history:
    {chat_text}

    You:
    """

    # Call the LLM
    response = openrouter_chat.invoke(prompt)
    result = response.content

    # Process result
    key_info = extract_key_info(result)
    print(key_info)
    insert_customer_booking(
        first_name=key_info.get("first_name", ""),
        last_name=key_info.get("last_name", ""),
        email=key_info.get("email", ""),
        phone_number=key_info.get("phone_number", ""),
        passport_number=key_info.get("passport_number", ""),
        date_of_birth=key_info.get("date_of_birth", ""),
        nationality=key_info.get("nationality", ""),
        flight_number=key_info.get("flight_number", ""),
        operating_airline=key_info.get("operating_airline", ""),
        from_city=key_info.get("from_city", ""),
        to_city=key_info.get("to_city", ""),
        departure_datetime=key_info.get("departure_datetime", ""),
        arrival_datetime=key_info.get("arrival_datetime", ""),
        seat_number=key_info.get("seat_number", ""),
        price_paid=key_info.get("price_paid", "")
    )
    send_to_n8n(key_info)
    return result

# ============================== MAKING IT A TOOL =================================

summarizing_tool = Tool(name="summarizing_tool",
                        func=summarizing_func,
                        description=""" 
                        This tool is designed to generate the final summary of the entire flight-booking process.
                        Use this tool only after:
                        Tool 1 — ask_customer_data_tool has collected all customer details
                        Tool 2 — flight_data_retrieval_tool has retrieved all flight information
                        Once both steps are completed, use this tool to produce a clear, final booking summary.
                        """)

# ===========================================================================================
                         # BUILDING THE AGENT
# ===========================================================================================

tools = [ask_customer_data_tool, flight_data_retrieval_tool, summarizing_tool]

system_prompt_agent = SystemMessagePromptTemplate.from_template(
"""
You are Booking Flight Assistant, a friendly and reliable flight booking agent.

Your workflow is strictly sequential and must follow these rules:

1. **Personal Details Collection (Tool 1 – personal_data_tool)**  
   - Before doing anything else, call the `personal_data_tool` to collect all required user information:  
     - Full name  
     - Contact information (phone/email)  
     - Passport or ID  
     - Date of birth  
   - Do NOT continue until all personal details are fully collected and confirmed.

2. **Flight Information Retrieval (Tool 2 – flight_info_tool)**  
   - After personal details are complete, call the `flight_info_tool` to retrieve flight options.  
   - Present processed results including:  
     - Flight numbers  
     - Departure/arrival cities and times  
     - Airline  
     - Duration  
     - Price  
   - Only use Tool 2 after Tool 1 has finished successfully.

3. **Final Booking Summary (Tool 3 – booking_summary_tool)**  
   - After the user has selected a flight and all required information is confirmed, call `booking_summary_tool`.  
   - This tool generates the final summary of the entire booking process, including:  
     - Personal information  
     - Selected flight details  
     - Total price  
     - Any confirmations or final notes  
   - Use Tool 3 ONLY after Tool 1 and Tool 2 have both been completed.

4. **General Rules**  
   - Never skip steps or mix tools.  
   - Always speak in clear, friendly, natural language.  
   - Do not show raw tool output; interpret it and give a polished response.  
   - Ask clarifying questions whenever any detail is missing.  
   - Guide the user step-by-step through the entire process from personal data → flight options → final summary.

**Goal:**  
Help the user complete their booking smoothly by strictly following the sequence:  
**Tool 1 → Tool 2 → Tool 3**, without skipping or mixing steps.

IMPOTANT:
Handle the normal queries like greetings or others naturally and well
"""
)

human_prompt_agent = HumanMessagePromptTemplate.from_template(""" User Message: {user_input}""")

chat_prompt_agent = ChatPromptTemplate.from_messages([
    system_prompt_agent,
    MessagesPlaceholder(variable_name="chat_history"),
    human_prompt_agent,
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(llm=gemini_chat,
                                  tools=tools,
                                  prompt=chat_prompt_agent)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=chat_memory,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)

def booking_agent(query, history): # DEFINE A HISTORY PARAMETER WHEN USING GRADIO
    response = agent_executor.invoke({"user_input": query})
    return response["output"]

# ===========================================================================================
                         # TESTING
# ===========================================================================================

# print("Welcome to AeroAssist! Type 'exit' to quit.\n")
# 
# while True:
    
    # user_query = input("You: ")
    # 

    # if user_query.lower() in ["exit", "quit"]:
        # print("Goodbye! Have a safe journey ✈️")
        # break
    # 
    # response = agent_executor.invoke({"user_input": user_query})
    # 

    # print(f"AeroAssist: {response['output']}\n")

# ===========================================================================================
                         # A DEMO INTERFACE
# ===========================================================================================
gr.ChatInterface(fn=booking_agent, 
                 title="Flight Assistant").launch(inbrowser=True)




