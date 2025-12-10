# SkyVista Master Agent

## Overview
SkyVista is a multi-agent AI system designed to handle complex workflows related to flight information, booking, and customer assistance. Users interact with a single interface while the system intelligently routes requests to the most appropriate specialized agent. The project demonstrates a **hybrid AI system** that combines intelligent agents, databases, AI models, and automation workflows.

## Agents
**1. Retrieval Agent** – Accesses a comprehensive database of all available flights. Users can query flights based on airline, flight ID, or other criteria. Uses **SQLite3** for relational data storage.  
**2. Booking Agent** – Handles the complete flight booking workflow. It collects customer data, provides flight information, summarizes booking details, saves them to the database, and sends automated confirmation emails via **n8n** automation.  
**3. Help Agent** – A RAG-based agent that provides information about company policies, rules, and general customer assistance.  

## Technologies & Tools
- **Languages & Frameworks**: Python, Streamlit, Gradio, LangChain  
- **AI Models & APIs**: Large Language Models (LLMs), OpenRouter API, Gemini API  
- **Databases**: Chroma (vector database), SQLite3 (relational database)  
- **Core Techniques**: RAG (Retrieval-Augmented Generation)  
- **Automation & Integration**: n8n workflow automation  
- **Embeddings**: Hugging Face Embedding Model  

## Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Create a `.env` file with the following variables:
    ```
    GEMINI_API_KEY=<your_key>
    OPENROUTER_API_KEY=<your_key>
    GEMINI_URL=<url>
    OPENROUTER_URL=<url>
    ```

## Usage
Start the Streamlit application:
```bash
streamlit run final_appy.py
```
Interact with the interface to communicate with the **master agent**, which will automatically route your requests to the appropriate sub-agent (retrieval, booking, or help).

## Features
- **Intelligent Routing**: Multi-agent system that directs user queries to the most suitable specialized agent.  
- **Flight Search**: Retrieve and search flight information via direct database queries.  
- **Automated Booking**: Complete booking workflow with data collection, summarization, and confirmation.  
- **Customer Support**: Help agent for instant access to company policy and rule information.  
- **Experimentation**: Each agent folder includes Jupyter notebooks for prototyping and testing.  
- **Hybrid Integration**: Combines AI models, multiple database systems, and external automation workflows.  

## Project Structure
The repository is organized into agent-specific directories, each containing:  
- Core Python files implementing the agent's functionality.  
- Jupyter notebooks for experimentation and testing.  
A `requirements.txt` file lists all necessary packages for the local setup.  
