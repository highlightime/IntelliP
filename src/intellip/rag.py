from langchain_upstage import UpstageLayoutAnalysisLoader
from IPython.display import display, HTML
import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_upstage import ChatUpstage


def test():
    print('test!!')

def pdfload(file):
    # path_cur = os.path.dirname(os.path.abspath(__file__))
    path_file = file
    layzer = UpstageLayoutAnalysisLoader(
        path_file, use_ocr=True, output_type="html"
    )
    # For improved memory efficiency, consider using the lazy_load method to load documents page by page.
    docs = layzer.load()  # or layzer.lazy_load()

    return docs

def questionWithDocs(question, docs):
    display(HTML(docs[0].page_content[:1000]))
    
    llm = ChatUpstage()

    prompt_template = PromptTemplate.from_template(
        """
        Please provide most correct answer from the following context. 
        If the answer is not present in the context, please write "The information is not present in the context."
        ---
        Question: {question}
        ---
        Context: {Context}
        """
    )
    chain = prompt_template | llm | StrOutputParser()
    question_template = {"question": question, "Context": docs}

    return question_template