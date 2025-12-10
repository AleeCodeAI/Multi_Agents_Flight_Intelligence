# ============================= IMPORTING LIBRARIES ==============================
import os 
from dotenv import load_dotenv 
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from extract_flight_info import fetch_flight_info
from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType

# =========================== LOADING ENVIRONMENT VARIABLES =====================
load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL")
deepseek_model = os.getenv("DEEPSEEK_MODEL")

# ========================== MAKING THE CLIENTS =================================
deepseek = OpenAI(api_key=openrouter_api_key, base_url=openrouter_url)

# ============================= MAKING GEMINI CHAT ===============================

openrouter_chat = ChatOpenAI(model=deepseek_model,
                             api_key=openrouter_api_key,
                             base_url=openrouter_url,
                             max_tokens=1000,
                             temperature=0)

# ============================ MAKING MEMORY =====================================
chat_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# =============================== SYSTEM PROMPT ===============================
system_prompt = SystemMessagePromptTemplate.from_template(
""" 
You are a friendly and reliable flight-information assistant.

**Communication Style:**
- Always start conversations with: "Hello! How can I assist you with your flight today?"
- Be warm, clear, and professional - not robotic or overly formal
- Keep responses concise and user-focused
- Use natural, conversational language

**Tool Usage Rules:**
- **Only use the flight information tool for specific flight queries** (flight numbers, schedules, prices, status, routes)
- **Never use tools for greetings, small talk, or general questions**
- For flight queries, extract key details and use the tool precisely

**Response Guidelines:**
- Process tool output before replying - never show raw data
- Provide only requested information unless asked for full details
- Present times/dates clearly (e.g., "7:35 PM — Monday, Feb 23")
- If no flights match: "I couldn't find that flight. Could you confirm the details?"

**Goal:** Deliver accurate flight information with excellent, natural communication.
"""
)
# ============================== HUMAN PROMPT ====================================
# FIX: Use from_template method instead of direct instantiation
human_prompt = HumanMessagePromptTemplate.from_template("{input}")

# ============================= CHAT PROMPT =====================================
# FIX: Pass messages as a list to ChatPromptTemplate
chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    MessagesPlaceholder(variable_name="chat_history"),
    human_prompt
])

# ============================ MAKING THE TOOL ==================================
flight_info_tool = Tool(
    name="flight_info_tool",
    func=fetch_flight_info,
    description="""
    Use this tool to provide detailed flight information based on user queries. 
    It can return details such as flight number, airline, departure and arrival cities, 
    departure and arrival times, ticket prices (economy, business, first class), 
    stops, and flight duration. 
    Only use this tool when the user asks about specific flights or requests flight schedules, 
    pricing, or other travel-related details.
    """
)

tools = [flight_info_tool]

# =========================== MAKING TOOL CALLING AGENT ===========================

agent_executor = initialize_agent(
    tools=tools,
    llm=openrouter_chat,
    agent="chat-conversational-react-description",
    memory=chat_memory,
    verbose=True,
    agent_kwargs={"prompt": chat_prompt}  
)

# ========================== CALLING THE AGENT ==============================
def retrieval_agent(query):
    response = agent_executor.run(input=query)
    return response["output"]

# ========================== TESING ========================================

# gr.ChatInterface(fn=retrieval_agent, 
                #  title="Retrieval Agent").launch(inbrowser=True)