import warnings

warnings.filterwarnings("ignore")

import gradio as gr

from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage, HumanMessage
from langchain_core.tools import tool

import os
from dotenv import load_dotenv

import requests

from rag import pdfload, questionWithDocs

load_dotenv()

UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

llm = ChatUpstage(streaming=True)

# More general chat
chat_with_history_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
    ]
)

prompt_template = PromptTemplate.from_template(
    """
    Please provide answer for question from the following context. 
    ---
    Question: {question}
    ---
    Context: {context}
    """
)
chain = chat_with_history_prompt | llm | StrOutputParser()

solar_summary = """
SOLAR 10.7B: Scaling Large Language Models with Simple yet Effective Depth Up-Scaling

We introduce SOLAR 10.7B, a large language model (LLM) with 10.7 billion parameters, 
demonstrating superior performance in various natural language processing (NLP) tasks. 
Inspired by recent efforts to efficiently up-scale LLMs, 
we present a method for scaling LLMs called depth up-scaling (DUS), 
which encompasses depthwise scaling and continued pretraining.
In contrast to other LLM up-scaling methods that use mixture-of-experts, 
DUS does not require complex changes to train and inference efficiently. 
We show experimentally that DUS is simple yet effective 
in scaling up high-performance LLMs from small ones. 
Building on the DUS model, we additionally present SOLAR 10.7B-Instruct, 
a variant fine-tuned for instruction-following capabilities, 
surpassing Mixtral-8x7B-Instruct. 
SOLAR 10.7B is publicly available under the Apache 2.0 license, 
promoting broad access and application in the LLM field.
"""

@tool
def solar_paper_search(query: str) -> str:
    """Query for research paper about solarllm, dus, llm and general AI.
    If the query is about DUS, Upstage, AI related topics, use this.
    """
    return solar_summary

@tool
def solar_pdf_search(query: str) -> str:
    """Query for pdf file link. PDF LINK:
    """
    print("Read sample file")
    link = "https://pages.cs.wisc.edu/~remzi/OSTEP/dialogue-virtualization.pdf"

    def get_pdf_from_url(url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
        response = requests.get(url=url, headers=headers, timeout=120)
        # Save the response content to a file
        with open('data/sample/pdf/document.pdf', 'wb') as file:
            file.write(response.content)
        return 'document.pdf'

    document = get_pdf_from_url(link)
    print(f"File downloaded at {document} from link {link}")
    print(os.path.isfile(document))
    docs = pdfload(document)

    return docs

@tool
def solar_pdf_load(query: str) -> str:
    """Query for pdf file. PDF PATH:
    """
    print("Read sample file")
    path = "data/sample/pdf/document.pdf"
    print(f"File downloaded at {path}")
    print(os.path.isfile(path))

    docs = pdfload(path)

    return docs

@tool
def internet_search(query: str) -> str:
    """This is for query for internet search engine like Google.
    Query for general topics.
    """
    return "Link not found"

@tool
def get_news(topic: str) -> str:
    """Get latest news about a topic.
    If users are more like recent news, use this.
    """
    # https://newsapi.org/v2/everything?q=tesla&from=2024-04-01&sortBy=publishedAt&apiKey=API_KEY
    # change this to request news from a real API
    news_url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={os.environ['NEWS_API_KEY']}"
    respnse = requests.get(news_url)
    return respnse.json()

def call_tool_func(tool_call):
    tool_name = tool_call["name"].lower()
    if tool_name not in globals():
        print("Tool not found", tool_name)
        return None
    selected_tool = globals()[tool_name]
    return selected_tool.invoke(tool_call["args"])

tools = [solar_paper_search, internet_search, get_news, solar_pdf_search, solar_pdf_load]
llm_with_tools = llm.bind_tools(tools)

def tool_rag(question, history):
    for _ in range(3): # try 3 times
        tool_calls = llm_with_tools.invoke(question).tool_calls
        if tool_calls:
            break

    if not tool_calls:
        return "I'm sorry, I don't have an answer for that."
    
    print(tool_calls)
    context = ""
    for tool_call in tool_calls:
        context += str(call_tool_func(tool_call))

    chain = prompt_template | llm | StrOutputParser()
    print({"context": context, "question": question})

    return chain.invoke({"context": context, "question": question, "history": history})

def chat(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    # return chain.invoke({"message": message, "history": history_langchain_format})
    return tool_rag(message, history_langchain_format)

# def chat(message, history):
#     history_langchain_format = []
#     for human, ai in history:
#         history_langchain_format.append(HumanMessage(content=human))
#         history_langchain_format.append(AIMessage(content=ai))

#     generator = chain.stream({"message": message, "history": history_langchain_format})

#     assistant = ""
#     for gen in generator:
#         assistant += gen
#         yield assistant

with gr.Blocks() as demo:
    chatbot = gr.ChatInterface(
        chat,
        examples=[
            "How to eat healthy?",
            "Best Places in Korea",
            "How to make a chatbot?",
        ],
        title="Solar Chatbot",
        description="Upstage Solar Chatbot",
    )
    chatbot.chatbot.height = 300

if __name__ == "__main__":
    demo.launch()
