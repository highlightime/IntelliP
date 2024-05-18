import warnings

warnings.filterwarnings("ignore")

import gradio as gr

from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage, HumanMessage
from langchain_core.tools import tool
from embedding import retriever_from_docs
from crawler import fetch_docs

import os
from dotenv import load_dotenv

import requests

from rag import pdfload, questionWithDocs

retrievers = {}

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

def solar_pdf_search(query: str) -> str:
    """Query for pdf link. 
    Link will be presented after the keyword PDF LINK:
    The link will be in double quotes and starts with https:// and ends with .pdf
    """
    # query = "https://pages.cs.wisc.edu/~remzi/OSTEP/dialogue-virtualization.pdf"

    def get_pdf_from_url(url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
        response = requests.get(url=url, headers=headers, timeout=120)
        # Save the response content to a file
        out_path = f"data/sample/pdf/{url.split('/')[-1]}.pdf"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as file:
            file.write(response.content)
        return out_path

    document = get_pdf_from_url(query)
    print(f"File downloaded at {document} from link {query}")
    docs = pdfload(document)

    return docs

def solar_pdf_load(query: str) -> str:
    """Query for pdf file. 
    The file's path will be presented after the keyword PDF PATH:
    The path will end with .pdf
    """
    # query = "data/sample/pdf/document.pdf"

    if not os.path.isfile(query):
        print(f"File not found search {query} from web")
        return solar_pdf_search(query)

    docs = pdfload(query)
    print(f"File downloaded at {query}")

    return docs

def query_with_link(link, question):
    if link not in retrievers:
        docs = fetch_docs(link)
        retriever = retriever_from_docs(docs, link)
        retrievers[link] = retriever
    retriever = retrievers[link]
    return questionWithDocs(question, retriever.invoke(question))

tools = [solar_pdf_search, solar_pdf_load]
llm_with_tools = llm.bind_tools(tools)

def tool_rag(question, history):
    import re

    context = ""
    if "https://" in question and ".pdf" in question:
        url_link = re.findall(r"https://.*", question)
        context += str(solar_pdf_search(url_link))
    elif ".pdf" in question:
        file_path = [i for i in question.split(" ") if i.endswith(".pdf")][-1]
        context += str(solar_pdf_load(file_path))

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
