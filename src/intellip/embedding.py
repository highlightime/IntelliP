from langchain_upstage import UpstageEmbeddings
from langchain.docstore.document import Document
try:
    import sqlite3
except ImportError:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_chroma import Chroma
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

from dotenv import load_dotenv
load_dotenv()

chunk_size = 1000
embeddings_model = UpstageEmbeddings(model="solar-embedding-1-large")
text_splitter = RecursiveCharacterTextSplitter.from_language(
    chunk_size=chunk_size, chunk_overlap=int(chunk_size * 0.1), language=Language.HTML
)
persist_directory = "./chroma_db"
chroma_instance = Chroma(embedding_function=embeddings_model, persist_directory=persist_directory)

def retriever_from_docs(docs, domain):
    for i in range(len(docs)):
        doc = docs[i]
        if isinstance(doc, dict):
            doc['metadata']['domain'] = domain
            docs[i] = Document(**doc)
        else:
            docs[i].metadata['domain'] = domain
        
    splits = text_splitter.split_documents(docs)
    vectorstore = chroma_instance.from_documents(
        documents=splits,
        embedding=embeddings_model,
        persist_directory=persist_directory,
    )
    vectorstore._collection.get()
