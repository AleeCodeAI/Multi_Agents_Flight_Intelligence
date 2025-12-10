import os
import sys
from dotenv import load_dotenv
from langchain.schema import HumanMessage

# =============================
# LOAD ENVIRONMENT VARIABLES
# =============================
load_dotenv(override=True)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# =============================
# FIX IMPORT PATHS
# =============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "1_Flight_Search_Agent"))
sys.path.append(os.path.join(BASE_DIR, "2_Booking_Flight_Agent"))
sys.path.append(os.path.join(BASE_DIR, "3_Help_Flight_Agent"))

# =============================
# IMPORT AGENTS
# =============================
from retrieval_agent import retrieval_agent
from booking_agent import booking_agent
from help_agent import help_agent

# =============================
# USE OPENROUTER LLM
# =============================
from langchain_community.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=openrouter_api_key,
    temperature=0,
    base_url="https://openrouter.ai/api/v1"
)

# =============================
# SIMPLE ROUTER FUNCTION
# =============================
def route_message(user_input: str) -> str:
    """
    Uses LLM to pick the best agent: RETRIEVAL, BOOKING, or HELP.
    """
    print("\n[DEBUG] Routing user message through LLM...")  # Debug

    prompt = f"""
    You are SkyVista's master router.

    User message: "{user_input}"

    Decide which agent is best to handle this query:
    - RETRIEVAL_AGENT: searching flights, availability, fares.
    - BOOKING_AGENT: booking tickets, entering personal info, confirmation.
    - HELP_AGENT: company policies, general questions.

    Output ONLY the agent name: RETRIEVAL_AGENT, BOOKING_AGENT, or HELP_AGENT
    """

    # Pass a HumanMessage instead of a dict
    response = llm.generate([ [HumanMessage(content=prompt)] ])
    agent_choice = response.generations[0][0].text.strip().upper()

    print(f"[DEBUG] LLM suggested agent: {agent_choice}")  # Debug
    return agent_choice

# =============================
# MASTER AGENT FUNCTION
# =============================
def master_agent(user_input: str):
    print(f"\n[DEBUG] Received user input: {user_input}")  # Debug

    agent = route_message(user_input)

    if agent == "RETRIEVAL_AGENT":
        print("[DEBUG] Calling Retrieval Agent...")  # Debug
        return retrieval_agent(user_input)
    elif agent == "BOOKING_AGENT":
        print("[DEBUG] Calling Booking Agent...")  # Debug
        return booking_agent(user_input)
    elif agent == "HELP_AGENT":
        print("[DEBUG] Calling Help Agent...")  # Debug
        return help_agent(user_input)

    print("[DEBUG] No suitable agent found.")  # Debug
    return "Sorry, I could not understand the request."

# =============================
# RUN LOOP
# =============================
if __name__ == "__main__":
    print("SkyVista Master Agent Ready.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting SkyVista Master Agent.")
            break

        response = master_agent(user_input)
        print("SkyVista:", response, "\n")
