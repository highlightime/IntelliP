import warnings

warnings.filterwarnings("ignore")

import gradio as gr

from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage, HumanMessage
from embedding import retriever_from_docs, chroma_instance
from crawler import fetch_docs

import os
from dotenv import load_dotenv

import requests

from rag import pdfload

last_link = None
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
    You are an intelligent assistant designed to help answer questions based on the content of a specific link or file.
    If the information is not in the link or file, respond with "The information is not available in the link or file.  
    Below is either the path to the file or the URL to the webpage you need to reference for your answers. 
    Please use the content of the specified resource to respond accurately to the questions asked. 
    
    Your response should be within 5 sentences. 
    Additionally, include the location and the full sentence from which you derived the answer.

    LINK: <insert link here>
    PATH: <insert file path here>

    Please answer the following question based on the content of the specified resource:

    <insert your question here>

    Provide your answer below, including the location and the full sentence:

    Answer: <your answer>
    Location: <location in the document>
    Full Sentence: <full sentence from the document>

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
    if query.startswith("file://"):
        fname = query[7:]
    if not os.path.isfile(fname):
        raise ValueError(f"File {query} not found. Please provide a valid file path.")
        # return solar_pdf_search(fname)

    docs = pdfload(fname)
    # print(f"File downloaded at {query}")

    return docs

def tool_rag(question, history):
    import re
    global last_link
    parse_ftn = None
    link = last_link
    if "https://" in question and ".pdf" in question:
        link = re.findall(r"https://.*", question)[-1]
        parse_ftn = solar_pdf_search
    elif ".pdf" in question:
        path = [i for i in question.split(" ") if i.endswith(".pdf")][-1]
        link = "file://" + path
        parse_ftn = solar_pdf_load
    elif "https://" in question:
        link = re.findall(r"https://.*", question)[-1]
        parse_ftn = fetch_docs
    last_link = link
    if link is not None:
        if len(chroma_instance._collection.get(where={"domain": link}, include=[])["ids"]) == 0:
            docs = parse_ftn(link)
            retriever_from_docs(docs, link)
        retriever = chroma_instance.as_retriever(search_kwargs={"filter": {"domain": link}})
    
        chain = prompt_template | llm | StrOutputParser()
        context = retriever.invoke(question)
    else:
        context = ""
    print(context)
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

def main():
    with gr.Blocks() as demo:
        chatbot = gr.ChatInterface(
            chat,
            examples=[
                "What is o1js? https://docs.minaprotocol.com/",
                "What is virtualization? data/sample/pdf/document.pdf",
                "What is Round Robin scheduling policy? https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf"
            ],
            title="IntelliP Chatbot",
            description="Closed-source chatbot that can answer questions based on the content of a specific link or file.",
        )
        chatbot.chatbot.height = 600
    demo.launch()

if __name__ == "__main__":
    main()
