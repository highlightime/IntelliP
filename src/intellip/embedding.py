from langchain_upstage import UpstageEmbeddings
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from urllib.parse import urlparse
from secrets import token_urlsafe

from dotenv import load_dotenv
load_dotenv()

chunk_size = 200
embeddings_model = UpstageEmbeddings(model="solar-embedding-1-large")
text_splitter = RecursiveCharacterTextSplitter.from_language(
    chunk_size=chunk_size, chunk_overlap=int(chunk_size * 0.25), language=Language.HTML
)

def retriever_from_docs(docs, domain):
    chroma_instance = Chroma()
    docs = [Document(**doc) for doc in docs]
    splits = text_splitter.split_documents(docs)
    vectorstore = chroma_instance.from_documents(
        documents=splits,
        embedding=embeddings_model,
        collection_name=token_urlsafe(8),
    )
    return vectorstore.as_retriever(search_kwargs={"filter": {"domain": domain}})
