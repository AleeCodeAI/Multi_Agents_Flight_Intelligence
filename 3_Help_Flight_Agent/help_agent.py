import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool
import gradio as gr
from answer import answer_question
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
deepseek_model = os.getenv("DEEPSEEK_MODEL")

openrouter_chat = ChatOpenAI(model=deepseek_model,
                             api_key=openrouter_api_key,
                             max_tokens=1000,
                             temperature=0,
                             base_url="https://openrouter.ai/api/v1")

chat_memory = ConversationBufferMemory(memory_key="chat_history",
                                       return_messages=True)

retrieval_tool = Tool(
    name="retrieval_tool",
    func=answer_question,
    description="""
    This tool answers any question related to the flight company SkyVista Airlines using a Retrieval-Augmented Generation (RAG) approach. 
    It retrieves relevant documents from the knowledge base, combines them with conversation history if provided, 
    and generates a context-aware answer. The tool returns both the generated answer and the source chunks used for reference.
    """
)


system_prompt = SystemMessagePromptTemplate.from_template("""
You are a helpful and accurate assistant for SkyVista, a flight company. 
Your task is to answer any questions about SkyVista using the provided retrieval tool called `retrieval_tool`. 

Rules for answering questions:

1. Always use information retrieved from the `retrieval_tool` to answer questions.
2. Do not invent facts about SkyVista. If the answer is not in the retrieved documents, politely say that the information is not available.
3. Keep answers clear, concise, and relevant to the question.
4. Consider conversation history to provide context-aware responses when available.
5. Provide useful details like flight schedules, policies, services, or other official company info only if confirmed by the documents.

Remember, your primary source of truth is the `retrieval_tool` that fetches chunks from the SkyVista knowledge base.
""")

tools = [retrieval_tool]

chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{user_input}")
])

agent_executor = initialize_agent(
    tools=tools,
    llm=openrouter_chat,
    agent="chat-conversational-react-description",
    memory=chat_memory,
    verbose=True,
    agent_kwargs={"prompt": chat_prompt}  
)

def help_agent(query): # WHEN USING GRADIO DEFINE A HISTORY PARAMETER
    response = agent_executor.run(user_input=query)
    return response

# gr.ChatInterface(fn=help_agent, 
                #  title="Help Agent").launch(inbrowser=True)